from pyvirtualdisplay import Display
from selenium import webdriver
import os, time, datetime
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import UnexpectedAlertPresentException
from socket import error as SocketError

import sys
sys.path.append("/media/michael/Files/Dropbox/workspace/2.research/_bin")
from ontologize.modules.util.all import *


print( "============================" )
print( "== Run started at ", datetime.datetime.now() )
print( "============================" )

tmp_dir = "/home/michael/Downloads"

publ_details = {}
with open('./publications.tsv', 'r') as tsv:
	tsv = csv.reader(tsv, delimiter='\t')
	for row in tsv:
		publ_details[row[0]] = row[1]


# Download files
for filename in os.listdir( tmp_dir ):
	if filename.startswith("BL_"):
		print( filename )
		publ = filename.split("_")[1]
		save_dir = publ_details[publ]
		year = filename.split("_")[2][:4]
		writepath = "%s/%s/%s" % ( save_dir, year, filename )
		if not os.path.exists( writepath ):
			fmpath = "%s/%s" % ( tmp_dir, filename )
			os.system( "mv %s %s" % ( escape_filepath( fmpath ), escape_filepath( writepath ) ) )
		else:
			print( "Exists..." )
