import os, time, sys
from selenium import webdriver

dirpath = "/mnt/SSD3/Dropbox/workspace/2.research/01.Sources/01.Primary/04.Visual-Sources/(A), Illustrations/00.WWW/HES, Historic Environment Scotland re. Governor etc"


is_override = False
SLEEP_TIME = 1
BROWSER = None

##Set up browser
fp = webdriver.FirefoxProfile()
fp.set_preference('browser.helperApps.neverAsk.saveToDisk',
                   'image/jpeg,image/png,'
                   'application/octet-stream')
BROWSER = webdriver.Firefox(firefox_profile=fp)


def rasterise_page( url ):
	print( "- Rasterising page..." )
	if not "http" in url: return

	dlfile = url.rsplit("&cv=",1)[1].split("&xywh=",1)[0]
	dest = "%s/01_IMG/%s.png" % ( root, dlfile.zfill(4) )

	if not os.path.exists( "%s/01_IMG" % (root) ): os.mkdir( "%s/01_IMG" % (root) )

	if os.path.isfile( dest ) and not is_override: return

	cmd = "./phantomjs ./rasterize.js '%s' '%s'" % ( url, dest )
	#print( cmd )
	os.system( cmd )

	cmd = "convert '%s' -crop 10025x4800+300+120 '%s'" % (dest,dest) # originally 13200x4800, take 3175 (need to take more because it's a wider zoom box!)
	os.system( cmd )
	cmd = "convert '%s' -fuzz 20%% -trim +repage '%s'" % (dest,dest) # ... ?
	os.system( cmd )
	print( "- Done" )


for root, dirs, files in os.walk( dirpath ):
	for fname in files:
		if fname == "get.url":
			with open( "%s/%s" % (root,fname), "r" ) as r:
				url = r.readline().strip()

				BROWSER.get( url )
				time.sleep(5)

				if not "&xywh=" in url:
					open_images_xpath = "/html/body/div[2]/div/div[2]/div[2]/div[1]/div/div/div[2]/div/div/div[3]/a/span[2]"
					BROWSER.find_element_by_xpath(open_images_xpath).click()
					time.sleep(5)

				while True:
					try:
						print( BROWSER.current_url )
						rasterise_page( BROWSER.current_url )
						iframes = BROWSER.find_elements_by_tag_name("iframe")
						for iframe in iframes:
							if iframe.get_attribute("id").startswith( "easyXDM_"):
								BROWSER.switch_to.frame( iframe )
								break

						next_page_xpath = "/html/body/div/div[2]/div[1]/div[2]/div[1]/div/div[3]/div/div"
						BROWSER.find_element_by_xpath(next_page_xpath).click()
						time.sleep(2)
					except:
						type, value, traceback = sys.exc_info()
						print( value )
						break
