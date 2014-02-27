import urllib
import requests
from bs4 import BeautifulSoup
from urlparse import urljoin
import re
from datetime import datetime
import os

years_url = 'http://www.federalreserve.gov/newsevents/press/monetary/2014monetary.htm'
releases_url = 'http://www.federalreserve.gov/'

def get_stuff(url):

	response = requests.get(years_url)
	#print response
	soup = BeautifulSoup(response.content)
	#print soup
	urls = []
	titles = []
	for link in soup.find_all('div', {'class':'indent'}):
		a_tag = link.find('a')
		url_suffix = a_tag.attrs['href']
		title = a_tag.text
		url_full = urljoin(releases_url, url_suffix)
		urls.append(url_full)
		titles.append(title)
		print "href:", url_suffix
		print "text:", title

	return urls, titles 

urls, title =  get_stuff(years_url) 



