from selenium import webdriver
import os, time, datetime, csv
from bs4 import BeautifulSoup as BS
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys  
import datetime

reload(sys)  
sys.setdefaultencoding('utf8')

SLEEP_TIME = 3
BROWSER = None
GOTO_URL = None
delay = 1

fp = webdriver.FirefoxProfile()
fp.set_preference('browser.helperApps.neverAsk.saveToDisk',
                   'image/jpeg,image/png,'
                   'application/octet-stream')
BROWSER = webdriver.Firefox(firefox_profile=fp)

academia_root = "/media/michael/Files/Dropbox/workspace/2.research"

def find_element(xpath):
	return BROWSER.find_element_by_xpath(xpath)


def download_tables_as_data( writepath, place_txt="", date_txt = "" ):
	# Getting contents of table
	try:
		BROWSER.find_element_by_xpath("//*[@id='results-main']/table")
	except NoSuchElementException:
		return

	#print "URL: %s (@%s)" % ( BROWSER.current_url, str( datetime.datetime.now() ) )
	#print "Saving HTML table as TSV..."
	content = BROWSER.find_element_by_xpath("//*[@id='results-main']/table").get_attribute('outerHTML')
	soup = BS(content)
	with open( writepath, 'a') as f:
		for row in soup.findAll('tr')[1:]:
			col = row.findAll('td')
			name = ''.join(col[1].findAll(text=True))
			birthyear = ''.join(col[2].findAll(text=True))
			parish = ''.join(col[3].findAll(text=True))
			colony = ''.join(col[4].findAll(text=True))
			year = ''.join(col[5].findAll(text=True))
			owner = ''.join(col[6].findAll(text=True))
			for a in col[7].find_all("a", href=True):
			    img_url = a["href"]
			
			record = (name, birthyear, parish, colony, year, owner, img_url, BROWSER.current_url)
			#print record
			f.write( ( "\t".join(record) ) + "\n" )
	f.close()

	# Moving to next page, and repeat...
	if len( BROWSER.find_elements_by_xpath("//*[@class='next']/a") ) > 0:
		#print "Moving to next page..."
		url = BROWSER.find_elements_by_xpath("//*[@class='next']/a")[0].get_attribute( "href" )
	else:
		return	

	BROWSER.get( url )
	return download_tables_as_data( writepath )



print "============================"
print "== Run started at ", datetime.datetime.now()
print "============================"

# Get credentials
BROWSER.get("https://secure.ancestry.co.uk/login")
f = open('./credentials.txt', 'r')
username, password = f.readlines()
print "Username: %s" % username.strip()
print "Password: %s" % password.strip()
f.close()

# Log in
print "Logging in..."
find_element("//input[@id='username']").send_keys(username.strip())
find_element("//input[@id='password']").send_keys(password.strip())
BROWSER.execute_script( "$('#loginButton').click();" )
print "Logged in..."


for root, dirs, files in os.walk( academia_root ):
	for filename in files:
		URL 		= ""
		place_txt 	= ""
		date_txt 	= ""
		is_continue = False
		filepath = "%s/%s" % ( root, filename )

		if filename == "@CONTINUE.url":
			print "Continue..."
			is_continue = True
			with open( filepath,  "r" ) as r:
				URL = r.readline()

		if filename == "@GET.[slaves].tsv":
			with open( filepath,  "r" ) as r:			
				tsv = csv.DictReader( r, delimiter="\t", quotechar="'" )
				row = next( tsv )
				place_txt = row["PLACE_TXT"]
				date_txt  = row["DATE_TXT"]
				print place_txt
				if '"' in place_txt:
					print "Specific locale... %s" % place_txt
					URL = "http://search.ancestry.co.uk/cgi-bin/sse.dll?db=BritishSlaves&gss=sfs28_ms_r_db&new=1&rank=1&msrpn__ftp=%s&msrpn__ftp_x=1&msrdy=%s&msrdy_x=1&MSAV=1&MSV=0&uidh=60i" % ( place_txt.replace( '"', "%22" ).replace( ' ', '%20' ), date_txt )
				else:
					print "Non-specific locale... %s" % place_txt
					URL = "http://search.ancestry.co.uk/cgi-bin/sse.dll?db=BritishSlaves&gss=sfs28_ms_r_db&new=1&rank=1&gskw=%s&gskw_x=1&msrdy=%s&msrdy_x=1&MSAV=1&MSV=0&uidh=60i" % ( place_txt, date_txt )

				# just retrieve the slaves born after given date...
				if "BORN_AFT" in row:
					born_plu_min_10 = int(row["BORN_AFT"]) + 11 # add 11 years on, because search has 10 year window
					URL = "http://search.ancestry.co.uk/cgi-bin/sse.dll?db=BritishSlaves&gss=sfs28_ms_r_db&new=1&rank=1&msbdy=%s&msbdy_x=1&msbdp=10&gskw=%s&gskw_x=1&msrdy=%s&msrdy_x=1&MSAV=1&MSV=0&uidh=60i" % ( str(born_plu_min_10), place_txt, date_txt )

		if URL:
			root_dir = filepath.rsplit("/",1)[0]
			writepath = root_dir + '/01_TSV/ALL.html.tsv'

			odspath = writepath.replace( "01_TSV", "02_ODS" ) + ".[+].^.ods" # lost some TSVs... so also looking to see if ODS exists...

			if ( os.path.exists( writepath ) or os.path.exists( odspath ) ) and not is_continue:
				print "File exists..."
			else:
				print "Processing %s..." % filepath

				if is_continue:
					cmd = "cp %s %s" % ( writepath, writepath+".cont.bkp" )
					print cmd
					os.system( cmd )

				# Start downloading
				BROWSER.get( URL )
				print "Processing URL '%s'..." % URL
				download_tables_as_data( writepath, place_txt, date_txt )

os.system( "rm geckodriver.log" )
