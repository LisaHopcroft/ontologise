#!/usr/bin/python

import sys
import csv
sys.path.append("/media/michael/Files/Dropbox/workspace/2.research/_bin")

try:
    # for Python2
    from Tkinter import *
except ImportError:
    # for Python3
    from tkinter import * 
import sqlite3
import datetime
from ods2csv import *
from util import *

# --------------------------------------------------------- #
# Convert a list of records to MKD template files
# --------------------------------------------------------- # 

if len(sys.argv) > 1:
	infile = sys.argv[1]

def pad_with_zeroes( txt_num, target_digits ):
	if len( txt_num ) < target_digits:
		txt_num = "0" + txt_num
		return pad_with_zeroes( txt_num, target_digits )
	else:
		return str(txt_num)

with open(infile,"rb") as csvfile:
	reader = csv.DictReader(csvfile)
	for row in reader:
		fm_name = row['Fm'].replace("/","-")
		id_text = pad_with_zeroes( row['Id'], 3 )
		to_name = row['To'].replace("/","-")
		year = row['Date']
		if row['Date'].startswith("1"):
			year = row['Date'][:4]
		if "," in fm_name and fm_name[:1] != "+":
			fm_name = row['Fm'].split(",",1)[1][1:2] + "." + row['Fm'].split(",",1)[0]
		if "," in to_name and to_name[:1] != "+":
			to_name = row['To'].split(",",1)[1][1:2] + "." + row['To'].split(",",1)[0]
		filename = '%s, %s to %s, %s.txt' % (id_text, fm_name, to_name, year)
		print filename
		f = open('02_TXT/' + filename, 'w')
		f.write("#LETTER\n")
		f.write("##Fm:   %s\n" % ( row['Fm'] ))
		f.write("##Fm@:  %s\n" % ( row['Fm@'] ))
		f.write("##To:   %s\n" % ( row['To'] ))
		f.write("##To@:  %s\n" % ( row['To@'] ))
		f.write("##Date: %s\n" % ( row['Date'] ))
		f.write("----------------------\n")
		f.write("> \n")
		f.write("----------------------\n")
		f.write("\n")
		f.write("\n")
		f.close()
