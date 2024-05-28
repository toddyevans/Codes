import datetime
import time
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.by import By

sections=['italia','mondo','politica','cultura','scienza','internet','economia','sport']
df_sect=pd.DataFrame(sections)

num_section=int(input("Insert the number of the section that you would like to scrape: (0: Italia, 1: Mondo, 2: Politica, 3: Cultura, 4: Scienza, 5: Internet, 6: Economia, 7: Sport)"))
#num_page=input("Insert the number of pages that you would like to scrape: ")
article_links = []

# Get articles link from the pages
def get_article_links(url):
    article_links = []
    article_title=[]
    article_summary=[]
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    for article in soup.find_all('div', class_='_taxonomy-item__content_al3wh_53'):
        link = article.a['href']
        article_links.append(link)
    return article_links

def get_date(link):
  response = requests.get(link)
  soup = BeautifulSoup(response.text, 'html.parser')
  date_= soup.find('li', class_='_breadcrumbs__time_1nii6_67')
  date=date_.text.strip()

  return date

def convert_to_datetime(stringa_data):
    stringa = stringa_data.split(' ', 1)[1]
    mesi_italiani = {
        'gennaio': 1, 'febbraio': 2, 'marzo': 3, 'aprile': 4,
        'maggio': 5, 'giugno': 6, 'luglio': 7, 'agosto': 8,
        'settembre': 9, 'ottobre': 10, 'novembre': 11, 'dicembre': 12
    }
    parti = stringa.split(' ')
    giorno = int(parti[0])
    mese = mesi_italiani[parti[1].lower()]
    anno = int(parti[2])
    dat = "{:02d}-{:02d}-{}".format(giorno, mese, anno)
    data = datetime.strptime(dat, "%d-%m-%Y")

    return data

url_bas = 'https://www.ilpost.it/'+ df_sect.iloc[num_section,0] +'/page/'
number=input('Insert the number of page: ')

startDT = input("Start time (DD-MM-YYYY)")
try:
    startDT = datetime.strptime(startDT, "%d-%m-%Y")
except ValueError:
    print("wrong date time format")

endDT = input("End time (DD-MM-YYYY)")
try:
    endDT = datetime.strptime(endDT, "%d-%m-%Y")
except ValueError:
    print("wrong date time format")

links=[]
title=[]
summary=[]
date=[]
commNums=[]

while True:
  url = url_bas + str(number)
  article_links = get_article_links(url)

  if not article_links:
      break

  for link in article_links:
      article_date = get_date(link)
      if article_date:
          article_dat= convert_to_datetime(article_date)
          if startDT <= article_dat <= endDT:
              links.append(link)
              date.append(article_dat)
          if article_dat < startDT:
            break
  if article_dat < startDT:
    break

  number += 1


commNums=[]
title_art=[]
summary_art=[]

for url in links:
  driver = webdriver.Chrome()
  driver.get(url)
  time.sleep(1)
  driver.find_element(By.CLASS_NAME, "iubenda-cs-accept-btn").click() #Cookies
  time.sleep(1)
  soup_1 = BeautifulSoup(driver.page_source, 'html.parser')
  title_= soup_1.select_one('#index_main-content__nZYrw > div > div > article > div.index_main-content__header__WktGW > h1')
  title=title_.get_text(strip=True)
  sum_ = soup_1.select_one('#index_main-content__nZYrw > div > div > article > div.index_main-content__header__WktGW > h2')
  title_art.append(title)
  if sum_:
      summary=sum_.get_text(strip=True)
  else:
      summary='Null'
  summary_art.append(summary)

  try:
    show_comments_button = driver.find_element(By.XPATH, '//*[@id="showComments"]')
    show_comments_button.click() #Show Comments
    time.sleep(5)
    driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="gc-iframe"]')) #Switch to the frame
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser') #Get comments number
    comments = soup.select_one('body > div.gc-body.gc-theme-light.gc-theme-picton-blue > div.gc-header.translate-cloak > div.gc-headerItem.gc-header-left > h3 > a')

    comm=comments.text.strip()
    print(comm)
    if comm == 'Nessun commento':
      commNums.append("0 commenti")
    else:
      commNums.append(comm)
  except ElementClickInterceptedException:
    driver.find_element(By.CLASS_NAME, "iubenda-cs-accept-btn").click()
    show_comments_button = driver.find_element(By.XPATH, '//*[@id="showComments"]')
    show_comments_button.click() #Show Comments
    time.sleep(5)
    driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="gc-iframe"]')) #Switch to the frame
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser') #Get comments number
    comments = soup.select_one('body > div.gc-body.gc-theme-light.gc-theme-picton-blue > div.gc-header.translate-cloak > div.gc-headerItem.gc-header-left > h3 > a')
    comm=comments.text.strip()
    if comm == 'Nessun commento':
      commNums.append("0 commenti")
    else:
      commNums.append(comm)
  except NoSuchElementException:
    print("The button ShowComments was not found")
    commNums.append("0 commenti")
  finally:
    driver.close()


driver.quit()
num = []
for comment in commNums:
  numb= comment.split()[0]
  num.append(int(numb))

import openpyxl
print('Number of page: ', number)
df_art= pd.DataFrame({'Title': title_art, 'Summary': summary_art, 'Link': links, 'Date': date, 'Comments': num})
df_art.to_excel('Post'+ ' ' + sections[num_section] + ' ' + str(startDT) + ' ' + str(endDT) + ' .xlsx')