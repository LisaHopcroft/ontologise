from pyvirtualdisplay import Display
from selenium import webdriver
import os, time, datetime
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import UnexpectedAlertPresentException
from socket import error as SocketError
import http.client
import csv
import glob


# update the searches based on existing files

publ_details = {}
with open('./publications.tsv', 'r') as tsv:
	tsv = csv.reader(tsv, delimiter='\t')
	for row in tsv:
		publ_details[row[0]] = ( row[1], row[2] )


def get_first_date( dirpath, start_date, end_date ):

	start_year = int(start_date[:4])
	end_year = int(end_date[:4])

	for year in range( end_year, start_year, -1 ):
		glob_txt = "%s/%s/*.pdf" % ( dirpath, year )
		for fpath in sorted( glob.glob( glob_txt ), reverse=True ):
			fname = fpath.rsplit("/",1)[1]
			date_el = fname.split("_")[2]
			yy = date_el[:4]
			mm = date_el[4:6]
			dd = date_el[6:8]
			return yy + "-" + mm + "-" + dd

	return start_date

with open('./get.tsv', 'r') as tsv, open('./searches.tsv', 'w') as w:
	tsv = csv.reader(tsv, delimiter='\t')

	for row in tsv:
		publ 		= row[0]
		start_date 	= row[1]
		end_date 	= row[2]
		save_dir = publ_details[publ][0]

		start_date = get_first_date( save_dir, start_date, end_date )
		print( start_date )
		
		writeline = "https://www.britishnewspaperarchive.co.uk/search/results/%s/%s?retrievecountrycounts=false&newspapertitle=%s&sortorder=dayearly\n" % ( start_date, end_date, publ_details[publ][1] )
		w.write( writeline )
		print( writeline )


#BROWSER = None
SLEEP_TIME = 1

def get_thumbnail_count():
	try:
		thumb_count = len(BROWSER.find_elements_by_xpath("//div[@class='thumbnailContainer']"))
	except http.client.BadStatusLine:
		print( "************************** BAD STATUS **********************************" )
		time.sleep(SLEEP_TIME)
		get_page( BROWSER.current_url() )
		return get_thumbnail_count()
	return thumb_count

def open_thumbnail(thumbnail_number):
	href = find_element("(//div[@class='thumbnailContainer']/a)[%d]"% (thumbnail_number)).get_attribute( "href" )
	print( href )
	get_page( href )

def get_page( url ):
	try:
		BROWSER.get( url )
	except UnexpectedAlertPresentException:
		print( "Handling alert..." )
		time.sleep(SLEEP_TIME)
		return get_page( url )
	except http.client.BadStatusLine:
		print( "************************** BAD STATUS **********************************" )
		time.sleep(SLEEP_TIME)
		return get_page( url )
	return

def find_element(xpath, iteration=0):
	try:
		el = BROWSER.find_element_by_xpath(xpath)
	except NoSuchElementException:
		print( "Did not find element (%s)... waiting and trying again..." % xpath )
		time.sleep(SLEEP_TIME)
		if iteration == 3:
			print( "Trying a refresh..." )
			BROWSER.refresh()
		if iteration == 5:
			print( "Giving up.... moving on..." )
			return False
		return find_element(xpath, iteration+1)
	except UnexpectedAlertPresentException:
		print( "Unexpected alert..." )
		time.sleep(SLEEP_TIME)
		if iteration == 3:
			print( "Trying a refresh..." )
			BROWSER.refresh()
		if iteration == 5:
			print( "Giving up.... moving on..." )
			return False
		return find_element(xpath, iteration+1)
	except SocketError:
		print( "Socket error..." )
		time.sleep(SLEEP_TIME)
		if iteration == 3:
			print( "Trying a refresh..." )
			BROWSER.refresh()
		if iteration == 5:
			print( "Giving up.... moving on..." )
			return False
		return find_element(xpath, iteration+1)
	except http.client.BadStatusLine:
		print( "************************** BAD STATUS **********************************" )
		time.sleep(SLEEP_TIME)
		if iteration == 3:
			print( "Trying a refresh..." )
			BROWSER.refresh()
		if iteration == 5:
			print( "Giving up.... moving on..." )
			return False
		return find_element(xpath, iteration+1)
	return el

def navigate_to_page(page_number):
	print( "%s&page=%d" % (URL, page_number) )
	get_page( "%s&page=%d" % (URL, page_number) )

def download_issue(thumbnail_number):
	open_thumbnail(thumbnail_number)
	page_count = get_thumbnail_count()
	for page_number in range(1, page_count + 1):
		print( " *** Page number (in issue) = %d"% page_number )
		open_thumbnail(page_number)
		save_url() #download_page()
		BROWSER.back()

def save_url():
	try:
		urlfile = open("urls.txt","a")
		href = find_element("//*[@id='ajaxcontainer']/section/div/div/div[2]/div/div[2]/div[1]/a[3]").get_attribute("href")
		print( "Writing URL..." ) # %s..." % href
		urlfile.write("%s\n" % href)
		urlfile.close()
	except UnexpectedAlertPresentException:
		print( "Unexpected alert..." )
		BROWSER.refresh()
		time.sleep(SLEEP_TIME)
		return save_url()
		


print( "============================" )
print( "== Run started at ", datetime.datetime.now() )
print( "============================" )

#display = Display(visible=0, size=(800, 600))
#display.start()

#
fp = webdriver.FirefoxProfile()

# Log in
BROWSER = webdriver.Firefox(firefox_profile=fp)
BROWSER.get("https://www.britishnewspaperarchive.co.uk/account/login")
f = open('./credentials.txt', 'r')
username, password = f.readlines()
f.close()
find_element("//input[@id='Username']").send_keys(username)
find_element("//input[@id='Password']").send_keys(password)
find_element("//input[@id='login-form-log-in']").click()
time.sleep(SLEEP_TIME) 
		


with open( "searches.tsv", "r" ) as r:
	i = 0
	for line in r.readlines():
		URL = line.strip()

		print( "Processing URL '%s'" % URL )

		'''
		navigate_to_page(0)
		ol = find_element("//div[@id='ajaxcontainer']/div[1]/div[2]/nav[1]/ol")

		if not ol:
			continue

		lis = ol.find_elements_by_css_selector("*")
		print( len(lis) )
		if len(lis) == 9+8:
			print( "... getting number of pages from last element ..." )
			#num_pages = find_element("//div[@id='ajaxcontainer']/div[1]/div[2]/nav[1]/ol/li[9]/a").get_attribute( "title" ).replace( "Skip to page ", "" )
			num_pages = 200 # can't get number of pages from this page
		else:
			print( "... getting number of pages from number of elements ..." )
			num_pages = len(lis)

		print( "Num pages: %s" % num_pages )
		'''

		num_pages = 200 # pages of results...

		for page_number in range(0, int(num_pages)-1):
			print( " * Filter page = %d"% page_number )
			navigate_to_page(page_number)
			thumbnail_count = get_thumbnail_count()
			print( " (%s issues on page)" % thumbnail_count )

			if thumbnail_count == 0:
				break # no search results, so move on to the next search

			for thumbnail_number in range(1, thumbnail_count + 1):
				print( " ** Issue number (on page) = %d"% thumbnail_number )
				download_issue(thumbnail_number)
				navigate_to_page(page_number) # return to the results page
			'''
			i += 1
			if i == 4:
				## Restarting browser (to avoid firefox crashing problem)
				print( "*** RESTARTING BROWSER ***" )
				print( "Logging out..." )
				get_page( "http://www.britishnewspaperarchive.co.uk/account/logout" )
				BROWSER.close()
				BROWSER.quit()
				time.sleep(SLEEP_TIME) 

				##
				fp = webdriver.FirefoxProfile()
				##			
				print( "Logging in..." )
				BROWSER = webdriver.Firefox(firefox_profile=fp)
				BROWSER.get("https://www.britishnewspaperarchive.co.uk/account/login")
				f = open('./credentials.txt', 'r')
				username, password = f.readlines()
				f.close()
				find_element("//input[@id='Username']").send_keys(username)
				find_element("//input[@id='Password']").send_keys(password)
				find_element("//input[@id='login-form-log-in']").click()
				time.sleep(SLEEP_TIME) 
				i = 0
			'''

print( "Logging out..." )
find_element("//a[@id='hello-log-out']").click()
time.sleep(SLEEP_TIME) 
BROWSER.close()
