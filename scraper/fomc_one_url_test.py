import urllib
import requests
from bs4 import BeautifulSoup
from urlparse import urljoin
import re
from datetime import datetime 

# Insert test URL here to run and tweak code:
# Once tweaked, feed mandatory fixes into fomc_all
url = 'http://www.federalreserve.gov/fomc/minutes/20021210.htm'

re_date = re.compile(r"(\w+)(?: ?- ?\d+)? (\d+), (\d+)")
date_format = '%B %d, %Y'
date_object = []



def cook_soup(url): 

	response = requests.get(url)
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
		"""
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
		"""
	# parse text
	paragraphs = []
	for p in soup.find_all('p'):
		text = p.text.encode('utf-8', 'ignore')
		# Sub out empty spaces that may cause prblems
		text = re.sub('\s{2,}', ' ', text).strip()
		text = re.sub('(Release Date ?:) (\w+)(?: ?- ?\d+)? (\d+), (\d+)',' ', text).strip()
		paragraphs.append(text)

		# This was the source of the problem
		"""# ignore date paragraph
		if re_date.search(p.text):
		# build up a list or paragraphs
			text = p.text.encode('utf-8', 'ignore')
			# Sub out empty spaces that may cause prblems
			text = re.sub('\s{2,}', ' ', text).strip()
			paragraphs.append(text)
		"""

	text = " ".join(paragraphs) 
			
	"""if text is None:
		text = p.text.encode('utf-8', 'ignore')
		# Sub out empty spaces that may cause prblems
		text = re.sub('\s{2,}', ' ', text).strip()
		paragraphs.append(text)"""

	# print to console
	#print paragraphs
	print date_object, text

cook_soup(url)