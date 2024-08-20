import os, time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import sys  
import datetime
import urllib
import glob


dl_dir = "/home/michael/Downloads"

SLEEP_TIME = 1
fp = webdriver.FirefoxProfile()
fp.set_preference("browser.download.panel.shown", False)
fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "image/jpeg")
fp.set_preference("browser.download.dir", dl_dir)
BROWSER = webdriver.Firefox(firefox_profile=fp)


def get_description( url, root, fname ):
	print( "URL: " + url )
	BROWSER.get( url )

	title_html = BROWSER.find_element_by_xpath("//*[@id=\"contentHeader\"]/h1").get_attribute('innerHTML')
	description_html = BROWSER.find_element_by_xpath("//*[@id=\"content\"]").get_attribute('innerHTML')

	wpath = root + "/@20190819, AMG/00_HTML/%s.html" % fname
	if not os.path.exists( root + "/@20190819, AMH" ): os.mkdir( root + "/@20190819, AMG" )
	if not os.path.exists( root + "/@20190819, AMH/00_HTML" ): os.mkdir( root + "/@20190819, AMG/00_HTML" )
	with open( wpath, "w" ) as w:
		w.write( title_html + "\n\n" )
		w.write( description_html )


for root, dirs, files in os.walk( "/media/michael/Files/Dropbox/workspace/2.research/01.Primary/03.Maps etc/00.WWW/NAN, Nationaal Archief (NED)" ):
	for fname in files:
		if fname.startswith( "amh" ) and fname.endswith( ".url" ):
			fpath = "%s/%s" % ( root, fname )
			with open( fpath, "r" ) as r:
				lines = r.readlines()
				if len(lines) > 0:
					line = lines[0].strip()
					get_description( line, root, fname )
