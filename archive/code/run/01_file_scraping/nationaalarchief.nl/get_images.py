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

SLEEP_TIME = 2
fp = webdriver.FirefoxProfile()
fp.set_preference("browser.download.panel.shown", False)
fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "image/jpeg")
fp.set_preference("browser.download.dir", dl_dir)
BROWSER = webdriver.Firefox(firefox_profile=fp)


def get_approx_path_if_exists( wpath ):
	if len( glob.glob( wpath + ", *" ) ) > 0:
		return( glob.glob( wpath + ", *" )[0] )
	return wpath


def hover(browser, xpath):
    element_to_hover_over = browser.find_element_by_xpath(xpath)
    hover = ActionChains(browser).move_to_element(element_to_hover_over)
    hover.perform()


def get_images( url, root ):

	print( root )
	glob_root = root.replace( "[","<" ).replace( "]",">" )
	glob_root = glob_root.replace( "<","[[]" ).replace( ">","[]]" )
	#if len( glob.glob( glob_root+"/01_IMG/*.jpg" ) ) > 0: return # hack to avoid getting stuff I already have...

	BROWSER.get( url )

	grp = url.split( "https://www.nationaalarchief.nl/en/research/archive/", 1 )[1].split( "/inventory?", 1 )[0]

	# get the number of pages:
	num_pages_els = BROWSER.find_elements_by_xpath("//*[@id=\"block-natarch-content\"]/div[2]/div[2]/div/div/div[2]/p/em[1]")
	if len( num_pages_els ) == 0: 
		num_pages = "1"
	else:
		num_pages = num_pages_els[0].text
	print( "- pages: " + num_pages )

	ref = url.split( "inventarisnr=", 1 )[1].split( "&activeTab", 1 )[0]
	print( "ref: " + ref )
	if "&scans-inventarispagina=" in ref:
		ref = ref.rsplit( "&scans-inventarispagina=", 1 )[0]

	if len( glob.glob( root+"/01_IMG/@original/*.jpg" ) ) >= int(num_pages): 
		print( "*ALREADY HAVE ALL IMAGES*" )
		return

	for i in range( 1, int(num_pages)+1 ): # can hack this if want a specific page range

		#root = get_approx_path_if_exists( root ) # does this work?

		if int(num_pages) == 1:
			if len( glob.glob( glob_root+"/01_IMG/*.jpg" ) ) > 0 or len( glob.glob( glob_root+"/01_IMG/@original/*.jpg" ) ) > 0: 
				print( "- already got this" )
				continue
		else:
			if len( glob.glob( glob_root+"/01_IMG/*%s.jpg" % str(i).zfill(4) ) ) > 0 or len( glob.glob( glob_root+"/01_IMG/@original/*%s.jpg" % str(i).zfill(4) ) ) > 0: 
				print( "- already got this" )
				continue

		page_url = url
		page_url = page_url.replace("activeTab=gahetnascans","activeTab=gahetnascan")
		page_url = page_url.replace("#tab-heading","")
		if int(num_pages) == 1:
			page_url = page_url + "&afbeelding=NL-HaNA_%s_%s" % ( grp, ref )
		else:
			page_url = page_url + "&afbeelding=NL-HaNA_%s_%s_%s" % ( grp, ref, str(i).zfill(4) )

		#print( "URL1: " + page_url )

		BROWSER.get( page_url )

		time.sleep( 4 )

		# download
		dl_els = BROWSER.find_elements_by_xpath( "//*[@id=\"block-natarch-content\"]/div[2]/div[2]/div/div/div[4]/a" )
		if len( dl_els ) < 1: continue
		dl_link = dl_els[0]
		href = dl_link.get_attribute("href")
		#print( "URL2: " + href )

		try:
			BROWSER.set_page_load_timeout(1)
			BROWSER.get( href )
			BROWSER.set_page_load_timeout(10)
		except TimeoutException as ex:
			BROWSER.set_page_load_timeout(10)
			pass

		time.sleep( 4 )

		'''
		try: 
			BROWSER.switch_to_alert().accept()
		except NoAlertPresentException: 
			pass
		'''

		#print( "go back" )
		BROWSER.execute_script("window.history.go(-1)")

		time.sleep( 4 ) #100

		if len(BROWSER.find_elements_by_xpath( "/html/body/div[2]/div[2]/div/a[1]" ))>0:
			BROWSER.find_elements_by_xpath( "/html/body/div[2]/div[2]/div/a[1]" )[0].click()


#for root, dirs, files in os.walk( "/media/michael/Files/Dropbox/workspace/2.research/01.Primary/03.Maps etc/00.WWW/NAN, Nationaal Archief (NED)" ):
for root, dirs, files in os.walk( "/media/michael/SSD3/Dropbox/workspace/2.research/01.Primary/01.Manuscripts/00.WWW/NL-HaNA, Nationaal Archief/1.05.21, Dutch Series Guyana/(4), Berbice/(4.1), Court of Policy & Criminal Justice/(4), Letters and letter books, 1747-1817" ):
	for fname in files:
		if fname == "get.url":
			fpath = "%s/%s" % ( root, fname )
			print( fpath )
			with open( fpath, "r" ) as r:
				lines = r.readlines()
				if len(lines) > 0:
					line = lines[0].strip()
					get_images( line, root )
