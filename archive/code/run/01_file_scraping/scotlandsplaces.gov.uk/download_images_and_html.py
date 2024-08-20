import os, time, datetime, csv
from bs4 import BeautifulSoup as BS
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys  
import datetime
import urllib


SLEEP_TIME = 1
fp = webdriver.FirefoxProfile()
BROWSER = webdriver.Firefox(firefox_profile=fp)


run_dir = "/mnt/SSD3/Dropbox/workspace/2.research/01.Sources/01.Primary/01.Manuscripts/00.WWW/SP, Scotlands Places/E326.09, Horse tax, 1785-98/02, L-W"


def download_page(BROWSER, root):

	# get details

	zoomify_url = ""

	source = BROWSER.page_source#.encode('ascii', 'ignore'):
	lines = source.split("\n")
	for line in lines:
		if "sp_zoomify_init('/proxy.php?url=" in line: zoomify_url = line.split("sp_zoomify_init('/proxy.php?url=")[1].split("/'",1)[0]
	img_id = zoomify_url.rsplit("/",1)[1]
	print( zoomify_url )
	print( img_id )

	# download image

	if not os.path.exists(root+"/01_IMG"): os.mkdir(root+"/01_IMG")
	dload_path = "%s/01_IMG/%s.jpg" % ( root, img_id )
	cmd = "python3 ../\(generic\)/dezoomify/dezoomify.py '%s' '%s' -b" % ( zoomify_url, dload_path )
	os.system( cmd )

	#download html

	if not os.path.exists(root+"/00_HTML"): os.mkdir(root+"/00_HTML")
	with open(root+"/00_HTML/"+img_id+".html", "w") as f:
		f.write(BROWSER.page_source)#.encode('ascii', 'ignore')

	time.sleep(SLEEP_TIME) 

	#proceed to next page
	next_elements = BROWSER.find_elements_by_xpath("//*[@id=\"sp-zoomify-sequence\"]/div/div[2]/a/span")
	if next_elements: 
		next_elements[0].click()
	else:
		return

	return download_page(BROWSER, root)

for root, dirs, files in os.walk( run_dir ):
	for fname in files:
		if fname=="GET.urls":
			with open( root + "/" + fname, "r" ) as r:
				for line in r.readlines():
					if line.startswith("#"): continue
					URL = line.strip()
					if not URL.endswith("/1"): URL = URL + "/1"
					BROWSER.get( URL )
					download_page( BROWSER, root )
					os.system( "mv '%s' '%s'" % ( root + "/" + fname, root + "/#" + fname ) )
