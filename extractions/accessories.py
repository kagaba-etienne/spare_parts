from bs4 import BeautifulSoup
from app.db import Session
from app.db.models import Accessory, Car, ASubcategory, ACategory, Trim, TrimCar, TrimEngineAndCar, Engine
import requests


def find_or_create(mod, obj, sess):
    res = sess.query(mod).filter_by(**obj).first()

    if not res:
        res = mod(**obj)
        sess.add(res)
        sess.commit()
        return True, res

    return False, res


session = Session()
base_url = 'https://www.oemgenuineparts.com'


def select_text(sp, slct):
    try:
        new_sp = sp.select(slct)[0].text
        return new_sp
    except IndexError:
        return ""


def get_part(link, name, sub_category):
    r = requests.get(link)

    if r.status_code < 400:
        part_soup = BeautifulSoup(r.content, 'html.parser')
        details_module = part_soup.select('div.product-details-module')

        try:
            images = part_soup.select('div.product-images-module ul.secondary-images')[0]
            images = [image.get('src') for image in images.select('img')]
        except IndexError:
            images = []

        try:
            other_image = part_soup.select('div.product-images-module div.main-image a img')[0].get('src')
        except IndexError:
            other_image = ''

        images.append(other_image)

        try:
            details = details_module[0]
            part_num = select_text(details, 'li.part_number span.list-value').strip()
            description = select_text(details, 'li.description span.list-value').strip()
            other_names = select_text(details, 'li.also_known_as span.list-value').split(', ')
            replaces = select_text(details, 'li.product-superseded-list span.list-value').split(', ')
            condition = select_text(details, 'li.condition span.list-value').strip()
            brands = [img.get('src') for img in details.select('li.manufacturer img')]
            positions = select_text(details, 'li.positions span.list-value').split(', ')
            price = select_text(part_soup, 'div.product-purchase-module li.sale-price span#product_price').strip()
            part = {
                'part_num': part_num,
                'description': description,
                'other_names': other_names,
                'replaces': replaces,
                'condition': condition,
                'brands': brands,
                'positions': positions,
                'price': price,
                'name': name,
                'images': images
            }
            created, part = find_or_create(Accessory, part, session)
            sub_category.accessories.append(part)
            session.commit()

            fitment_module = part_soup.select('table.fitment-table tbody tr')

            for fitment in fitment_module:
                year = select_text(fitment, '.fitment-year').strip()
                make = select_text(fitment, '.fitment-make').strip()
                model = select_text(fitment, '.fitment-model').strip()
                trims = select_text(fitment, '.fitment-trim').strip().split(', ')
                engines = select_text(fitment, '.fitment-engine').strip().split(', ')

                car = {
                    'year': year,
                    'model': model,
                    'make': make
                }

                created_car, car = find_or_create(Car, car, session)

                if created_car:
                    for tr in trims:
                        tr = {
                            'trim': tr.strip()
                        }

                        created_tr, tr = find_or_create(Trim, tr, session)
                        car.trims.append(tr)
                        session.commit()

                        trim_car = session.query(TrimCar).filter_by(car_id=car.id, trim_id=tr.id).first()

                        for eng in engines:
                            eng = {
                                'engine': eng.strip()
                            }

                            created_eng, eng = find_or_create(Engine, eng, session)
                            trim_car.engines.append(eng)
                            session.commit()

                            trim_engine_and_car = (
                                session.query(TrimEngineAndCar).filter_by(engine_id=eng.id,
                                                                          trim_car_id=trim_car.id).first())
                            part.fits.append(trim_engine_and_car)
                else:
                    for tr in trims:
                        tr = {
                            'trim': tr.strip()
                        }

                        created_tr, tr = find_or_create(Trim, tr, session)

                        trim_car = session.query(TrimCar).filter_by(car_id=car.id, trim_id=tr.id).first()
                        if not trim_car:
                            continue
                        for eng in engines:
                            eng = {
                                'engine': eng.strip()
                            }

                            created_eng, eng = find_or_create(Engine, eng, session)

                            trim_engine_and_car = (
                                session.query(TrimEngineAndCar).filter_by(engine_id=eng.id,
                                                                          trim_car_id=trim_car.id).first())
                            if trim_engine_and_car:
                                part.fits.append(trim_engine_and_car)
        except IndexError:
            pass
        finally:
            pass


def get_parts(link, sub_category):
    res = requests.get(link)
    j = 1

    if res.status_code < 400:
        parts_soup = BeautifulSoup(res.content, 'html.parser')
        product_links = parts_soup.select('.catalog-products .catalog-product .product-title > a')
        for prod in product_links:
            print(f'{j}-th part: {prod.text.strip()}')
            j += 1
            get_part(base_url + '/' + prod.get('href').strip('/'), prod.text.strip(), sub_category)


if __name__ == '__main__':
    home_page = requests.get(base_url)
    soup = BeautifulSoup(home_page.content, 'html.parser')

    categories_soup = soup.select('#accessories-menu > .page-builder-layout-module > div')
    i = 0
    past_cat = 'Interior Accessories'
    for category in categories_soup:
        if i == 0:
            i+=1
            continue
        cat_title = select_text(category, '.heading').strip()
        if not len(cat_title):
            cat_title = past_cat
        past_cat = cat_title
        print(f'\n\ncategory {i}: {cat_title}\n\n')
        i += 1

        new_cat = {
            'name': cat_title
        }
        created_cat, new_cat = find_or_create(ACategory, new_cat, session)
        subcategories = category.select('ul.links-list > li > a')
        for subcategory in subcategories:
            sub_title = subcategory.text.strip()

            newsub = {
                'name': sub_title,
                'category': new_cat
            }
            created_sub, new_sub = find_or_create(ASubcategory, newsub, session)
            sub_cat_link = base_url + '/' + subcategory.get('href').strip('/')
            get_parts(sub_cat_link, new_sub)

    session.close()
