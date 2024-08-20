from selenium import webdriver
import os, time, datetime, csv
from bs4 import BeautifulSoup as BS
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys  
import datetime
import glob

reload(sys)  
sys.setdefaultencoding('utf8')
sys.setrecursionlimit(10000)

SLEEP_TIME = 3
BROWSER = None
GOTO_URL = None
delay = 1

fp = webdriver.FirefoxProfile()
adblockfile = '../adblock_plus-2.9.1-an+fx+sm+tb.xpi'
fp.add_extension (adblockfile)
fp.set_preference('browser.helperApps.neverAsk.saveToDisk',
                   	"image/jpeg, image/png, application/octet-stream, application/zip, application/x-zip, application/x-zip-compressed")


BROWSER 	= webdriver.Firefox(firefox_profile=fp)

for root, dirs, files in os.walk( "/media/michael/Files/Dropbox/workspace/2.research" ):
	for fname in files:
		if fname == "dload.urls":
			print fname
			filepath = "%s/%s" % (root, fname)
			with open( filepath, "r" ) as r:
				for line in r.readlines():
					print line.strip()
					if line.startswith( "http://jcb.lunaimaging.com" ):
						BROWSER.get( line )
						el 		= BROWSER.find_element_by_xpath( "//*[@id='MediaInformation']/div[2]/table/tbody/tr[5]/td/div[1]" )
						acc_num = el.text

						el 		= BROWSER.find_element_by_xpath( ".//*[@id='MediaInformation']/div[2]/table/tbody/tr[7]/td/div[1]" )
						filenum	= el.text


						print acc_num
						new_dirpath = os.path.dirname( filepath ) + "/JCB." + acc_num
						if not os.path.exists( new_dirpath ):
							os.mkdir( new_dirpath )

						dest_path = "%s/%s.zip" % (new_dirpath, filenum)

						if os.path.exists( dest_path ):
							continue # already download...

						# download
						el 		= BROWSER.find_element_by_xpath( "//*[@id='ExportButton']" )
						el.click()
						el.click()

						time.sleep( SLEEP_TIME )

						if BROWSER.find_elements_by_xpath( "//*[@id='ExportResolution6']" ):
							el		= BROWSER.find_element_by_xpath( "//*[@id='ExportResolution6']" )
						else:
							el		= BROWSER.find_element_by_xpath( "//*[@id='ExportResolution5']" )
						el.click()

						time.sleep( SLEEP_TIME )
						time.sleep( SLEEP_TIME )
						time.sleep( SLEEP_TIME )
						time.sleep( SLEEP_TIME )
						#time.sleep( SLEEP_TIME )
						#time.sleep( SLEEP_TIME )

						metapath = new_dirpath + "/%s.html" % filenum
						with open( metapath, "w" ) as w:
							w.write( BROWSER.page_source )

						# do stuff with the file
						filelist = glob.glob( "/home/michael/Downloads/*" )
						time_sorted_list = sorted(filelist, key=os.path.getmtime)
						file_name = time_sorted_list[len(time_sorted_list)-1]
						print file_name

						os.system( "mv '%s' '%s'" % (file_name, dest_path) )
