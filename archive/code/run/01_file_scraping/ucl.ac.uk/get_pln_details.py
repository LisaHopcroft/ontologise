from selenium import webdriver
import os, time, datetime, csv
from bs4 import BeautifulSoup as BS
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys  
import datetime

reload(sys)  
sys.setdefaultencoding('utf8')

SLEEP_TIME = 3
BROWSER = None
GOTO_URL = None
delay = 1

fp = webdriver.FirefoxProfile()
fp.set_preference('browser.helperApps.neverAsk.saveToDisk',
                   'image/jpeg,image/png,'
                   'application/octet-stream')
BROWSER = webdriver.Firefox(firefox_profile=fp)

academia_root = "/media/michael/Files/Dropbox/workspace/2.research"

def find_element(xpath):
	return BROWSER.find_element_by_xpath(xpath)


def download_page_as_data( writepath ):

	with open( writepath, 'a') as f:

		for i in range(1,50):
			xpath = "//*[@id='form1']/table/tbody/tr[%s]/td/div[1]/strong/a" % i
			el = BROWSER.find_element_by_xpath( xpath )
			text = el.text
			href = el.get_attribute("href")
			print text
			f.write( ( "\t".join([text, href]) ) + "\n" )

	f.close()

	# Moving to next page, and repeat...
	BROWSER.find_elements_by_xpath("//*[@id='submit']")[2].click()

	return download_page_as_data( writepath )



print "============================"
print "== Run started at ", datetime.datetime.now()
print "============================"


for root, dirs, files in os.walk( academia_root ):
	for filename in files:
		URL 		= ""
		filepath = "%s/%s" % ( root, filename )

		if filename == "@GET.[plns].tsv":
			URL = "http://www.ucl.ac.uk/lbs/estates/"

		if URL:
			writepath = root + '/01_TSV/ALL.html.tsv'

			# Start downloading
			BROWSER.get( URL )
			download_page_as_data( writepath )

os.system( "rm geckodriver.log" )
