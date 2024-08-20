import os, time, sys
from selenium import webdriver

dirpath = "/media/michael/SSD3/Dropbox/workspace/2.research/01.Material/01.Primary/01.Manuscripts/00.WWW/BL, British Library/EAP.794, Nevis/1, Eastern Caribbean Court/10, Plans and maps, 1888-1974"


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
	if not "http" in url: return

	dlfile = url.rsplit("&cv=",1)[1].split("&xywh=",1)[0]
	dest = "%s/01_IMG/%s.png" % ( root, dlfile )

	if not os.path.exists( "%s/01_IMG" % (root) ): os.mkdir( "%s/01_IMG" % (root) )

	if os.path.isfile( dest ) and not is_override: return

	cmd = "./phantomjs ./rasterize.js '%s' '%s'" % ( url, dest )
	#print( cmd )
	os.system( cmd )

	#print( "- Shaving and trimming" )
	cmd = "convert '%s' -crop 10025x4800+300+120 '%s'" % (dest,dest) # originally 13200x4800, take 3175 (need to take more because it's a wider zoom box!)
	#cmd = "convert '%s' -crop 2800x2400+300+120 '%s'" % (dest,dest) # originally 4800x2400, take 2000 off the right
	os.system( cmd )
	cmd = "convert '%s' -fuzz 20%% -trim +repage '%s'" % (dest,dest) # ... ?
	os.system( cmd )


for root, dirs, files in os.walk( dirpath ):
	for fname in files:
		if fname == "get.url":
			with open( "%s/%s" % (root,fname), "r" ) as r:
				url = r.readline().strip() 

				BROWSER.get( url )
				time.sleep(2)

				if not "&xywh=" in url:
					BROWSER.find_element_by_xpath("//*[@id=\"block-system-main\"]/div/div/div[2]/div[2]/div/a").click()
					time.sleep(2)

				while True:
					try:
						print( BROWSER.current_url )
						rasterise_page( BROWSER.current_url )
						iframes = BROWSER.find_elements_by_tag_name("iframe")
						for iframe in iframes:
							if iframe.get_attribute("id").startswith( "easyXDM_"):
								BROWSER.switch_to.frame( iframe )
								break
						BROWSER.find_element_by_xpath("/html/body/div/div[2]/div[1]/div[2]/div[1]/div/div[3]/div/div").click()
						time.sleep(2)
					except:
						type, value, traceback = sys.exc_info()
						print( value )
						break
