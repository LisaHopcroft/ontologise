from selenium import webdriver
import os, time, datetime, csv
from bs4 import BeautifulSoup as BS
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys  
import datetime

#reload(sys)  
#sys.setdefaultencoding('utf8')
#sys.setrecursionlimit(10000)

SLEEP_TIME = 3
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


def move_to_next_page( BROWSER ):
	first_xpath 	= "html/body/table[3]/tbody/tr[4]/td[3]/form/input[4]"
	second_xpath 	= "html/body/table[3]/tbody/tr[4]/td[4]/form/input[4]"
	first_button	= None
	second_button	= None

	if BROWSER.find_elements_by_xpath( first_xpath ):
		first_button = BROWSER.find_element_by_xpath( first_xpath )
	if BROWSER.find_elements_by_xpath( second_xpath ):
		second_button = BROWSER.find_element_by_xpath( second_xpath )

	if second_button:
		if "Next" in second_button.get_attribute('value'):
			second_button.click()
			return True
		else:
			return False
	elif first_button:
		if "Next" in first_button.get_attribute('value'):
			first_button.click()
			return True
		else:
			return False
	else:
		print( "Page hasn't loaded?" )
		return False


def download_page_as_data( BROWSER, dirpath, prefix, i ):
	writepath = "%s/%s_%s.html" % ( dirpath, prefix, i )

	if "Sorry, The Server Is Busy" in BROWSER.find_element_by_xpath( "html/body" ).text:
		print( "Sorry, The Server Is Busy" )
		BROWSER.execute_script("window.history.go(-1)")
		time.sleep( SLEEP_TIME )
		time.sleep( SLEEP_TIME )
		move_to_next_page( BROWSER )
		download_page_as_data( BROWSER, dirpath, prefix, i )

	with open( writepath, 'w') as f:

		all_txt = BROWSER.find_element_by_xpath( "html/body/table[3]" ).get_attribute('outerHTML')
		f.write( all_txt )

	# Moving to next page, and repeat...
	proceeding = move_to_next_page( BROWSER )
	if not proceeding:
		return

	return download_page_as_data( BROWSER, dirpath, prefix, i+1 )


print( "============================" )
print( "== Run started at ", datetime.datetime.now() )
print( "============================" )

for root, dirs, files in os.walk( "/mnt/SSD3/Dropbox/workspace/2.research/01.Sources/01.Primary/02.Publications/(D), Records/Census Records" ):
	for fname in files:
		if fname.endswith( "freecen.pieces.list" ) and not "#" in fname:
			filepath = "%s/%s" % ( root, fname )
			with open( filepath, "r" ) as r:
				pieces = r.read().splitlines()
					
				for piece in pieces:
					print( piece )
					if "No matches" in piece:
						folio_num = "0"
					elif "#" in piece:
						print( "Skipping" )
						continue
					else:
						folio_num = "1"
					piece = piece.replace( "No matches", "" ).replace( "#", "" ).replace( " ", "" )

					BROWSER 	= webdriver.Firefox(firefox_profile=fp)
					URL 		= "https://www.freecen.org.uk/cgi/search.pl"
					BROWSER.get( URL )

					# -------------------------------------#
					# set search criteria
					# -------------------------------------#

					# change to previous version
					el = BROWSER.find_element_by_xpath( "/html/body/div[2]/main/div/div[1]/p/a" )
					el.click()
					time.sleep( SLEEP_TIME )
					time.sleep( SLEEP_TIME )
					el = BROWSER.find_element_by_xpath( "/html/body/b/font/font/font/font/b/table/tbody/tr/td[1]/font/b/a" )
					el.click()
					time.sleep( SLEEP_TIME )
					time.sleep( SLEEP_TIME )

					val_year = "1871"

					# year
					el = BROWSER.find_element_by_xpath( "html/body/form/table/tbody/tr[1]/td[2]/select" )
					for option in el.find_elements_by_tag_name('option'):
						if option.text == val_year:
							option.click() # select() in earlier versions of webdriver
							break

					# start
					val_folio = "0"
					val_page = "1"
					val_schedule = "1"
					val_district = "1"
					val_iteration = 1
					val_folio = "0"
					val_page = "5"
					val_schedule = "22"
					val_district = "9"
					val_iteration = 749

					# piece
					el = BROWSER.find_element_by_xpath( "html/body/form/table/tbody/tr[2]/td[2]/input" )
					el.send_keys( piece )

					# folio
					el = BROWSER.find_element_by_xpath( "html/body/form/table/tbody/tr[14]/td[2]/input[1]" )
					el.send_keys( val_folio )

					# page
					el = BROWSER.find_element_by_xpath( "html/body/form/table/tbody/tr[14]/td[2]/input[2]" )
					el.send_keys( val_page )

					# schedule
					el = BROWSER.find_element_by_xpath( "/html/body/form/table/tbody/tr[14]/td[2]/input[3]" )
					el.send_keys( val_schedule )

					# enumeration district
					el = BROWSER.find_element_by_xpath( "/html/body/form/table/tbody/tr[3]/td[2]/input" )
					el.send_keys( val_district )

					# submit
					BROWSER.find_element_by_xpath( "html/body/form/input[1]" ).click()


					if "Sorry, we found no matches" in BROWSER.find_element_by_xpath( "html/body" ).text:
						print( "Sorry, we found no matches" )
						continue

					if "Sorry, The Server Is Busy" in BROWSER.find_element_by_xpath( "html/body" ).text:
						print( "Sorry, The Server Is Busy" )
						continue

					# -------------------------------------#
					# open first household
					# -------------------------------------#

					BROWSER.find_element_by_xpath( "/html/body/table[3]/tbody/tr[5]/td[23]/form/input[4]" ).click()
					# "/html/body/table[3]/tbody/tr[5]/td[19]/form/input[4]" if 1841 ... for some reason...

					# -------------------------------------#
					# start downloading
					# -------------------------------------#

					download_page_as_data( BROWSER, root + "/00_HTML/%s, Lochwinnoch" % piece, str(piece), val_iteration )


os.system( "rm geckodriver.log" )
