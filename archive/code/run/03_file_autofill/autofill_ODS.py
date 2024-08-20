from __future__ import unicode_literals, division
import ezodf

import os
import glob
import sys

run_dir = "/media/michael/SSD3/Dropbox/workspace/2.research/01.Material/01.Primary/03.Maps etc/00.WWW/NAN, Nationaal Archief (NED)/VEL/(1488-1665), Guiana/1577, GUIANA, Berbice, 1802 [L][EP]"



def find_kml_dir( dirname, lines, line_num, scope ):
	i = line_num

	for line in lines[line_num+1:]:
		i += 1

		num_tabs = line.count("\t")

		if not scope or num_tabs == scope+1:
			if "<name>%s</name>" % dirname in line or "<name>%s," % dirname in line or "<name>%s [" % dirname in line:
				#print( "Found at: %s" % i )
				return i, num_tabs

		if num_tabs < scope and num_tabs != 0: # i.e. if a stray newline has snuck in to one of the pin or folder titles, ignore that case... 
			#print( "- ( gave up on line %s with scope %s)" % ( i, scope ) )
			return None, None # left the scope
	return None, None


def get_lat_long( lines, line_num, scope ):
	i = line_num

	latitude 	= None
	longitude 	= None

	for line in lines[line_num:]:

		num_tabs = len(line)-len(line.lstrip('\t'))

		if "<longitude>" in line: longitude = line.strip().replace("<longitude>","").replace("</longitude>","")
		if "<latitude>" in line: latitude = line.strip() .replace("<latitude>","").replace("</latitude>","")

		if latitude and longitude: return longitude, latitude

	return None, None


kml_shortcuts = {
	"OS1-6inch-Ren": "/media/michael/SSD3/Dropbox/workspace/2.research/01.Material/01.Primary/03.Maps etc/00.WWW/NLS, National Library of Scotland/OS 6-inch, 1st Edition, 1843-1882 [+]/Renfrewshire/02_KML/ALL.kml"
}


for root, dirs, files in os.walk( run_dir ):
	for fname in files:
		if fname.endswith(".ods") and "[+]" in fname:
			filepath = root + "/" + fname

			ods = ezodf.opendoc( filepath )
			sheet = ods.sheets[0]


			# Surname analysis

			col_pers_id = None
			col_sco 	= None
			col_hld 	= None
			for col in range(sheet.ncols()):
				if sheet[0, col].value == "###PERS_ID": col_pers_id = col
				if sheet[0, col].value == "###^SURNAME:SCO": col_sco = col
				if sheet[0, col].value == "###^SURNAME:HLD": col_hld = col

			if col_pers_id and col_sco and col_hld:
				# todo (or should it be in a separate file?)
				pass


			# Mapping refs

			missing_refs	= []
			col_mappingref 	= None
			col_latitude 	= None
			col_longitude 	= None
			for col in range(sheet.ncols()):
				if sheet[0, col].value == "###MAPPING_REF": col_mappingref = col
				if sheet[0, col].value == "###^LATITUDE": col_latitude = col
				if sheet[0, col].value == "###^LONGITUDE": col_longitude = col

			if col_mappingref and col_latitude and col_longitude:

				print( filepath )

				# Loop through rows
				for row in range(1,sheet.nrows()):
					mappingref = str(sheet[row, col_mappingref].value)

					if not mappingref or mappingref == "None": continue
					# GET THE LATITUDE AND LONGITUDE FROM THE KML FILE

					kml_filename 	= mappingref.split(":",1)[0].replace("@","").strip()
					kml_dirnames 	= mappingref.split(":")[1:]
					latitude		= None
					longitude		= None

					if kml_filename in kml_shortcuts:
						kml_path = kml_shortcuts[kml_filename]
					else:
						kml_path = "%s/../02_KML/%s.kml" % ( root, kml_filename )
						if not os.path.isfile( kml_path ):
							kml_path = "%s/../../A, Map/02_KML/%s.kml" % ( root, kml_filename )

					if not os.path.isfile( kml_path ):
						print( "KML FILE DOES NOT EXIST" )
						print( kml_path )
						break

					kml_dirnames = [ "02_PINS" ] + kml_dirnames
					with open( kml_path, "r" ) as r:
						lines 		= r.readlines()
						line_num 	= 0 
						scope 		= 0
						for kml_dirname in kml_dirnames:
							kml_dirname = kml_dirname.strip()
							#print( "Looking for: \"%s\", from line %s; scope %s" % ( kml_dirname, line_num, scope ) )
							line_num, scope = find_kml_dir( kml_dirname, lines, line_num, scope )
							if not line_num and not scope: break

					# UPDATE THE SRPEADSHEET

					if line_num and scope:
						latitude, longitude = get_lat_long( lines, line_num, scope )

						if latitude and longitude:
							sheet[row, col_latitude].set_value( latitude )
							sheet[row, col_longitude].set_value( longitude )
					else:
						missing_refs.append( mappingref )
						
				print( "NUM MISSING: %s" % len( missing_refs ) )
				#for ref in sorted( missing_refs ): print( "- %s" % ref )

			ods.save()
