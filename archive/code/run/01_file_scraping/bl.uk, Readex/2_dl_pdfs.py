from selenium import webdriver
import os, time, datetime, csv
import glob
from bs4 import BeautifulSoup as BS
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import datetime
import string
import random

SLEEP_TIME = 3
BROWSER = None
GOTO_URL = None
delay = 1

mime_types = "application/pdf,application/vnd.adobe.xfdf,application/vnd.fdf,application/vnd.adobe.xdp+xml"
fp = webdriver.FirefoxProfile()
fp.set_preference("browser.helperApps.neverAsk.saveToDisk", mime_types)
fp.set_preference("plugin.disable_full_page_plugin_for_types", mime_types)
fp.set_preference("pdfjs.disabled", True)

BROWSER 	= webdriver.Firefox(firefox_profile=fp)


###########################################################
#
# When you see this message, it means you have exceeded downloading the allowed 350MB in 30 minute server policy restriction (remember most PDFs in our electronic databases or journals are about 2-4 MB each, which rougly equates to 75 articles being downloaded in a 30 minute period). If you wait for about 15 minutes though, your connection should be restored. 
#
# > MH: Suspension actually lasts an hour?
#
###########################################################


#credentials
username = "laird18"
password = "3a46BLbbf9"


month_nums = {
	"January": "01",
	"February": "02",
	"March": "03",
	"April": "04",
	"May": "05",
	"June": "06",
	"July": "07",
	"August": "08",
	"September": "09",
	"October": "10",
	"November": "11",
	"December": "12",
}


for root, dirs, files in os.walk( "/media/michael/Files/Dropbox/workspace/2.research/01.Primary/02.Publications/(B), Newspapers" ):
	for fname in files:
		if fname == "readex.urls":
			with open( "%s/%s" % ( root, fname ), "r" ) as r:
				for line in r.readlines():

					url = line.strip()

					print( url )
					if url.strip() == "": continue

					if not "issue_id=" in url: continue

					issue_id = url.split( "issue_id=", 1 )[1]
					with open( "./mv.tsv", "r" ) as r:
						if issue_id in r.read():
							print( "- issue already downloaded" )
							continue

					BROWSER.get( url )
					time.sleep( float(5) + random.uniform(0, 5) )

					if "Log in to continue" in BROWSER.page_source:
						print( "- logging in..." )

						el 	= BROWSER.find_element_by_xpath( ".//*[@id='username']" )
						el.send_keys( username )
					
						el 	= BROWSER.find_element_by_xpath( ".//*[@id='password']" )
						el.send_keys( password )

						el	= BROWSER.find_element_by_xpath( ".//*[@id='btnLoginReg']" )
						el.click()

						time.sleep( float(10) + random.uniform(0, 5) )
					else:
						print( "- (no log in required)" )
 
					el 			= BROWSER.find_element_by_xpath( ".//*[@id='citDate']/nobr" )
					date_txt	= el.text
					mmdd		= date_txt.split(", ",1)[0]
					year		= date_txt.split(", ",1)[1]
					mm			= mmdd.split(" ",1)[0]
					dd			= mmdd.split(" ",1)[1]
					for key, val in month_nums.items():
						mm = mm.replace( key, val )
					date_txt	= "%s%s%s" % ( year, mm, dd.zfill(2) )

					el 			= BROWSER.find_element_by_xpath( ".//*[@id='tileViewer_toc']/div[2]/div/a[1]" )
					url			= el.get_attribute( "href" )
					BROWSER.get( url )

					issue = url.split( "&f_issue=" )[1].split( "&f_page=" )[0]

					num_pages_el = BROWSER.find_element_by_xpath( "//*[@id='multipagePDF']/div[3]/ul/li[2]" )
					num_pages = num_pages_el.text
					num_pages = int( num_pages.replace("(","").replace(")","").replace(" Pages","").rsplit(" ",1)[1] )


					el 	= BROWSER.find_element_by_xpath( "/html/body/div[2]/div[5]/div[3]/ul/li[2]/a" )
					el.click()

					with open( "./mv.tsv", "a" ) as a:
						a.write( "%s\t%s/00_PDF/%s/%s.pdf\n" % ( issue, root, year, date_txt ) )

					time.sleep( num_pages*(50) + random.uniform(0, 10) ) # enforced wait, to avoid going over ~10MB per min limit (350MB per 30 mins)
