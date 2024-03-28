# from bs4 import BeautifulSoup
# from app.db import Session
# from app.api.models import Car
# import requests
#
# session = Session()
#
# base_url = 'https://www.oemgenuineparts.com'
# car_base = '/v-toyota'
# home_page = requests.get(base_url + car_base)
#
# soup = BeautifulSoup(home_page.content, 'html.parser')
#
# vehicle_links = soup.select('#vehicle-data-lists li a')
# for link in vehicle_links:
#     model = link.text.strip()
#     years_link = base_url + link.get('href')
#     years_page = requests.get(years_link)
#     years_soup = BeautifulSoup(years_page.content, 'html.parser')
#     years_links = years_soup.select('#vehicle-data-lists .year li')
#     i=0
#     for year in years_links:
#         car = {
#             "make": "Toyota",
#             "model": model,
#             "year": year.text.strip(),
#         }
#
#         car = Car(**car)
#         session.add(car)
#         session.commit()
#         print(i)
#         i += 1
#
# session.close()
