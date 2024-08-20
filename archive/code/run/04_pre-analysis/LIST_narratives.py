#!/usr/bin/python

import sys
sys.path.append("/mnt/cloud/Dropbox/workspace/2.research/_bin")
from util.util import *
from subprocess import call




def q_will_file( readfile ):
	will_file = 0
	first_line=readfile.readline().rstrip()
	if "#WILL" in first_line:
		will_file = 1
	return will_file


trx_all = []
trx_wills = []
trx_letters = []
jpg_all = []
trx_official_all = []
max_depth = 10
skip_dirs = [ "02_TXT", "02_MKD", "01_JPG", "01_PNG" ]


def parse_material_folder( folder ):
	narrative_list = []

	for root, dirs, files in os.walk( folder, topdown=True ):
		for d in dirs:
			if "_narratives" in d:
				path = root + "/" + d

				for trxroot, subdirs, txtfiles in os.walk( path ):
					for fname in txtfiles:
						if fname.endswith(".txt") and not fname.startswith("^"):
							txt = trxroot + "/" + fname
							txt = txt.replace( "/mnt/cloud/Dropbox/workspace/2.research/1.Material/", "" )
							txt = txt.replace( "/mnt/cloud/Dropbox/workspace/2.research/1.Material/1.Manuscripts/", "" )

							folder_list = txt.split("/")
							folder_txt = ""

							for folder in folder_list[:-1]:
								if "_narratives" in folder:
									continue

								folder = folder.split(",")[0]
								folder_txt = folder_txt + folder + "."

							print fname
							print txt
							print folder_list[-1]
							folder_txt = folder_list[-1] + "\t" + folder_txt

							narrative_list.append( folder_txt )

	return sorted(narrative_list)


narrative_files = parse_material_folder( "/mnt/cloud/Dropbox/workspace/2.research/1.Material" )
with open('../../^lists/^narrative_filelist.tsv', "w") as w:
	for narrative_file in narrative_files:
		w.write("%s\n" % narrative_file)

for m in narrative_files:
	print m

#print_bib( "/mnt/cloud/Dropbox/workspace/2.research/1.Material/2.Official/^trx_all.txt", trx_official_all )
