import os, time, datetime, csv
from bs4 import BeautifulSoup as BS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
import sys  
import datetime
import urllib



run_dir = "/mnt/SSD3/Dropbox/workspace/2.research/01.Sources/01.Primary/01.Manuscripts/01.Archives/01.SCOTLAND/NRS, National Records of Scotland/CH, Church Records/2, Kirk Session/294, Presbytery of Paisley"
	
fp = webdriver.FirefoxProfile()
BROWSER = webdriver.Firefox(firefox_profile=fp)

# ---------------------------------------------------- #
# STEP 1: Log in

login_url 	= "https://www.scotlandspeople.gov.uk"
username 	= "michael.hopcroft@gmail.com"
password 	= "-3a46SPbbf9/"

BROWSER.get( login_url )
time.sleep(2)
BROWSER.find_element_by_xpath( "/html/body/div[4]/div/div/div[2]/button[1]" ).click() # cookie consent
time.sleep(2)
BROWSER.find_element_by_xpath( "//*[@id=\"mainHeader\"]/div/div/label/a[1]" ).click()
time.sleep(4)
BROWSER.find_element_by_xpath( "//*[@id=\"edit-name\"]" ).send_keys(username)
BROWSER.find_element_by_xpath( "//*[@id=\"edit-pass\"]" ).send_keys(password)
#WebDriverWait(BROWSER, 5).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR,"iframe[name^='a-'][src^='https://www.google.com/recaptcha/api2/anchor?']")))
#time.sleep(3)
#element = BROWSER.find_element_by_xpath( "//span[@class='recaptcha-checkbox goog-inline-block recaptcha-checkbox-unchecked rc-anchor-checkbox']/div[@class='recaptcha-checkbox-checkmark']" )
#BROWSER.execute_script("arguments[0].click();", element)
#time.sleep(3)
#BROWSER.switch_to.default_content()

# Have to manually do some captcha stuff and then click the log in button...
wait = WebDriverWait(BROWSER, 60)
element = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id=\"block-system-user-menu\"]" )))


for root, dirs, files in os.walk( run_dir ):
	for fname in files:
		if fname == "VV_url.txt":
			with open( "%s/%s" % (root, fname), "r" ) as r:
				url = r.readline()

				# ---------------------------------------------------- #
				# STEP 2: Save records

				BROWSER.get( url )
				time.sleep(4)
				prev_image_num = ""

				while True:
					image_num = BROWSER.find_element_by_xpath("//*[@id=\"edit-image-number\"]").get_attribute('value')
					if image_num == prev_image_num: break
					
					

					# preset 1: landscape
					canvas_height = "1600" #"1350" # remember to go F11
					is_fit_height = True

					# preset 2: portrait
					#canvas_height = "2150" # fine tune this
					#is_fit_height = False

					BROWSER.execute_script( 'document.styleSheets[0].insertRule("#watermark_image{ display: none !important; }", 0 )' )
					BROWSER.execute_script( 'document.styleSheets[0].insertRule("#water-mark{ display: none !important; }", 0 )' )
					BROWSER.execute_script( 'document.styleSheets[0].insertRule("#water-mark-center{ display: none !important; }", 0 )' )
					BROWSER.execute_script( 'document.styleSheets[0].insertRule("#water-mark-bottom{ display: none !important; }", 0 )' )
					BROWSER.execute_script( 'document.styleSheets[0].insertRule(".container-fluid{ min-width: 100% !important; }", 0 )' )
					BROWSER.execute_script( 'document.styleSheets[0].insertRule(".container-fluid{ max-width: 100% !important; }", 0 )' )
					BROWSER.execute_script( 'document.styleSheets[0].insertRule(".volume-images-nav{ display: none !important; }", 0 )' )
					BROWSER.execute_script( 'document.styleSheets[0].insertRule("#holder{ height: %spx !important; }", 0 )' % canvas_height )
					BROWSER.execute_script( 'document.styleSheets[0].insertRule("header{ display: none !important; }", 0 )' )
					BROWSER.execute_script( 'document.styleSheets[0].insertRule(".region-promotional{ display: none !important; }", 0 )' )
					BROWSER.execute_script( 'document.styleSheets[0].insertRule("#waypointing{ display: none !important; }", 0 )' )
					
					time.sleep(3)

					if is_fit_height:
						BROWSER.find_element_by_xpath("//*[@id=\"filters\"]/div[1]/ul/li[6]/a").click()
					else:
						BROWSER.find_element_by_xpath("//*[@id=\"filters\"]/div[1]/ul/li[7]/a").click()
					
					time.sleep(3)
					
					BROWSER.execute_script("window.scrollBy(0, 220);")

					time.sleep(3)

					BROWSER.save_screenshot("%s/01_IMG/%s.png" % (root, image_num.zfill(4)))

					BROWSER.find_element_by_xpath("//*[@id=\"filters\"]/div[1]/ul/li[3]/a").click()
					time.sleep(5)

					prev_image_num = image_num
