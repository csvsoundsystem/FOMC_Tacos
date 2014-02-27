import urllib
import requests
from bs4 import BeautifulSoup
from urlparse import urljoin
import re
from datetime import datetime 

# URL definition:
#url = 'http://www.federalreserve.gov/newsevents/press/monetary/20140129a.htm'
url = 'http://www.federalreserve.gov/fomc/minutes/19961113.htm'

re_date = re.compile(r"(Release Date|meeting of):? (.*)", re.IGNORECASE)
date_format = '%B %d, %Y'

def cook_soup(): 

  response = requests.get(url)
  soup = BeautifulSoup(response.content)

  # parse date
  if soup.find('p', {'id':'prContentDate'}):
    #This gets the press releases for HTML structure after 2006
    raw_date = soup.find('p', {'id':'prContentDate'}).text
  elif soup.find("font", {"size":"+2"}):
    raw_date = soup.find("font", {"size":"+2"}).text
  else:
    #This gets the press releases for HTML structure before 2006
    raw_date = soup.find('i').text
  m = re_date.search(raw_date)
  print raw_date
  if m:
    date_string = m.group(2)
    date_object = datetime.strptime(date_string, date_format)
  else:
    print "ERROR parsing date: %s" % raw_date

  # parse text
  paragraphs = []
  for p in soup.find_all('p'):
    # ignore date paragraph
    if not re_date.search(p.text):
      # buld up a list or paragraphs
      paragraphs.append(p.text.encode('utf-8').strip())

  # turn list of paragraphs into one string
  text = " ".join(paragraphs)

  # print to console
  print date_object, text

cook_soup()