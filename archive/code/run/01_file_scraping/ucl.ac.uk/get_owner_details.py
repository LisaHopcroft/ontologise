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



def download_page_as_data( writepath ):

	with open( writepath, 'a') as f:

		num_trs = len( BROWSER.find_elements_by_xpath( "//*[@id='form1']/table/tbody/tr" ) )
		for i in range( 1, num_trs+1 ):
			num_divs = len( BROWSER.find_elements_by_xpath( "//*[@id='form1']/table/tbody/tr[%s]/td/div" % i ) )
			claim = BROWSER.find_element_by_xpath( "//*[@id='form1']/table/tbody/tr[%s]/td/div[1]/strong/a" % i )
			claim_text = claim.text
			claim_href = claim.get_attribute("href")
			print num_divs
			for j in range( 1, num_divs+1 ):
				xpath 	= "//*[@id='form1']/table/tbody/tr[%s]/td/div[%s]/a" % ( i, j )
				if BROWSER.find_elements_by_xpath( xpath ):
					el 		= BROWSER.find_element_by_xpath( xpath )
					text 	= el.text
					href 	= el.get_attribute("href")
					print text
					f.write( ( "\t".join([text, href, claim_text, claim_href]) ) + "\n" )

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

		if filename == "@GET.[compensation-owners].tsv":
			URL = "https://www.ucl.ac.uk/lbs/search/"

		if URL:
			writepath = root + '/01_TSV/ALL.html.tsv'

			BROWSER.get( URL )

			el = BROWSER.find_element_by_id('input_category')
			for option in el.find_elements_by_tag_name('option'):
				if option.text == 'Owner-in-fee':
					option.click()

			BROWSER.find_element_by_xpath("//*[@id='submit']").click()

			# Start downloading
			download_page_as_data( writepath )

os.system( "rm geckodriver.log" )
