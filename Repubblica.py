import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, ElementClickInterceptedException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

num_section=int(input("Insert the number of the section that you would like to scrape: (0: Cronaca, 1: Esteri, 2: Politica, 3: Salute, 4: Economia, 5: Sport)"))
sections=['cronaca','esteri','politica','salute','economia','sport']
df_sect=pd.DataFrame(sections)


#num_page=input("Insert the number of pages that you would like to scrape ")
article_links = []
article_time = []
article_title=[]
article_summary=[]

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

oldST = startDT
if startDT > endDT:
    startDT = endDT
    endDT = oldST

lastFoundTime = datetime.now()
num_page = int(input('Insert the number of page: '))
breaker = False
url_bas = 'https://www.repubblica.it/'+ df_sect.iloc[num_section,0] +'/'

while lastFoundTime > startDT:

  number = str(num_page)
  url = "".join((url_bas, "", number))
  response = requests.get(url)
  soup = BeautifulSoup(response.text, 'html.parser')
  section = soup.select_one('body > main > div:nth-child(2) > div.gd-column-8 > section.block.block__layout-list')
  divOut = section.find_all('div', class_='entry__content')
  firstDT = datetime.strptime(divOut[0].find('time')['datetime'], "%Y-%m-%dT%H:%MZ")
  lastDT = datetime.strptime(divOut[len(divOut)-1].find('time')['datetime'], "%Y-%m-%dT%H:%MZ")
  lastFoundTime = lastDT
  num_page += 1

  if lastDT > endDT:
      continue

  for ddiv in divOut:
    if ddiv.find('span', attrs = {'class': 'cntr-commertial'}):
        ddiv.decompose()
        continue
    artDT = datetime.strptime(ddiv.find('time')['datetime'], "%Y-%m-%dT%H:%MZ")
    if artDT > endDT:
          continue
    if artDT < startDT:
          breaker = True
          break
    entry_title_a = ddiv.find('h2', class_='entry__title').find('a')
    alink = entry_title_a['href']
    atitle = entry_title_a.get_text(strip=True)
    article_title.append(atitle)
    article_links.append(alink)
    if ddiv.find('div', class_='entry__summary'):
        entry_summary_a = ddiv.find('div', class_='entry__summary').find('a')
        asummary = entry_summary_a.get_text(strip=True)
    else:
        asummary='Null'
    article_summary.append(asummary)
    article_time.append(artDT.strftime("%Y-%m-%d %H:%M"))

  if breaker:
    break

article_comments = []


#Get comments number
for link in article_links:
  driver = webdriver.Chrome()
  driver.get(link)
  time.sleep(5)

  try:
    driver.find_element(By.XPATH, '//*[@id="iubenda-cs-banner"]/div/div/div/div[1]/div[2]/div/button[2]').click()
    time.sleep(5)

  #WIDGET
  #driver.find_element(By.XPATH, '//*[@id="exitIntentClose"]').click()
  #WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="exitIntent"]'))) #Timeout exception, it doesn't find the element

  except NoSuchElementException:
    driver.find_element(By.XPATH, '//*[@id="iubenda-cs-banner"]/div/div/div/button').click()
    print("No cookies here ")

  except ElementClickInterceptedException:
    driver.find_element(By.XPATH, '//*[@id="exitIntentClose"]').click()
    driver.find_element(By.XPATH, '//*[@id="iubenda-cs-banner"]/div/div/div/div[1]/div[2]/div/button[2]').click()
  driver.maximize_window()


  try:
      #driver.find_element(By.XPATH, '//*[@id="commentsTrigger"]').click()
      driver.find_element(By.CLASS_NAME, 'story__comments__trigger').click()
      time.sleep(1)
  except (ElementClickInterceptedException, ElementNotInteractableException) as e:
      print("Error occurred while clicking Show Comments button:", e)
      try:
        but=driver.find_element(By.XPATH, '//*[@id="exitIntentClose"]')
        driver.execute_script("arguments[0].click();", but)
        time.sleep(2)
        driver.find_element(By.CLASS_NAME, 'story__comments__trigger').click()
      except NoSuchElementException:
        print("The banner was not found")
      except ElementNotInteractableException:
        b=driver.find_element(By.CLASS_NAME, 'story__comments__trigger')
        driver.execute_script("arguments[0].click();", b)
      #driver.find_element(By.XPATH, '//*[@id="commentsTrigger"]').click()
  except NoSuchElementException:
          print("The button ShowComments was not found")

  time.sleep(2)

  soup = BeautifulSoup(driver.page_source, 'html.parser')
  comment_div = soup.find('span', class_='vf-badge')  # Get comments number
  if comment_div is None:
      comment_div = soup.find('span', class_='vf-badge vf-label-text vf-badge--accent-color vf-badge--disabled vf-square-badge vf-square-badge--small vf-nav-tab-button__badge')
      if comment_div is None:
        print("The button ShowComments was not found")
        article_comments.append(0)
      else:
        comments = comment_div.find('span')
        article_comments.append(int(comments.text.strip()))

  else:
      comments = comment_div.find('span')  # Get comments number
      article_comments.append(int(comments.text.strip()))

  driver.close()

print('Number of page: ', number)
df2 = pd.DataFrame({ 'Title': article_title, 'Summary': article_summary, 'Link': article_links, 'Date': article_time, 'CommNum': article_comments})
df2.to_excel('Repubblica '+ df_sect.iloc[num_section,0] + ' ' + str(startDT) + str(endDT) + '.xlsx')