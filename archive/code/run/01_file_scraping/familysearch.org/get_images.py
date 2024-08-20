import selenium
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException 
import os, time, datetime
import ezodf
from glob import glob
import re
import shutil
import random


SLEEP_TIME = 1
BROWSER = None
FILTER_URL = None


print( "============================" )
print( "== Run started at ", datetime.datetime.now() )
print( "============================" )


f = open('credentials.txt', 'r')
username, password = f.readlines()
f.close()

##----------------------------------------##

##Set up browser

fp = webdriver.FirefoxProfile()
fp.set_preference('browser.helperApps.neverAsk.saveToDisk',
                   'image/jpeg,image/png,'
                   'application/octet-stream')
BROWSER = webdriver.Firefox(firefox_profile=fp)

##----------------------------------------##

##Log in Page

print( "Logging in..." )
BROWSER.get("https://ident.familysearch.org/cis-web/oauth2/v3/authorization?client_secret=au4xhX6Oji8b6ZACMZ%2BxF%2FBwjP0BLQk7nnboc5Zs5bWHFltqIGZf9KLK65nHRfAUlPvN8blZVIeUm%2FcYKk3oXUTnytGqPQSLyppVspH3rWAhVKtiBamRG%2BMIP1flffFQ6yI4nlHUDo56XwrrXIBV%2BNUYySmse47P1aCKY1MSzTlPLtvdMRVs67OpmuGhQJM%2FfWYSwuy34TIRCAXm5alIWgwH6yaJTsJh%2FuYEyaUnaFIIwnXHt5JfA2ZeXZc0zIK4EVFwPBiLwZbGp5N143yqBmgwOJXtFZEIQoeoJNkjx7gghgs5AbDPQ5%2BePbLcJBrCTPyFBesRpDsu0%2ByEjPTeiQ%3D%3D&response_type=code&redirect_uri=https%3A%2F%2Fwww.familysearch.org%2Fauth%2Ffamilysearch%2Fcallback&state=%2F&client_id=3Z3L-Z4GK-J7ZS-YT3Z-Q4KY-YN66-ZX5K-176R")
BROWSER.find_element_by_xpath("//*[@id='userName']").send_keys(username)
BROWSER.find_element_by_xpath("//*[@id='password']").send_keys(password)
BROWSER.find_element_by_xpath("//*[@id='login']").click()
time.sleep(SLEEP_TIME) 
time.sleep(SLEEP_TIME) 
print( "Logged in..." )

##----------------------------------------##

BROWSER.switch_to_default_content()


def file_len(fname):
	i = 0
	for l in enumerate(f):
		i += 1
	f.seek(0)
	return i + 1


def get_num_JPGs( dirname ):
	paths1 = glob( dirname + "/01_IMG/@original/*.jpg" )
	paths2 = glob( dirname + "/01_IMG/@original/*.png" )
	if paths1 or paths2:
		return len( paths1 ) + len( paths2 )
	return 0


for (dirpath, dirnames, filenames) in os.walk("/media/michael/SSD3/Dropbox/workspace/2.research/01.Material/01.Primary/01.Manuscripts/00.WWW/FS, FamilySearch/359031, Cairn of Lochwinyoch matters, 1827-37/1419528, Vol 38 [...]"):
	for filename in filenames:
		if filename == "FS-GET.txt": 
			filepath = dirpath + "/" + filename
			print( "--------------------------" )
			print( filepath )

			with open(filepath, "r", encoding="utf8", errors='ignore') as f:
				start_url = f.readline()
				start_url = start_url.strip()
				print( start_url )

			url = start_url
			print( url )

			ITEM_path = dirpath
			if not os.path.exists( ITEM_path + "/01_IMG/@original" ):
				os.makedirs( ITEM_path + "/01_IMG" )
				os.makedirs( ITEM_path + "/01_IMG/@original" )

			BROWSER.get( url )
			time.sleep(SLEEP_TIME)
			time.sleep(SLEEP_TIME)

			# close the cookie popup
			try:
				BROWSER.find_element_by_xpath('/html/body/div[8]/div[1]/div/div[2]/div[2]/a[1]').click()
			except selenium.common.exceptions.NoSuchElementException:
				print( "- Cookie popup: No such element" )

			num_pages = BROWSER.find_element_by_xpath('/html/body/div[1]/main/div[1]/fs-film-viewer/div/div[1]/div[2]/div[3]/div[1]/span[2]/label[2]').text.replace("of ","")
			print( num_pages )
			num_pages = int( num_pages.strip() )

			num_JPGs = get_num_JPGs( ITEM_path )
			print( num_JPGs )
			print( num_pages )
			if int( num_JPGs ) >= num_pages:
				print( "- WARNING: Already downloaded %s images." % ( num_JPGs ) )
				continue

			dl_fpath = "/home/michael/Downloads/record-image_undefined.jpg"
			BROWSER.find_element_by_xpath('//*[@id="ImageViewer"]/div[2]/div[2]/ul/li[5]/button').click() # full screen

			start_page = 1
			if "?i=" in start_url:
				start_page = int(start_url.rsplit("?i=",1)[1])

			## Download images
			for i in range( start_page, num_pages ):
				
				dest_fname = str(i).zfill(4)
				dest_fpath = "%s/01_IMG/@original/%s.png" % (ITEM_path, dest_fname)
				print( dest_fpath )

				if os.path.isfile( dest_fpath ) or os.path.isfile( dest_fpath.replace(".png",".jpg" ) ):
					BROWSER.find_element_by_xpath('//*[@id="ImageViewer"]/div[2]/div[3]/div[1]/span[3]').click() # move to next page
					print( "- skipping..." )
					continue


				# save by screenshot (because download is throttled)

				## if single page button appears on the page then we've zoomed out too much... go back to single page
				try:
					BROWSER.find_element_by_xpath('/html/body/div/div[2]/div[2]/ul/li[3]/button').click()
					time.sleep( random.uniform(.5, 1) )
				except selenium.common.exceptions.ElementNotInteractableException:
					pass

				BROWSER.find_element_by_xpath('//*[@id="ImageViewer"]/div[4]/fs-combo-record-list/div[1]/div/div[1]') # full screen
				time.sleep( random.uniform(.5, 1) )
				BROWSER.find_element_by_xpath('/html/body/div/div[2]/div[2]/ul/li[4]/button').click() # multi page
				time.sleep( random.uniform(.5, 1) )
				BROWSER.find_element_by_xpath('/html/body/div/div[2]/div[2]/ul/li[3]/button').click() # single page
				time.sleep( random.uniform(.5, 1) )
				BROWSER.find_element_by_xpath('//*[@id="ImageViewer"]/div[2]/div[2]/ul/li[2]/button').click() # zoom out
				time.sleep( random.uniform(.5, 1) )


				## if single page button appears on the page then we've zoomed out too much... go back to single page
				try:
					BROWSER.find_element_by_xpath('/html/body/div/div[2]/div[2]/ul/li[3]/button').click()
				except selenium.common.exceptions.ElementNotInteractableException:
					pass

				time.sleep( random.uniform(1, 2) )
				BROWSER.save_screenshot( dest_fpath )
				time.sleep( random.uniform(.5, 1) )

				BROWSER.find_element_by_xpath('//*[@id="ImageViewer"]/div[2]/div[3]/div[1]/span[3]').click() # move to next page
				time.sleep( random.uniform(.5, 1) )


				'''
				# save by download button

				dest_fpath = "%s/01_IMG/@original/%s.jpg" % (ITEM_path, dest_fname)

				BROWSER.find_element_by_xpath('//*[@id="saveLi"]/a').click()

				time.sleep(SLEEP_TIME)
				time.sleep(SLEEP_TIME)
				time.sleep(SLEEP_TIME)
				time.sleep(SLEEP_TIME)
				time.sleep(SLEEP_TIME)
				time.sleep(SLEEP_TIME)

				if os.path.isfile( dl_fpath ):
					shutil.move( dl_fpath, dest_fpath )

				time.sleep(SLEEP_TIME)

				BROWSER.find_element_by_xpath('//*[@id="ImageViewer"]/div[2]/div[3]/div[1]/span[3]').click() # move to next page
				'''
