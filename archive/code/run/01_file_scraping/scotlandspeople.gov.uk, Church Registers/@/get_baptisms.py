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


fp = webdriver.FirefoxProfile()
BROWSER = webdriver.Firefox(firefox_profile=fp)

#root = "/media/michael/SSD3/Dropbox/workspace/2.research/_bin/ontologize/run/01_file_scraping/scotlandspeople.gov.uk"
root = "/mnt/SSD3/Dropbox/workspace/2.research/_bin/ontologize/run/01_file_scraping/scotlandspeople.gov.uk, BDMs"

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
#WebDriverWait(BROWSER, 5).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR,"iframe[name^='a-'][src^='https://www.google.com/recaptcha/api2/anchor?']")))
#time.sleep(3)
#element = BROWSER.find_element_by_xpath( "//span[@class='recaptcha-checkbox goog-inline-block recaptcha-checkbox-unchecked rc-anchor-checkbox']/div[@class='recaptcha-checkbox-checkmark']" )
#BROWSER.execute_script("arguments[0].click();", element)
#BROWSER.switch_to.default_content()

# Have to manually do some captcha stuff and then click the log in button...
#wait = WebDriverWait(BROWSER, 60)
#element = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id=\"block-system-user-menu\"]" )))

BROWSER.find_element_by_xpath( "//*[@id=\"edit-submit--3\"]" ).click()
time.sleep(5)


# ---------------------------------------------------- #
# STEP 2: Search records

#search_url  = "https://www.scotlandspeople.gov.uk/advanced-search/church/births-baptisms"
search_url  = "https://www.scotlandspeople.gov.uk/advanced-search#{%22category%22:%22church%22,%22record%22:%22church-births-baptisms%22}"
county      = "RENFREW"
church_type = "3"

start_page = ""
#start_page = "4405"
pickup_url = ""
#pickup_url = "https://www.scotlandspeople.gov.uk/record-results?page={0}&search_type=people&event=%28B%20OR%20C%20OR%20S%29&record_type%5B0%5D=opr_births&church_type=Old%20Parish%20Registers&dl_cat=church&dl_rec=church-births-baptisms&surname_so=exact&forename_so=starts&county=ARGYLL&record=Church%20of%20Scotland%20%28old%20parish%20registers%29%20Roman%20Catholic%20Church%20Other%20churches".format( start_page )

ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)
	
BROWSER.maximize_window()

church_type_xpath = "//*[@id=\"edit-church-type\"]/div[%s]/label" % church_type
#county_sel_xpath = "//*[contains(@id,\"edit-county\")]"
county_sel_xpath  = "/html/body/div[4]/div/div/main/div/section/div/div/div[2]/div[2]/div[6]/form/div/div[10]/div[2]/div[1]/span"
submit_xpath      = "//*[contains(@id,\"edit-submit\")]"

if pickup_url == "":
	BROWSER.get( search_url )
	time.sleep(5)
	
	#el = BROWSER.find_element_by_xpath("//*[@id=\"edit-church-type-presbyterian-registers\"]")
	el = BROWSER.find_element_by_xpath( church_type_xpath )
	#BROWSER.execute_script("arguments[0].scrollIntoView();", element)
	el.click()
	time.sleep(5)
	
	# manually select the county and submit ! can't get it working due to ElementNotInteractableException
	time.sleep(5)
		
	#el = BROWSER.find_element_by_xpath("//*[@id=\"edit-county--6\"]/option[text()='%s']" % county)
	#sel_el = BROWSER.find_element_by_xpath( county_sel_xpath )
	#sel_el.click()
	#time.sleep(2)
	
	#opt_el = BROWSER.find_element_by_xpath("//*[contains(@id,\"edit-county\")]/option[text()='%s']")
	#BROWSER.execute_script("arguments[0].scrollIntoView();", opt_el)
	#opt_el.click()
	
	#BROWSER.find_element_by_xpath("//*[@id=\"edit-submit--9\"]").click()
	#BROWSER.find_element_by_xpath( submit_xpath ).click()
	#time.sleep(5)
else:
	BROWSER.get( pickup_url )	
	time.sleep(5)


while True:
	el = WebDriverWait(BROWSER, 20, ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.ID, "edit-jump-to-page")))
	page_num = Select(el).first_selected_option.text

	with open(root+"/00_HTML/%s.html" % page_num, "w") as f:
		f.write(BROWSER.page_source)

	# move to next page
	try:
		el = WebDriverWait(BROWSER, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "li.next a")))
	except:
		BROWSER.refresh() # probably got an error page, so give it a second try...
		el = WebDriverWait(BROWSER, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "li.next a"))) # try a third time ?? loop it ?
	BROWSER.execute_script("arguments[0].scrollIntoView();", el)
	el.click()
	time.sleep(2)
