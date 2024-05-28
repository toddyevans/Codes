import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

num_section=int(input("Insert the number of the section that you would like to scrape: (0: Cronaca Locale, 1: Mondo, 2: Politica, 3: Salute, 4: Tecnologia, 5: Economia, 6: Sport)"))
sections=['cronaca-locale-167540','esteri','internet','salute','tecnologia','economia','sport']
df_sect=pd.DataFrame(sections)

article_links = []
article_comments = []
article_date=[]

from datetime import datetime

def convert_to_datetime(date_string):
    month_map = {
        "Gennaio": 1, "Febbraio": 2, "Marzo": 3, "Aprile": 4,
        "Maggio": 5, "Giugno": 6, "Luglio": 7, "Agosto": 8,
        "Settembre": 9, "Ottobre": 10, "Novembre": 11, "Dicembre": 12
    }

    date_time_parts = date_string.split(" - ")

    date_parts = date_time_parts[0].split()
    month = month_map[date_parts[1]]
    day = int(date_parts[0])
    year = int(date_parts[2])

    time_parts = date_time_parts[1].split(":")
    hour = int(time_parts[0])
    minute = int(time_parts[1])
    date=datetime(year, month, day, hour, minute)
    formatted_date = date.strftime("%d-%m-%Y %H:%M")
    formatted_date=datetime.strptime(formatted_date,"%d-%m-%Y %H:%M")
    return formatted_date

def get_article_links(url):
    article_links = []
    article_title = []
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    for article in soup.find_all('div', class_='cards'):

    #Get the link
      for a_tag in article.find_all('a', class_='card'):  # Find all <a> tags with class 'card'
            link = a_tag.get('href') # Get the 'href' attribute value
            title=a_tag.find('div','card__title').get_text()
            if link.startswith ('https://'):  # Ensure a link is present
              continue
            else:
              link_final = 'https://www.ilgiornale.it' + link
              article_links.append(link_final)
              article_title.append(title)

    return article_links

def get_date_comment(link):
  response = requests.get(link)
  soup = BeautifulSoup(response.text, 'html.parser')
  h1=soup.find('h1', class_='content__title')
  if h1:
      title=h1.find('span').get_text()
  else:
      title='Null'
  div=soup.find('div', class_='content__excerpt')
  if div:
      summary=div.find('p').get_text()
  else:
      summary='Null'

  date_= soup.find('span', class_='content__date')
  if date_:
      date=date_.text.strip()
  else:
      date='Null'
  comment = soup.find('a', class_='comments-link')
  if comment:
    commNum=int(comment.text.strip())
  else:
    commNum=0
  return date, commNum, title, summary

url_bas = 'https://www.ilgiornale.it/sezioni/'+ df_sect.iloc[num_section,0] +'.html?page='
number=1

startDT = input("Start time (DD-MM-YYYY HH:MM)")
try:
    startDT = datetime.strptime(startDT, "%d-%m-%Y %H:%M")
except ValueError:
    print("wrong date time format")

endDT = input("End time (DD-MM-YYYY HH:MM)")
try:
    endDT = datetime.strptime(endDT, "%d-%m-%Y %H:%M")
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
      article_date, article_comments, article_title, article_sum = get_date_comment(link)
      if article_date:
          article_date = convert_to_datetime(article_date)
          if startDT <= article_date <= endDT:
              links.append(link)
              title.append(article_title)
              summary.append(article_sum)
              date.append(article_date)
              commNums.append(article_comments)
          if article_date < startDT:
            break
  if article_date < startDT:
    break

  number += 1

df2=pd.DataFrame({'Title': title,'Summary': summary, 'Link': links, 'Date':date, 'Comments':commNums})
unique_df = df2.drop_duplicates(subset='Link')


unique_df.to_excel('Giornale '+ sections[num_section] + ' ' + str(startDT) + ' ' + str(endDT) + ' .xlsx')