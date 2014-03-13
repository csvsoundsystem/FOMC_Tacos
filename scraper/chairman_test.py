import urllib
import requests
from bs4 import BeautifulSoup
from urlparse import urljoin
import re
from datetime import datetime
from time import strftime
import os
import dataset
from pprint import pprint
from thready import threaded
from atm import ATM

# Chairman not assigned, throws off whole code, needs fix

######################## SETUP VARIABLES ########################

# Base URL definitions:
YEARS_URL = 'http://www.federalreserve.gov/newsevents/press/monetary/'
RELEASES_URL = 'http://www.federalreserve.gov/'

# Database definition
db = dataset.connect('sqlite:///frb_releases/federalreserve.db')

# Cache definition
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
	print "YEAR: %s" % years_url
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

	# This gets the raw dates from the HTML of each press release
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

	# Create a list of paragraphs with all the text for each press release
	paragraphs = []
	for p in soup.find_all('p'):
		text = p.text.encode('utf-8', 'ignore')
		# Sub out empty spaces that may cause prblems
		text = re.sub('\s{2,}', ' ', text).strip()
		# Sub out press release date paragraphs because we are storing them in separate column
		text = re.sub('(Release Date ?:) (\w+)(?: ?- ?\d+)? (\d+), (\d+)',' ', text).strip()
		paragraphs.append(text)

	# Turn list of paragraphs into one string
	text = " ".join(paragraphs) 
	
	# Determine if the press release is an FOMC statement
	# FOMC statements always say 'FOMC statement' in the title
	is_fomc = 1 if 'fomc statement' in title.lower() else 0

	# Assign Federal Reserve Chairman:

	Bernanke_date = datetime.strptime("2006-01-02", "%B %d, %Y")
	chairman = 'Greenspan' if date_object < Bernanke_date else None

	# Collect the data
	data = {
		'source_url': url,
		'title': title,
		'is_fomc': is_fomc,
		'chairman': chairman,
		'date': date_object,
		'text': text
	}

	# Upsert the data into the SQL lite database by source_url
	db['press_releases'].upsert(data, ['source_url'])


# Save the data
def run():
	annual_urls = [get_url_year(year) for year in years]
	url_list = [cook_soup(u) for u in annual_urls]
	
	# Unnest 
	items = [i for item in url_list for i in item ]
	
	# Thread the data collection
	threaded(items, get_data,  20, 200)
		
# Showtime
run()
