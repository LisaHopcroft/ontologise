#from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
import os, time, datetime
import urllib
import glob
import shutil
import os.path
from selenium.common.exceptions import NoSuchElementException


## USAGE: Download html 'item page' as get.html, place in relevant folder, then run this script...


SLEEP_TIME = 2
BROWSER = None
FILTER_URL = None


def find_element(xpath):
  return BROWSER.find_element_by_xpath(xpath)


fp = webdriver.FirefoxProfile()
fp.set_preference('browser.helperApps.neverAsk.saveToDisk',
                   'image/jpeg,image/png,'
                   'application/octet-stream')
BROWSER = webdriver.Firefox(firefox_profile=fp)

run_dir = "/mnt/SSD3/Dropbox/workspace/2.research/01.Sources/01.Primary/01.Manuscripts/01.Archives/04.USA/SCR, Schomburg Centre for Research/SCMG 383"

for root, dirs, files in os.walk( run_dir ):
	for fname in files:
		if fname == 'url.txt':
			with open( "%s/%s" % ( root, fname ), "r" ) as r: url = r.readline()
			print( url )
			print( root )
			BROWSER.get( url )

			try:			
				while True:

					# download
							
					time.sleep( SLEEP_TIME )
					time.sleep( SLEEP_TIME )
					time.sleep( SLEEP_TIME )

					el = BROWSER.find_element_by_xpath( "/html/body/div[2]/div[5]/div/div[2]/div/div[2]/div[1]/div[1]/div[4]/a" )
					el.click()

					# move to next page
					
					time.sleep( SLEEP_TIME )
					time.sleep( SLEEP_TIME )
					time.sleep( SLEEP_TIME )
				
					el = BROWSER.find_element_by_xpath( "/html/body/div[2]/div[4]/div[3]/div[2]/div/div/ul/li[@class='current']/following-sibling::li/a" )
					el.click()
			except:
				print( "Reached end of file" )
			
			# tidy up
			
			time.sleep( SLEEP_TIME )
			time.sleep( SLEEP_TIME )
			time.sleep( SLEEP_TIME )
			time.sleep( SLEEP_TIME )
			
			cmd = "mv /home/michael/Downloads/*.jpg \"%s\"" % ( root + "/01_IMG" )
			if not os.path.exists( root + "/01_IMG" ): os.makedirs( root + "/01_IMG" )
			os.system( cmd )
