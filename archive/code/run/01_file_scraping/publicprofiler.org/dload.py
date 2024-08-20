from selenium import webdriver
import os, time, datetime, csv
import glob
from bs4 import BeautifulSoup as BS
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import datetime
import string

reload(sys)
sys.setdefaultencoding('utf8')


for filepath in glob.glob( "*est.tsv" ): #surnames.
	with open( filepath, "r" ) as r:
		tsv = csv.reader( r, delimiter="\t" )
		for row in tsv:

			# check if Scottish origin name first... save some time...

			URL = "http://gbnames.publicprofiler.org/Comparisons.aspx?name=%s&year=1881&altyear=1998&country=GB&type=name" % row[1]
			print URL
			writepath = "01_HTML/%s.html" % row[1]
			if not os.path.exists( writepath ):
				cmd = "wget -O \"%s\" \"%s\"" % ( writepath, URL )
				os.system( cmd )
