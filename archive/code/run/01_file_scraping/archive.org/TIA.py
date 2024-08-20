#from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
import os, time, datetime
import urllib
import glob
import shutil
import os.path
from selenium.common.exceptions import NoSuchElementException


## USAGE: Download html 'item page' as get.html, place in relevant folder, then run this script...


SLEEP_TIME = 2
BROWSER = None
FILTER_URL = None


def find_element(xpath):
  return BROWSER.find_element_by_xpath(xpath)

print "============================"
print "== Run started at ", datetime.datetime.now()
print "============================"


fp = webdriver.FirefoxProfile()
fp.set_preference('browser.helperApps.neverAsk.saveToDisk',
                   'image/jpeg,image/png,'
                   'application/octet-stream')
BROWSER = webdriver.Firefox(firefox_profile=fp)

run_dir = "/media/michael/Files/Dropbox/workspace/2.research/1.Material/3.Publications"

for root, dirs, files in os.walk( run_dir ):
	for fname in files:
		if fname == 'get_TIA.html' or fname == 'get_TIA.htm':
			filepath = root + "/" + fname
			print "\n"
			print filepath
			BROWSER.get("file:///" + filepath)
			time.sleep(1)

			try:
				ocr_lnk = BROWSER.find_element_by_partial_link_text('FULL TEXT')
				ocr_href = ocr_lnk.get_attribute('href').replace("file:///","http://archive.org/")
			except NoSuchElementException:
				ocr_href = ""				

			try:
				pdf_lnk = BROWSER.find_element_by_partial_link_text('PDF')
				pdf_href = pdf_lnk.get_attribute('href').replace("file:///","http://archive.org/")
			except NoSuchElementException:
				pdf_href = ""

			DL_dir = "/20160722, TIA"
			PDF_dir = root + DL_dir + "/01_PDF"
			OCR_dir = root + DL_dir + "/01_OCR"
			MKD_dir = root + DL_dir + "/02_MKD"

			if not os.path.exists(PDF_dir):
				os.makedirs(PDF_dir)
			if not os.path.exists(OCR_dir):
				os.makedirs(OCR_dir)
			if not os.path.exists(MKD_dir):
				os.makedirs(MKD_dir)

			PDF_path = PDF_dir + "/ALL.pdf"
			if pdf_href and not os.path.isfile( PDF_path ):
				print "Saving PDF..."
				urllib.urlretrieve(pdf_href, PDF_path)

			OCR_path = OCR_dir + "/ALL.ocr"
			if ocr_href and not os.path.isfile( OCR_path ):
				print "Saving OCR text..."
				BROWSER.get(ocr_href)
				time.sleep(SLEEP_TIME) 
				text = BROWSER.find_element_by_css_selector('pre').text

				w = open(OCR_path,'w')
				w.write(text.encode('ascii', 'ignore'))
				w.close()

			if ocr_href:
				MKD_path = MKD_dir + "/ALL.ocr.mkd"
				if not os.path.isfile( MKD_path ):
					r = open(OCR_path,'r')
					text = r.read()
					w = open(MKD_path,'w')
					w.write(text.encode('ascii', 'ignore'))
					w.close()

			mv_cmd = "mv \"%s\" \"%s\"" % ( filepath, root + DL_dir + "/meta.html" )
			print mv_cmd
			os.system( mv_cmd )
