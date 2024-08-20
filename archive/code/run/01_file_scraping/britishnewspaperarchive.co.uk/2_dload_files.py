from pyvirtualdisplay import Display
from selenium import webdriver
import os, time, datetime
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import UnexpectedAlertPresentException
from socket import error as SocketError
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
import csv

import sys
sys.path.append("/media/michael/Files/Dropbox/workspace/2.research/_bin")
#from ontologize.modules.util.all import *


os.system( "python2.7 3_mv_files.py" )


print( "============================" )
print( "== Run started at ", datetime.datetime.now() )
print( "============================" )

publ_details = {}
with open('./publications.tsv', 'r') as tsv:
	tsv = csv.reader(tsv, delimiter='\t')
	for row in tsv:
		publ_details[row[0]] = row[1]

tmp_dir = "/home/michael/Downloads"


SLEEP_TIME = 1

def find_element(xpath):
	try:
		el = BROWSER.find_element_by_xpath(xpath)
	except NoSuchElementException:
		print( "Did not find element... waiting and trying again..." )
		time.sleep(SLEEP_TIME)
		return find_element(xpath)
	except UnexpectedAlertPresentException:
		print( "Unexpected alert..." )
		BROWSER.refresh()
		time.sleep(SLEEP_TIME)
		return find_element(xpath)
	except SocketError:
		print( "Socket error..." )
		time.sleep(SLEEP_TIME)
		return find_element(xpath)
	return el

profile = FirefoxProfile()

#profile.set_preference('browser.helperApps.neverAsk.saveToDisk',
#                   'image/jpeg,image/png'
#                   'application/octet-stream')

mime_types = "application/pdf,application/vnd.adobe.xfdf,application/vnd.fdf,application/vnd.adobe.xdp+xml"

profile.set_preference('browser.download.manager.showWhenStarting', False)

profile.set_preference("browser.download.panel.shown", False)
profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
profile.set_preference("browser.download.folderList", 2)
profile.set_preference("browser.download.dir", tmp_dir)
profile.set_preference("plugin.disable_full_page_plugin_for_types", mime_types)
profile.set_preference("pdfjs.disabled", True)
profile.set_preference("http.response.timeout", 5)
profile.set_preference("dom.max_script_run_time", 5)

BROWSER = webdriver.Firefox(firefox_profile=profile)

# Log in
BROWSER.get("https://www.britishnewspaperarchive.co.uk/account/login")
f = open('./credentials.txt', 'r')
username, password = f.readlines()
f.close()
find_element("//input[@id='Username']").send_keys(username)
find_element("//input[@id='Password']").send_keys(password)
find_element("//input[@id='login-form-log-in']").click()
time.sleep(SLEEP_TIME)
time.sleep(SLEEP_TIME)
time.sleep(SLEEP_TIME)

# Download files
urlfile = open("urls.txt","r")
for line in urlfile.readlines():
	line = line.strip()
	publ = line.rsplit( "/", 4 )[1]
	date = line.rsplit( "/", 4 )[2]
	rand = line.rsplit( "/", 4 )[3]
	page = line.rsplit( "/", 4 )[4]
	year = date[:4]
	filename = "BL_%s_%s_%s_%s.pdf" % ( publ, date, rand, page )
	if not publ in publ_details: continue
	save_dir = publ_details[publ]
	writedir = "%s/%s" % ( save_dir.strip(), year )
	filepath = "%s/%s" % ( writedir, filename )
	tmppath = "%s/%s" % ( tmp_dir, filename )
	if not os.path.exists( writedir ):
		os.mkdir( writedir )
	if not os.path.isfile( filepath ) and not os.path.isfile( tmppath ):
		print( "Downloading %s..." % line )
		try:
			BROWSER.set_page_load_timeout(8)
			BROWSER.get(line.replace("\n",""))
		except Exception:
			print( 'time out' )
			BROWSER.execute_script("window.stop();")
	else:
		print( "Already downloaded..." )




os.system( "python2.7 3_mv_files.py" )
