import urllib
import requests
from bs4 import BeautifulSoup
from urlparse import urljoin
import re
from datetime import datetime
import os
import dataset
from pprint import pprint
from thready import threaded
from atm import ATM

######################## SETUP VARIABLES ########################

# Base URL definitions:
YEARS_URL = 'http://www.federalreserve.gov/newsevents/press/monetary/'
RELEASES_URL = 'http://www.federalreserve.gov/'

# Database definition
db = dataset.connect('sqlite:///frb_releases/federalreserve.db')

teller = ATM('cache-dir')

# Details for handling dates
re_date = re.compile(r"(\w+)(?: ?- ?\d+)? (\d+), (\d+)")

#OLD: (\w+) (\d+)(?: ?- ?\d+)?, (\d+)
#NEW: (\w+)(?: ?- ?\d+)? (\d+), (\d+)
#Former solution:
	#re_date = re.compile(r"(Release Date|meeting of):? (.*)", re.IGNORECASE)
date_format = '%B %d, %Y'
date_object = []

# Define the year range for the press releases
# Press releases start in 1996, end in 2014
years = range(1996, 2015)


######################### 	FUNCTIONS 	##########################

# Creat a list of annual URLs with all the press release URLs
def get_url_year(year):

	return urljoin(YEARS_URL,str(year)+'monetary.htm')

# Take the list of annual URLs and extract the press release URLs for each year
# Press releases for each year are saved into the urls list
def cook_soup(years_url):
	#print "YEAR: %s" % years_url
	response = teller.get_cache(years_url)
	#print response
	soup = BeautifulSoup(response.content)
	#print soup
	items = []
	for link in soup.find_all('div', {'class':'indent'}):
		a_tag = link.find('a')
		url_suffix = a_tag.attrs['href']
		url_full = urljoin(RELEASES_URL, url_suffix)
		
		title = a_tag.text
		
		item = (url_full, title.encode('utf-8', 'ignore').strip())
		
		items.append(item)

	return items

# Parse the data from each press release URL
def get_data(i):
	
	url, title = i
	print url

	response = teller.get_cache(url)
	soup = BeautifulSoup(response.content)

	if soup.find('p', {'id':'prContentDate'}):
		#This gets the press releases for HTML structure after 2006
		raw_date = soup.find('p', {'id':'prContentDate'}).text
	#Exception for problemsome October 2003 meeting
	elif soup.find("font", {"size":"+1"}):
		raw_date = soup.find("font", {"size":"+1"}).text
	#Exception for problemsome November 1996 meeting
	elif soup.find("font", {"size":"+2"}):
		raw_date = soup.find("font", {"size":"+2"}).text
	#Exception for problemsome November 2002 meeting
	elif soup.find("div", {"class":"head2"}):
		raw_date = soup.find("div", {"class":"head2"}).text
	#Exception for problemsome October 2008 meeting
	elif soup.find("div", {"class":"releaseDate"}):
		raw_date = soup.find("div", {"class":"releaseDate"}).text
	#Exception for problemsome September 2008 Wachovia press release
	elif soup.find("h4"):
		raw_date = soup.find("h4").text
	#Exception for problemsome February 2009 Treasury press release
	elif soup.find("b"):
		raw_date = soup.find("b").text	
	else:
		#This gets the press releases for HTML structure before 2006
		raw_date = soup.find('i').text

	#This turns the raw dates into data objects	
	m = re_date.search(raw_date)
	#print raw_date, m.groups()
	if m:
		date_string = m.group(1).replace("Plan", "") + " " + m.group(2) + ", " + m.group(3)
		date_object = datetime.strptime(date_string, date_format)

	else:
		date_object = None
		print "ERROR parsing date: %s" % raw_date

	paragraphs = []
	raw_paragraphs = []
	for p in soup.find_all('p')[1:]:
	# ignore date paragraph
		raw_paragraphs.append(p.text)
		
		# buld up a list of paragraphs
		text = p.text.encode('utf-8', 'ignore')
		text2 = re.sub('\s{2,}', ' ', text).strip()
		paragraphs.append(text2)
		#if text and not text2:
			#print "ERROR: text=", text 
		paragraphs.append(text2)

	# tests if all paragraphs are blanks
	#if not any(p for p in paragraphs):
		#print("Error")
		#import pprint
		#pprint.pprint(raw_paragraphs)


	# Turn list of paragraphs into one string, but remove CRLFs
	text = " ".join(paragraphs) #.replace("\n", " ").replace("\r", " ")
	
	# determine if it's a fomc statement
	is_fomc = 1 if 'fomc statement' in title.lower() else 0

	# Collect the data
	data = {
		'source_url': url,
		'title': title,
		'is_fomc': is_fomc,
		'date': date_object,
		'text': text
	}

	db['press_releases'].upsert(data, ['source_url'])


# Save the data
def run():
	if os.path.exists('frb_releases/federalreserve.db'):
		os.remove('frb_releases/federalreserve.db')

	annual_urls = [get_url_year(year) for year in years]
	url_list = [cook_soup(u) for u in annual_urls]
	
	# unnest
	items = [i for item in url_list for i in item ]
	
	# thread that shit
	threaded(items, get_data,  20, 200)
		
# Showtime
run()