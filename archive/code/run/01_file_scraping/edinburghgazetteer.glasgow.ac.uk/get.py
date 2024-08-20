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
import urllib.request


fp = webdriver.FirefoxProfile()
BROWSER = webdriver.Firefox(firefox_profile=fp)

# ---------------------------------------------------- #
# STEP 1: Download all !

start_url 	= "https://edinburghgazetteer.glasgow.ac.uk/the-gazetteer/?eg=13"

BROWSER.get( start_url )
time.sleep(2)

while True:
	
	final_xpath = ""
	
	image_xpath = "/html/body/div/div[2]/section/main/article/div/div[2]/a[3]"
	try:
		BROWSER.find_element_by_xpath( image_xpath )
		final_xpath = image_xpath
	except NoSuchElementException:
		pass
	
	image_xpath = "/html/body/div/div[2]/section/main/article/div/div[1]/a[3]"
	try:
		BROWSER.find_element_by_xpath( image_xpath )
		final_xpath = image_xpath
	except NoSuchElementException:
		pass
	
	image_url = BROWSER.find_element_by_xpath( final_xpath ).get_attribute('href') # download the image
	urllib.request.urlretrieve(image_url, image_url.rsplit("/",1)[1])
	time.sleep(4)
	
	# -------------------------------------------------------------------- #
	
	final_xpath = ""
	
	next_xpath = "/html/body/div/div[2]/section/main/article/div/div[2]/a[4]"
	try:
		BROWSER.find_element_by_xpath( next_xpath )
		final_xpath = next_xpath
	except NoSuchElementException:
		pass
	
	next_xpath = "/html/body/div/div[2]/section/main/article/div/div[1]/a[4]"
	try:
		BROWSER.find_element_by_xpath( next_xpath )
		final_xpath = next_xpath
	except NoSuchElementException:
		pass

	BROWSER.find_element_by_xpath( final_xpath ).click()
	time.sleep(4)
