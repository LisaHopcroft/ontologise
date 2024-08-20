#!/usr/bin/python

import urllib, urllib2
from bs4 import BeautifulSoup

import sys, os, time
sys.path.append("/mnt/cloud/Dropbox/workspace/2.academia/_bin")
from util import *

url_start = "http://eap.bl.uk/EAPDigitalItems/EAP688/EAP688"

for root, dirs, files in os.walk("/mnt/cloud/Dropbox/workspace/2.academia/1.Material/2.Official/00.DIGITAL-COLLECTIONS/"):
	for name in files:
		if name.startswith("links.html"):
			conn = urllib2.urlopen("file://" + root + "/links.html")
			html = conn.read()
			soup = BeautifulSoup(html, "html")
			links = soup.find_all('a')

			if not os.path.exists(root + "/01_JPG"):
				os.makedirs(root + "/01_JPG")

			for tag in links:
				link = tag.get('href', None)
				filename = link.rsplit('/', 1)[-1]
				if link is not None:
					print link 
					if not os.path.exists(root + "/01_JPG/" + filename):
						urllib.urlretrieve(link, root + "/01_JPG/" + filename)


