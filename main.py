
import requests
from bs4 import BeautifulSoup

response = requests.get('https://www.ilpost.it/2024/05/27/senna-balneabile-pfas-tfa/')
soup = BeautifulSoup(response.text, 'html.parser')
date_= soup.find('li', class_='_breadcrumbs__time_1nii6_67')
date=date_.text.strip()
title_ = soup.find('div', class_='index_main-content__header__WktGW ')
if title_:
  title = title_.find('h1').get_text(strip=True)
  sum_ = title_.find('h2')
  if sum_:
      summary = sum_.get_text(strip=True)
  else:
      summary = 'Null'
else:
  title='Null'
  summary='Null'