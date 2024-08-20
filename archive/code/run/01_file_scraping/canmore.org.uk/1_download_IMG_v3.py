import os, time, sys
import glob
from selenium import webdriver

dirpath = "/mnt/SSD3/Dropbox/workspace/2.research/01.Sources/01.Primary/04.Visual-Sources/"


is_override = False
SLEEP_TIME = 1
BROWSER = None



def rasterise_page( url ):

	# 2021-10-12: can't get this to work

	print( "- Rasterising page..." )

	if not "http" in url: return

	dest = "%s/01_IMG/ALL.png" % ( root )
	print( dest )

	if not os.path.exists( "%s/01_IMG" % (root) ): os.mkdir( "%s/01_IMG" % (root) )

	if os.path.isfile( dest ) and not is_override: return

	cmd = "./phantomjs ./rasterize.js '%s' '%s'" % ( url, dest )
	#print( cmd )
	os.system( cmd )

	#cmd = "convert '%s' -crop 10025x4800+300+120 '%s'" % (dest,dest) # originally 13200x4800, take 3175 (need to take more because it's a wider zoom box!)
	#os.system( cmd )
	#cmd = "convert '%s' -fuzz 20%% -trim +repage '%s'" % (dest,dest) # ... ?
	#os.system( cmd )
	print( "- Done" )


def download_images( url, fpath ):

	if not os.path.exists( fpath ):
		os.mkdir( fpath )

	img_path = fpath + "/01_IMG"

	if glob.glob( "%s/canmore*.jpg" % img_path ): return

	if not os.path.exists( img_path ):
		os.mkdir( img_path )

	print( fpath )

	##Set up browser
	fp = webdriver.FirefoxProfile()
	fp.set_preference('browser.download.manager.showWhenStarting', False)
	fp.set_preference("browser.download.panel.shown", False)
	fp.set_preference('browser.helperApps.neverAsk.saveToDisk',
		               'image/jpeg,image/png,'
		               'application/octet-stream')
	fp.set_preference("browser.download.folderList", 2)
	fp.set_preference("browser.download.dir", img_path)
	BROWSER = webdriver.Firefox(firefox_profile=fp)

	# download high-res (NOT WORKING)

	#rasterise_page( url )
	#time.sleep(3)

	# download low-res

	BROWSER.get( url )
	time.sleep(5)

	closecookies_xpath = "/html/body/section/div/div/button"
	BROWSER.find_element_by_xpath(closecookies_xpath).click()
	time.sleep(1)

	window_before = BROWSER.window_handles[0]
	dl1_xpath = "/html/body/div[3]/div/div/section/div[2]/div/section/div/div[2]/div/div/div/div[1]/div[1]/div[3]/div/div/ul/li[3]/a/div"
	BROWSER.find_element_by_xpath(dl1_xpath).click()
	time.sleep(5)

	window_after = BROWSER.window_handles[1]
	BROWSER.switch_to_window( window_after )

	dl2_xpath = "/html/body/div[3]/div/div/section/div[2]/div/section/div[1]/div[3]/div/div/ul/li[1]/a/div"
	element = BROWSER.find_element_by_xpath(dl2_xpath)
	BROWSER.execute_script("arguments[0].scrollIntoView();", element)
	time.sleep(1)
	element.click()
	time.sleep(5)

	BROWSER.quit()


for root, dirs, files in os.walk( dirpath ):
	for fname in files:
		fpath = "%s/%s" % ( root, fname )

		if fname == "get.url":
			with open( fpath, "r" ) as r:
				url = r.readline().strip()
				download_images( url, root )

		if fname == "get.urls":
			with open( fpath, "r" ) as r:
				for line in r.readlines():
					if line.startswith( "https://canmore.org.uk/" ):
						url = line.strip()
						if " " in url: url = url.split( " ", 1 )[0]
						dirname = url.rsplit( "/", 1 )[1]
						download_images( url, root + "/" + dirname )
