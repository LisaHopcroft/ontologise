from selenium import webdriver
import os, time, datetime
import ezodf
from glob import glob
import re
import shutil
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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
BROWSER.get("https://secure.ancestry.co.uk/login")
BROWSER.switch_to.frame('signInFrame')
BROWSER.find_element_by_xpath("//*[@id='username']").send_keys(username)
BROWSER.find_element_by_xpath("//*[@id='password']").send_keys(password)
BROWSER.execute_script( "$('#signInBtn').click();" )
time.sleep(2) 
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
	paths = glob( dirname + "/01_IMG/*.jpg" )
	if paths:
		return len( paths )
	return 0


def get_image_id( url ):
	image_id = url[-5:]
	return int(image_id)


def get_next_url( url ):
	image_id_int = get_image_id( url )
	new_id = image_id_int + 1
	new_url = url[:-5] + str(new_id).zfill(5)
	return new_url


# can also run this code for PROB.11 wills

for (dirpath, dirnames, filenames) in os.walk("/mnt/SSD3/Dropbox/workspace/2.research/01.Sources/01.Primary/01.Manuscripts/01.Archives/02.ENGLAND & WALES/TNA, National Archives (UK)/T71, Registry of Colonial Slaves and Compensation/(001-671), Slave Registers, 1817-32/(244-250), Antigua"):
	for filename in filenames:
		if filename == "url.txt": 
			filepath = dirpath + "/" + filename
			print( "--------------------------" )
			print( filepath )

			with open(filepath, "r", encoding="utf8", errors='ignore') as f:
				url = f.readline().strip()
				print( url )

			ITEM_path = dirpath #ITEM_path = dirpath.rsplit("/",1)[0]
			
			BROWSER.get( url )
			element = WebDriverWait(BROWSER,30).until(EC.visibility_of_element_located((By.XPATH, '/html/body/div/div/div/div/div[2]/div[1]/div[2]/div[2]/div/div/span[2]')))
			num_pages = BROWSER.find_element_by_xpath('/html/body/div/div/div/div/div[2]/div[1]/div[2]/div[2]/div/div/span[2]').text
			num_pages = int( num_pages.strip() )

			num_JPGs = get_num_JPGs( ITEM_path )
			print( num_JPGs )
			print( num_pages )
			if int( num_JPGs ) >= num_pages-1:
				print( "- WARNING: Already downloaded %s images." % ( num_JPGs ) )
				continue # already downloaded, so skip...

			start_id = get_image_id( url )


			## Digital Microfilm Page
			for i in range( start_id, start_id+num_pages ):
				url_el = url.rsplit("/",1)[1]
				dl_fpath = ITEM_path+"/01_IMG/"+url_el+".jpg"

				print( url_el )
				if os.path.isfile( dl_fpath ):
					url = get_next_url( url )
					continue

				'''src = BROWSER.page_source
				text_found = re.search(r'this page is temporarily unavailable', src)
				if text_found:
					print( "- Error page - skipping" )
					url = get_next_url( url )
					continue'''

				BROWSER.get( url )
				time.sleep(3)

				#save_btn_xpath = "/html/body/div[1]/div/div/div/div[1]/div[1]/div/nav/div[1]/div/button"
				save_btn_xpath = "/html/body/div/div/div/div/div[1]/div[1]/div/nav/div[2]/div/button"
				BROWSER.find_element_by_xpath(save_btn_xpath).click()
				time.sleep(3)

				#save_btn_xpath = "/html/body/div[2]/div[2]/div/div/div[2]/div[2]/button"
				save_btn_xpath = "/html/body/div[2]/div[2]/div/div/div[2]/div[2]/button"
				BROWSER.find_element_by_xpath(save_btn_xpath).click()
				time.sleep(3)
				
				url = get_next_url( url )


			dl_dir = '/home/michael/Downloads'

			## Move the files (doing this seperately now)
			url = start_url
			for i in range( start_id, start_id+num_pages ):
				url_el = url.rsplit("/",1)[1]
				dl_fpath = dl_dir+"/"+url_el+".jpg"
				dest_fpath = ITEM_path+"/01_IMG/"+url_el+".jpg"

				if not os.path.exists( ITEM_path + "/01_IMG" ):
					os.makedirs( ITEM_path + "/01_IMG" )

				if os.path.isfile( dl_fpath ):
					shutil.move( dl_fpath, dest_fpath ) # dl_name) # changed to url_el, rather than guessing the last downloaded file

				url = get_next_url( url )
