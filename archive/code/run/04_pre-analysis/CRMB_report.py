#!/usr/bin/python

import sys
sys.path.append("/media/michael/Files/Dropbox/workspace/2.research/_bin")

try:
    # for Python2
    from Tkinter import *
except ImportError:
    # for Python3
    from tkinter import *
import sqlite3
import os, time
import pipes
from util import *


def sql_safe( arg ):
    return arg.replace( "'", "''" )


override = False
if len(sys.argv) > 1:
	arg = sys.argv[1]
	if arg == "override":
		override = True

for root, dirs, files in os.walk("/media/michael/Files/Dropbox/workspace/2.research/1.Material/1.Manuscripts"):
    for name in files:
        if name.startswith("crmb.txt"):
			path = root + "/" + name
			f = open(path, 'r')
			print f.read()
