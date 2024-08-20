from selenium import webdriver
import os, time, datetime, csv
from bs4 import BeautifulSoup as BS
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys  
import datetime
import urllib


SLEEP_TIME = 1
fp = webdriver.FirefoxProfile()
BROWSER = webdriver.Firefox(firefox_profile=fp)


def download_page(URL, root):
	if os.path.isfile(root+"/00_HTML/ALL.html"): return
	BROWSER.get( URL )
	if not os.path.exists(root+"/00_HTML"): os.mkdir(root+"/00_HTML")
	with open(root+"/00_HTML/ALL.html", "w") as f:
		f.write(BROWSER.page_source)#.encode('ascii', 'ignore')


for root, dirs, files in os.walk( "/media/michael/Files/Dropbox/workspace/2.research/01.Primary/01.Manuscripts/00.WWW/SP, Scotlands Places" ):
	for fname in files:
		if fname=="GET.urls" or fname=="#GET.urls":
			with open( root + "/" + fname, "r" ) as r:
				for line in r.readlines():
					if line.startswith("#"): continue
					if line.strip() == "": continue
					URL = line.strip()
					if not URL.endswith("/1"): URL = URL + "?display=transcription"
					download_page( URL, root )
