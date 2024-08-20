import os
import re
import csv
import sys

sys.path.append("/mnt/SSD3/Dropbox/workspace/2.research/_bin")
from ontologize.modules.data_transformation.normalise import *


is_override = False
run_dir = "/mnt/SSD3/Dropbox/workspace/2.research/01.Sources"

if len(sys.argv) == 2:
	run_dir = sys.argv[1]



def get_folder_path( folder_list, tab_count ):
	folder_path = ""

	is_txt = False
	is_first = True
	i = 0
	for folder_name in folder_list:
		if folder_name:
			if i <= tab_count and is_txt:
				if not is_first:
					folder_path += " : "
				folder_path += folder_name
				is_first = False
			if folder_name == "02_TXT": is_txt = True
		i += 1
	#print( folder_name )
	return folder_path.replace("&apos;","'").replace("&amp;","&")


def is_proprietor_txt( actual_line, kml_path, num_lines ):
	if num_lines > 1:
		return actual_line.endswith( "'s" ) or actual_line.endswith( "'s]" ) or actual_line.endswith( "[']s" )

	if "[@]" in kml_path:
		return actual_line.endswith( "'s" ) or actual_line.endswith( "'s]" ) or actual_line.endswith( "[']s" )
	else:
		return not actual_line.endswith( "[@]" )


for root, dirs, files in os.walk( run_dir ):
	for fname in files:
		if fname.endswith( ".kml" ):
			fpath = "%s/%s" % ( root, fname )

			mappings			= []
			places				= []
			kml_paths 		= {}

			with open( fpath, "r" ) as r:
				item_type	= ""
				name 		= ""
				folder 		= ""
				folder_list = [None] * 100 #
				longitude 	= ""
				latitude 	= ""
				folder_path = ""
				for line in r.readlines():

					if "<GroundOverlay>" in line: item_type = "GroundOverlay"
					if "<Placemark>" in line: item_type = "Placemark"
					if "<Folder>" in line: item_type = "Folder"

					folder 	= re.sub('<[^<]+>', "", line.strip())

					if folder:
						if "<name>" in line:
							name = re.sub('<[^<]+>', "", line.strip())

							if ", " in name:
								el = name.split( ", ", 1 )[0]
								if el.isdigit() or el == el.upper() and not "@" in el:
									name = el

							# build a folder list to create full kml_path...
							tab_count = line.count('\t')
							folder_list[ tab_count ] = name

							kml_path = get_folder_path( folder_list, tab_count )
							place_id = kml_path.replace( " : ", ", " )


							if item_type == "Placemark":

								# if is a PARISH or TYPE directory then skip on...

								core_name = name.replace( "[@]", "" ).replace( "[']", "" )
								num_strip = ''.join([i for i in core_name if not i.isdigit()])
								if ( core_name == core_name.upper() and len( num_strip ) < 3 ) or "#" in core_name: # skip on
									continue

								if not core_name.isdigit() and " : " in kml_path:  # i.e. any textual entry...

									date_txt 	= ""
									colony_txt	= ""

									# Generate a PLN-LIST file by extracting details from the KML...

									# ...get date info...
									date_txt 	= kml_path.split(" : ",1)[0].replace( " *", "" )
									if " " in date_txt:
										date_txt	= date_txt.rsplit( " ", 1 )[1]


									# ...get colony info...
									pre_txt 	= kml_path.rsplit(" : ",1)[0]
									colony_txt 	= pre_txt.replace( " *", "" ).replace( " : ", ", " ).replace( "[@]", "" ).replace( "@", "" ).replace( date_txt, "" ).replace( " ,", "," ).replace( ", #[Houses]", "" ).replace( ", #[Sugar]", "" ).replace( ", #[Other]", "" ).replace( ", #[Seats]", "" ).replace( ", #[Crawls]", "" ).replace( ", #[Taverns]", "" ).replace( ", #[Others]", "" ).replace("[']","")


									# ...values to get...
									prop_type	= ""
									txt			= name.replace("&apos;","'").replace("&amp;","&")
									pers_id		= ""
									place_id	= colony_txt + ", ."
									pers_ids 	= []


									# ...get prop type...
									if "#[Houses]" in kml_path:
										prop_type 	= "House"
									elif "#[Sugar]" in kml_path:
										prop_type 	= "Sugar"
									elif "#[Seats]" in kml_path:
										prop_type 	= "Seat"
									elif "#[Other]" in kml_path:
										prop_type 	= "Other"
									else:
										prop_type 	= "."

									if "#[Taverns]" in kml_path:
										continue


									# loop through each "actual" line (seperated by "[/]") to get "pers_id" and "place_id"...

									if "[/]" in txt:
										actual_lines = txt.split( "[/]" )
									else:
										actual_lines = [txt]

									for actual_line in actual_lines:
										actual_line = actual_line.replace( " / ", " " ).replace( "/", "" )

										# adopt the possessive if ends with Pen, Estate etc...
										if "'s" in actual_line or "']s" in actual_line:
											if actual_line.endswith( " Craul" ) or actual_line.endswith( " Crawl" ):
												actual_line = actual_line[:-6]
											elif actual_line.endswith( " Estate" ):
												actual_line = actual_line[:-7]
											elif actual_line.endswith( " Pen" ) or actual_line.endswith( " pen" ):
												actual_line = actual_line[:-4]

										# IF this line contains proprietor text...
										if is_proprietor_txt( actual_line, kml_path, len( actual_lines ) ):

											txt = txt.replace( "[&]", "&" )
											# if multiple individuals iterate over each...
											if "&" in txt:
												names = txt.split( "&" )
											elif " and " in txt:
												names = txt.split( " and " )
											else:
												names = [ actual_line ]

											for indiv_name in names:
												indiv_name = indiv_name.strip()
												if indiv_name.endswith( " Esq" ):
													indiv_name = indiv_name[:-4]

												# convert to pers_id format...
												if " " in indiv_name:
													surname 	= indiv_name.rsplit(" ",1)[1]
													forenames 	= indiv_name.rsplit(" ",1)[0].replace("."," ").replace("  "," ")
												elif "." in indiv_name:
													surname 	= indiv_name.rsplit(".",1)[1]
													forenames 	= indiv_name.rsplit(".",1)[0].replace("."," ").replace("  "," ")
												else:
													surname 	= indiv_name
													forenames	= "."

												forenames = forenames.replace("Captn ","").replace("Maj ","").replace("Sir ","")

												# normalise surnames
												surname		= normalise_surnames( surname )

												if "Mrs" in forenames or "Miss" in forenames:
													surname = "--"+surname
													forenames = forenames.replace( "Mrs", "" ).replace( "Miss", "" )

												pers_ids.append( surname + ", " + forenames.replace("&","") )

										# IF this line contains property text...
										else:
											place_id = colony_txt + ", " + actual_line.replace( " [@]", "" )

									# make the maping_ref unique
									if not kml_path in kml_paths:
										kml_paths[kml_path] = 1
									else:
										kml_paths[kml_path] += 1
									if kml_paths[kml_path] > 1:
										kml_path = kml_path + " {%s}" % kml_paths[kml_path]

									pers_id = "; ".join( pers_ids )

									places.append( [ date_txt, prop_type, txt, pers_id, place_id, kml_path ] )

						if "<coordinates>" in line and item_type == "Placemark":
							#print line
							#print item_type
							coordinates 	= re.sub('<[^<]+>', "", line.strip())
							if "," in coordinates:
								longitude 	= coordinates.split(",")[0]
								latitude 	= coordinates.split(",")[1]
								mappings.append( [ kml_path, latitude, longitude ] )
								name 		= ""
								longitude 	= ""
								latitutde 	= ""
								kml_path    = ""

			if mappings:

				dat_dir = os.path.dirname( fpath ).replace( "02_KML", "03_^DAT" )
				if not os.path.exists( dat_dir ):
					os.mkdir( dat_dir )

				writepath = fpath.replace( "02_KML/", "03_^DAT/^" ) + ".MAPPING.tsv"
				with open( writepath, "w" ) as w:
					w.write( "\t".join( [ "kml_path", "lat", "lon" ] ) + "\n" )
					for mapping in mappings:
						w.write( "\t".join( mapping ) + "\n" )

			if places:

				dat_dir = os.path.dirname( fpath ).replace( "02_KML", "02_TSV" )
				if not os.path.exists( dat_dir ):
					os.mkdir( dat_dir )

				writepath = fpath.replace( "02_KML/", "02_TSV/^" ) + ".[+].tsv"
				with open( writepath, "w" ) as w:
					w.write( "\t".join( [ "#[]", "###DATE", "Prop type.", "Place/Prop text.", "###PERS_ID", "###AT", "###MAPPING_REF" ] ) + "\n" )
					for place in places:
						w.write( "\t".join( [ "PLN-LIST" ] + place ) + "\n" )
