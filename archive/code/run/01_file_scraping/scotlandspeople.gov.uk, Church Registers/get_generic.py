import os, time, csv
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
from datetime import datetime
import urllib
import os


fp      = webdriver.FirefoxProfile()
BROWSER = webdriver.Firefox(firefox_profile=fp)


# ---------------------------------------------------- #
# STEP 1: Log in

login_url 	= "https://www.scotlandspeople.gov.uk"
username 	= "michael.hopcroft@gmail.com"
password 	= "-3a46SPbbf9/"

BROWSER.get( login_url )
time.sleep(2)
BROWSER.find_element_by_xpath( "//*[@id=\"mainHeader\"]/div/div/label/a[1]" ).click()
time.sleep(4)
BROWSER.find_element_by_xpath( "//*[@id=\"edit-name\"]" ).send_keys(username)
BROWSER.find_element_by_xpath( "//*[@id=\"edit-pass\"]" ).send_keys(password)
BROWSER.find_element_by_xpath( "//*[@id=\"edit-submit--3\"]" ).click()
time.sleep(5)


# ---------------------------------------------------- #
# STEP 2: Search records

#search_url  = "https://www.scotlandspeople.gov.uk/advanced-search#{%22category%22:%22church%22,%22record%22:%22church-banns-marriages%22}"
search_url  = "https://www.scotlandspeople.gov.uk/advanced-search#{%22category%22:%22church%22,%22record%22:%22church-banns-marriages%22}"
#county      = "RENFREW"

start_page = ""
#pickup_url = "https://www.scotlandspeople.gov.uk/record-results?page=7103&search_type=people&event=M&record_type%5B0%5D=opr_marriages&church_type=Old%20Parish%20Registers&dl_cat=church&dl_rec=church-banns-marriages&surname_so=exact&forename_so=starts&spouse_name_so=exact&county=AYR&record=Church%20of%20Scotland%20%28old%20parish%20registers%29%20Roman%20Catholic%20Church%20Other%20churches"
pickup_url = ""

ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)
	
BROWSER.maximize_window()

if pickup_url == "":
	BROWSER.get( search_url )
	time.sleep(15)

	# manually select the chrurch type and county and submit ! 
	# ... can't get it working due to ElementNotInteractableException
	
	time.sleep(5)
else:
	BROWSER.get( pickup_url )	
	time.sleep(5)


# ---------------------------------------------------- #
# STEP 3: Save all the pages

cwd     = os.getcwd()
now   	= datetime.now()
new_dirname = now.strftime("%Y-%m-%d_%H-%M-%S")
new_dirpath = cwd +"/00_HTML/" + new_dirname
os.mkdir( new_dirpath )

while True:
	el = WebDriverWait(BROWSER, 20, ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.ID, "edit-jump-to-page")))
	time.sleep(1)
	page_num = Select(el).first_selected_option.text

	with open(new_dirpath+"/%s.html" % page_num, "w") as f:
		f.write(BROWSER.page_source)

	# move to next page
	try:
		el = WebDriverWait(BROWSER, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "li.next a")))
	except:
		BROWSER.refresh() # probably got an error page, so give it a second try...
		el = WebDriverWait(BROWSER, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "li.next a"))) # try a third time ?? loop it ?
	BROWSER.execute_script("arguments[0].scrollIntoView();", el)
	el.click()
