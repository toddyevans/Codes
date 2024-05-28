import time
from datetime import datetime

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver


def convert_time(tim):
    dt = datetime.strptime(tim, '%Y-%m-%dT%H:%M:%S%z')
    formatted_time_string = dt.strftime('%d-%m-%Y %H:%M')
    date = datetime.strptime(formatted_time_string, '%d-%m-%Y %H:%M')

    return date


url_bas='https://www.theguardian.com/uk-news?page='
number=input('Insert the number of page: ')

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


article_links = []
article_comments = []
article_date=[]
article_title=[]
article_summary=[]

while True:
  url = url_bas + str(number)
  driver = webdriver.Chrome()
  driver.get(url)
  time.sleep(3)

  html_1=driver.page_source
  soup = BeautifulSoup(html_1, 'html.parser')


  for li_tag in soup.find_all('div', class_='fc-item'):
    timestamp=li_tag.find('time', 'fc-item__timestamp' )
    tim=timestamp.get('datetime')
    if startDT <= convert_time(tim) <= endDT:
      article_date.append(tim)
      a_tag=li_tag.find('a', 'u-faux-block-link__overlay')
      link = a_tag.get('href')
      article_links.append(link)
      span_tag=li_tag.find('span', 'js-headline-text')
      title=span_tag.get_text(strip=True)
      article_title.append(title)
      div_tag=li_tag.find('div','fc-item__standfirst')
      if div_tag:
          summary=div_tag.get_text(strip=True)
          article_summary.append(summary)
      else:
          summary='None'
          article_summary.append(summary)

      comments=li_tag.find('a', 'fc-trail__count')
      if comments:
        comm=comments.get('aria-label')
        commNum=comm.split()[0].replace(',', '')
      else:
        commNum = 0
      article_comments.append(commNum)

    if convert_time(tim) < startDT:
      break

  if convert_time(tim) < startDT:
    break
  number += 1


print('Number of page: ', number)
df2=pd.DataFrame({'Title': article_title,'Summary': article_summary,'Url': article_links, 'Date':article_date, 'Comments': article_comments})
df2.to_excel('The Guardian '+ 'Uk_News' + ' ' + str(startDT) + ' ' + str(endDT) + ' .xlsx')