import re
from bs4 import BeautifulSoup
import requests
from app.db import Session
from app.db.models import Trim, Engine, Car, TrimCar


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
car_base = '/v-toyota'
home_page = requests.get(base_url + car_base)

soup = BeautifulSoup(home_page.content, 'html.parser')

vehicle_links = soup.select('#vehicle-data-lists li a')
for link in vehicle_links:
    model = link.text.strip()
    years_link = base_url + link.get('href')
    years_page = requests.get(years_link)
    years_soup = BeautifulSoup(years_page.content, 'html.parser')
    years_links = years_soup.select('#vehicle-data-lists .year li a')
    i = 1
    for year in years_links:
        engines_link = base_url + year.get('href')
        engines_page = requests.get(engines_link)
        engines_soup = BeautifulSoup(engines_page.content, 'html.parser')
        engines_links = engines_soup.select('#vehicle-data-lists ul li a')
        pattern = r'(.+)\s+([\d.]+L\s+[A-Za-z0-9\-\ ]+)'
        for eng_trm in engines_links:
            match = re.search(pattern, eng_trm.text.strip())
            if match is None:
                continue
            trim, engine = match.groups()

            new_car = {
                'make': 'Toyota',
                'model': model,
                'year': year.text.strip()
            }

            new_trim = {
                'trim': trim.strip()
            }

            new_engine = {
                'engine': engine.strip()
            }

            b, created_trim = find_or_create(Trim, new_trim, session)
            c, created_engine = find_or_create(Engine, new_engine, session)
            d, created_car = find_or_create(Car, new_car, session)
            created_car.trims.append(created_trim)
            session.commit()

            trim_car = session.query(TrimCar).filter_by(car_id=created_car.id, trim_id=created_trim.id).first()
            trim_car.engines.append(created_engine)
            session.commit()
            print(f'{i}-th')
            i += 1

session.close()
