from selenium import webdriver
import os, time, datetime, csv
import glob
from bs4 import BeautifulSoup as BS
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import datetime
import string
import random
from selenium.webdriver.common.keys import Keys

BROWSER = webdriver.Firefox()
BROWSER.set_window_position(0, 0)
#BROWSER.set_window_size(1440, 2560)
BROWSER.set_window_size(2560, 1440)


def toggle_fullscreen( BROWSER ):
	el	= BROWSER.find_element_by_xpath( "//*[@id=\"toolbar\"]/span/span[5]/div" )
	el.click()
	time.sleep( random.uniform(1, 2) )


for root, dirs, files in os.walk( "/media/michael/Files/Dropbox/workspace/2.research" ):
	for fname in files:
		if fname == "googlenews.urls":
			with open( "%s/%s" % ( root, fname ), "r" ) as r:
				i = 0
				for line in r.readlines():
					url = line.strip()
					dest = url.split("&dat=",1)[1].split("&printsec=",1)[0]

					if os.path.exists( dest+"-4_1.png" ) and os.path.exists( dest+"-4_2.png" ) and os.path.exists( dest+"-4_3.png" ): continue

					BROWSER.get( url )

					try:
						element = WebDriverWait(BROWSER, 1000000000).until(
							EC.presence_of_element_located((By.ID, "jtp_form"))
						)
					finally:

						print( dest )

						num_pages_txt = BROWSER.find_element_by_xpath( "//*[@id=\"jtp_form\"]" ).text
						num_pages = num_pages_txt.replace("&nbsp;","").split("of ",1)[1]
						num_pages = num_pages.strip()
						print( num_pages )
						if num_pages == "4":
							x_offset = 90
						else:
							x_offset = 0

						# zoom-in
						el 	= BROWSER.find_element_by_xpath( "//*[@id=\"toolbar\"]/span/span[3]/div" )
						el.click()
						time.sleep( random.uniform(1, 2) )
						el.click()
						time.sleep( random.uniform(1, 2) )
						el.click()
						time.sleep( random.uniform(1, 2) )
						el.click()
						time.sleep( random.uniform(1, 2) )
						el.click()
						time.sleep( random.uniform(1, 2) )

						# zoom-out
						#el	= BROWSER.find_element_by_xpath( "/html/body/table/tbody/tr[1]/td[1]/table/tbody/tr/td[2]/div/span/span[2]/div" ) 
						#el.click()	
						#time.sleep( random.uniform(1, 4) )

						# ---------------------------------------------------------- #

						# move to page 4
						el 	= BROWSER.find_element_by_xpath( "//*[@id=\"jtp\"]" )
						el.send_keys( Keys.BACKSPACE )
						el.send_keys( "4" )
						el.send_keys( Keys.RETURN )
						time.sleep( random.uniform(1, 4) )

						# take screenshot (1)
						toggle_fullscreen( BROWSER ) # full
						BROWSER.save_screenshot( dest+"-4_1.png" )
						time.sleep( random.uniform(1, 4) )
						toggle_fullscreen( BROWSER ) # exit full

						# ---------------------------------------------------------- #

						# move the viewport (to the middle)

						el = BROWSER.find_element_by_xpath( "//*[@id=\"overview\"]" )
						ac = ActionChains(BROWSER)
						ac.move_to_element(el).move_by_offset(x_offset, -10).click().click().perform() # this click isn't working... ?
						time.sleep( random.uniform(1, 2) )

						# take screenshot (2)
						toggle_fullscreen( BROWSER ) # full
						BROWSER.save_screenshot( dest+"-4_2.png" )
						time.sleep( random.uniform(1, 4) )
						toggle_fullscreen( BROWSER ) # exit full

						# ---------------------------------------------------------- #

						# move the viewport (to the bottom)

						el = BROWSER.find_element_by_xpath( "//*[@id=\"overview\"]" )
						ac = ActionChains(BROWSER)
						ac.move_to_element(el).move_by_offset(x_offset, 90).click().click().perform()
						time.sleep( random.uniform(1, 2) )

						# take screenshot (3)
						toggle_fullscreen( BROWSER ) # full
						BROWSER.save_screenshot( dest+"-4_3.png" )
						time.sleep( random.uniform(1, 4) )
						time.sleep( random.uniform(1, 2) )

						
						# APPROACH 2: save all the image elements, and then piece together useing imagemagick
						# google too clever? detects these requests as abnormal and blocks... ?
						'''
						el	= BROWSER.find_element_by_xpath( "//*[@id=\"viewport\"]/div[1]/div/div/div[2]/div/div[2]" ) # viewport
						html = el.get_attribute('innerHTML')
						imgs = html.replace("&amp;","&").split("><")
						for img in imgs:
							print( img )
							imgurl = img.split( "src=", 1 )[1].split( "&zoom=", 1 )[0].replace("\"","")
							break # just get the first one... need to do in a better way!! get first child

						for i in range( 0, 138 ):
							if os.path.exists( dest+"-4_"+str(i) ): continue
							cmd = "wget --output-document=%s \"%s\"" % ( dest+"-4_"+str(i), imgurl+"&zoom=5&tid="+str(i) )
							print( cmd )
							os.system( cmd )

						break
						'''
