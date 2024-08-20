from selenium import webdriver
import os, time, datetime, csv
from bs4 import BeautifulSoup as BS
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import datetime
import string

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

def find_element(xpath):
	return BROWSER.find_element_by_xpath(xpath)

print "============================"
print "== Run started at ", datetime.datetime.now()
print "============================"


list_of_surnames = []

import contextlib
from selenium.webdriver import Remote
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import staleness_of


from selenium.common.exceptions import NoSuchElementException


def page_has_loaded( old_page ):
	 try:
		new_page = BROWSER.find_element_by_tag_name('html')
		if new_page.id != old_page.id:
			return True
		else:
			time.sleep(1)
			return page_has_loaded( old_page )
	 except NoSuchElementException:
		return False


def download_pages( BROWSER, i, w ):
	print "Page %s" % i

	with open( writepath, "a" ) as w:
		for x in range(2,12):
			a_list = BROWSER.find_elements_by_xpath("//*[@id='DataGrid1']/tbody/tr[%s]/td[1]/a" % x)
			for a in a_list:
				print a.text
				td_list = BROWSER.find_elements_by_xpath("//*[@id='DataGrid1']/tbody/tr[%s]/td[2]" % x)
				for td in td_list:
					print td.text
					w.write( "\t".join( [ str(i), a.text, td.text ] ) + "\n" )

	nav_links = BROWSER.find_elements_by_xpath("//*[@id='DataGrid1']/tbody/tr[12]/td[1]/a")
	
	if nav_links:
		lnk_num = ( i % 5 ) 		# modulo
		if len( nav_links ) == 6: 	# deal with the back link...
			lnk_num += 1

		nav_links[ lnk_num ].click()

		if page_has_loaded( BROWSER.find_element_by_tag_name('html') ):
			download_pages( BROWSER, i+1, writepath )
	else:
		print "No nav links..."


for letter in string.ascii_uppercase:
	print letter

	URL = "http://gbnames.publicprofiler.org/NameSelection.aspx?name=%s&year=1881&altyear=1998&country=GB&type=name" % letter
	BROWSER.get( URL )
	writepath  = "./surnames.%s.tsv" % letter
	download_pages( BROWSER, 1, writepath )


os.system( "rm geckodriver.log" )
