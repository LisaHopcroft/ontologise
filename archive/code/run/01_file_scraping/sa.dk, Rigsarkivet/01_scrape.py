from selenium import webdriver
import os, time, datetime, csv
from bs4 import BeautifulSoup as BS
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys  
import datetime

SLEEP_TIME = 2
BROWSER = None
GOTO_URL = None
delay = 1

fp = webdriver.FirefoxProfile()
adblockfile = '../adblock_plus-2.9.1-an+fx+sm+tb.xpi'
fp.add_extension (adblockfile)
fp.set_preference('browser.helperApps.neverAsk.saveToDisk',
                   'image/jpeg,image/png,'
                   'application/octet-stream')

academia_root = "/media/michael/Files/Dropbox/workspace/2.research"


def download_pages_as_data( BROWSER, dirpath, i ):
	writepath = "%s/%s.html" % ( dirpath, i )

	# change language to English
	if i==1:
		time.sleep( SLEEP_TIME )
		time.sleep( SLEEP_TIME )
		BROWSER.find_element_by_xpath( "/html/body/div[1]/nav/div/div/ul/li[1]/a" ).click()


	# save transciption
	time.sleep( SLEEP_TIME )
	time.sleep( SLEEP_TIME )
	with open( writepath, 'w') as f:
		all_txt = BROWSER.find_element_by_xpath( "//*[@id='listValues']" ).get_attribute('outerHTML')
		f.write( all_txt )
	

	# move to next page
	try:
		element = BROWSER.find_element_by_xpath( "/html/body/div[2]/div/div/div[2]/div[1]/ul/li[@class='active']/following-sibling::li/a" )
	except NoSuchElementException:
		return
	BROWSER.execute_script("arguments[0].click();", element)

	return download_pages_as_data( BROWSER, dirpath, i+1 )


print( "============================" )
print( "== Run started at ", datetime.datetime.now() )
print( "============================" )

for root, dirs, files in os.walk( "/media/michael/SSD3/Dropbox/workspace/2.research/01.Primary/01.Manuscripts/00.WWW/VIH, Virgin Islands History" ):
	for fname in files:
		if fname == "GET-URL.txt" and not "#" in fname:
			filepath = "%s/%s" % ( root, fname )
			with open( filepath, "r" ) as r:
				url = r.read().strip()
				print( url )
				
				page = 1
				BROWSER 	= webdriver.Firefox(firefox_profile=fp)
				BROWSER.get( url )
				if "&page=" in url:
					page = int(url.split("&page=",1)[1])
				else:
					BROWSER.find_element_by_xpath("/html/body/div[2]/div/div/table[2]/tbody/tr[1]/td[2]/a").click()

				dirpath = root+"/00_HTML"
				if not os.path.isdir( dirpath ):
					os.mkdir( dirpath )
				download_pages_as_data( BROWSER, dirpath, page )


os.system( "rm geckodriver.log" )

