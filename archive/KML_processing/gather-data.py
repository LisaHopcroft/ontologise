import os
import csv
from collections import defaultdict
from collections import OrderedDict


is_refresh 			= False
is_debugging 		= False
is_render_images 	= False
is_run_places 		= False
is_run_people 		= True


if is_refresh:
	os.system( "python3 /mnt/SSD3/Dropbox/workspace/2.research/_bin/ontologize/run/05_data_transformation/parse_KML.py" )
	os.system( "python3 /mnt/SSD3/Dropbox/workspace/2.research/_bin/ontologize/run/05_data_transformation/parse_MKD.py" )
	os.system( "python3 /mnt/SSD3/Dropbox/workspace/2.research/_bin/ontologize/run/06_data_analysis/01_generate-DAG.py \"/mnt/SSD3/Dropbox/workspace/2.research/01.Sources/01.Primary/01.Manuscripts/00.WWW/FS, FamilySearch/359031, Cairn of Lochwinyoch matters, 1827-37\"" )

run_dir = "/mnt/SSD3/Dropbox/workspace/2.research/01.Sources/01.Primary/01.Manuscripts/00.WWW/FS, FamilySearch/359031, Cairn of Lochwinyoch matters, 1827-37"

LWH_maps = [
	( "OS 1857", "/mnt/SSD3/Dropbox/workspace/2.research/01.Sources/01.Primary/03.Maps etc/00.WWW/NLS, National Library of Scotland/OS 6-inch, 1st Edition, 1843-1882 [+]/Renfrewshire/02_KML/ALL.kml", "SCO, REN" ),
	( "Ainslie 1796", "/mnt/SSD3/Dropbox/workspace/2.research/01.Sources/01.Primary/03.Maps etc/00.WWW/NLS, National Library of Scotland/Newman.645, County of Renfrew, 1796 (Ainslie)/02_KML/ALL.kml", "SCO, REN" ),
	( "Roy 1750s", "/mnt/SSD3/Dropbox/workspace/2.research/01.Sources/01.Primary/03.Maps etc/00.WWW/NLS, National Library of Scotland/Military Survey of Scotland, 1747-55 (Roy)/02_KML/LWH.kml", "SCO, REN" ),
	( "Unknown c.1780", "/mnt/SSD3/Dropbox/workspace/2.research/01.Sources/01.Primary/03.Maps etc/01.Archives/01.SCOTLAND/RHC, Renfrewshire Heritage Centre/Castle Semple c.1780/02_KML/ALL.kml", "SCO, REN" ),
	( "Watt 1733", "/mnt/SSD3/Dropbox/workspace/2.research/01.Sources/01.Primary/03.Maps etc/01.Archives/02.ENGLAND & WALES/BCA, Birmingham City Archives/MS219.2, Records of John Watt Snr/4, Drawings/7, Map of Lochwinnoch parish, 1733/02_KML/ALL.kml", "SCO, REN, LWH" ),
	( "Watt c.1730", "/mnt/SSD3/Dropbox/workspace/2.research/01.Sources/01.Primary/03.Maps etc/01.Archives/02.ENGLAND & WALES/BCA, Birmingham City Archives/MS219.2, Records of John Watt Snr/4, Drawings/14, Map of Lochwinnoch, c1730/02_KML/ALL.kml", "SCO, REN" ),
	( "Infered", "/mnt/SSD3/Dropbox/workspace/2.research/01.Sources/07.Collated/(Geo-Coordinates)/02_KML/3.Infered-from-written-sources.kml", "" ),
]

WIN_maps = [
	( "Custom", "/mnt/SSD3/Dropbox/workspace/2.research/01.Sources/07.Collated/(Geo-Coordinates)/02_KML/WIN.kml", "WIN" ),
]

vis_dir = "/mnt/SSD3/Dropbox/workspace/2.research/_bin/ontologize/run/07_data_visualisation"
img_dir = "../site/img"

# get geo-coordinates

geo_places = {}

synonyms = {}
with open( "synonyms.tsv", "r" ) as r:
	for line in r.readlines():
		line = line.strip()
		vals = line.split("\t")
		original = vals[0]
		synonym  = vals[1]
		if original in synonyms:
			synonyms[ original ] += [ vals[1] ]
		else:
			synonyms[ original ] = [ vals[1] ]

LWH_places = []
WIN_places = []

first_line = None

def get_geo_coordinates( place_id, list_of_maps ):

	for map_name, map_path, prefix in list_of_maps:
		dat_fname = map_path.rsplit("/",1)[1]
		dat_dir   = map_path.rsplit("/",1)[0]
		dat_path  = "%s/^%s.MAPPING.tsv" % ( dat_dir.replace("02_KML","03_^DAT"), dat_fname )
		with open( dat_path, "r" ) as tsv:
			reader = csv.DictReader( tsv, delimiter='\t' )
			for row in reader:

				if " : " in row["kml_path"]:
					label = row["kml_path"].rsplit( " : ", 1 )[1]
					path = row["kml_path"].split( " : " )[0:-1]
					#if " [" in label: label = label.split( " [", 1 )[0]
				else:
					label = row["kml_path"]
					path = []

				new_path = []
				for el in path:
					if not el.startswith( "(" ): new_path.append( el )

				if not prefix=="": tmp = ", ".join( [ prefix ] + new_path + [ label ] )
				else: tmp = ", ".join( new_path + [ label ] )
				if place_id.lower() == tmp.lower():
					return( row["lat"], row["lon"], map_name )

	return "", "", ""

if is_run_places:
	with open( "^index-data.tsv", "w" ) as w:
		for root, dirs, files in os.walk( run_dir ):
			dirs.sort()

			is_first = True

			for fname in sorted( files ):
				if fname.endswith("PEOPLA.tsv") and "03_^DAT" in root and "---" in fname:
					fpath = "%s/%s" % ( root, fname )

					tree_root = root.replace( "03_^DAT", "04_^VIS/^trees" )
					tree_fname = fname.replace(".PEOPLA.tsv",".json")
					tree_fpath = "%s/%s" % ( tree_root, tree_fname )

					src_page = fpath.rsplit("/",1)[1].split(", ",1)[0].replace( "^", "" ).strip().lstrip("0")
					src_desc = fpath.rsplit("/",1)[1].split(", ",1)[1].replace( ".PEOPLA.tsv", " " ).replace( "--- ", " " ).replace( " [+]", "" ).replace( " [~]", "" ).replace( "[===] ", " " ).strip()
					src_vol  = fpath.rsplit("/",3)[1].split(",")[1].replace( "Vol ", "" ).strip().lstrip("0")

					if os.path.isfile( tree_fpath ):
						tree_outpath = "../site/json/trees/{src_vol}.{src_page}.{src_desc}.json".format( src_vol=src_vol.zfill(2), src_page=src_page.zfill(4), src_desc=src_desc.replace(" ","_").lower() )
						cmd = "cp \"{origin}\" \"{dest}\"".format( origin=tree_fpath, dest=tree_outpath )
						os.system( cmd )

					with open( fpath, "r" ) as tsv:
						reader = csv.DictReader( tsv, delimiter='\t' )

						if is_first:
							first_line = next( reader )
							w.write( "\t".join(first_line.keys()) + "\n" )
							is_first = False

						for row in reader:
							place_id = row["place_id"]
							if row["place_id"].startswith("SCO, REN, LWH, "):
								if not place_id in LWH_places: LWH_places.append( place_id )
								w.write( "\t".join(row.values()) + "\n" )
							if row["place_id"].startswith("WIN"):
								if not place_id in WIN_places: WIN_places.append( place_id )

	with open( "kml/LWH/src_points.tsv", "w" ) as w:
		w.write( "\t".join( [ "type", "id", "class", "label", "lat", "lon" ] ) + "\n" )
		for place_id in sorted( LWH_places ):
			if place_id.startswith( "SCO, REN, LWH, " ):
				lat, lon, src = get_geo_coordinates( place_id, LWH_maps )
				geo_places[ place_id ] = lat, lon, src
				if lat != "" and lon != "":
					w.write( "\t".join( [ "point", "", "source", "", lat, lon ] ) + "\n" )
				else:
					if place_id in synonyms:
						for synonym in synonyms[place_id]:
							lat, lon, src = get_geo_coordinates( synonym, LWH_maps )
							geo_places[ place_id ] = lat, lon, src
							if lat != "" and lon != "":
								w.write( "\t".join( [ "point", "", "source", "", lat, lon ] ) + "\n" )
								break
				if lat == "" and lon == "":
					print( place_id )


	with open( "kml/WIN/src_points.tsv", "w" ) as w:
		w.write( "\t".join( [ "type", "id", "class", "label", "lat", "lon" ] ) + "\n" )
		for place_id in sorted( WIN_places ):
			if place_id.startswith( "WIN" ):
				lat, lon, src = get_geo_coordinates( place_id, WIN_maps )
				geo_places[ place_id ] = lat, lon, src
				if lat != "" and lon != "":
					w.write( "\t".join( [ "point", "", "source", "", lat, lon ] ) + "\n" )


	os.system( "python3 kml_to_tsv.py" )


if is_run_people:
	with open( "^index-people.tsv", "w" ) as w:
		is_first = True

		for root, dirs, files in os.walk( run_dir ):
			dirs.sort()

			for fname in sorted( files ):
				if fname.endswith("PEOPLA.tsv") and "03_^DAT" in root and "---" in fname:
					fpath = "%s/%s" % ( root, fname )

					with open( fpath, "r" ) as tsv:
						reader = csv.DictReader( tsv, delimiter='\t' )

						if is_first:
							first_line = next( reader )
							w.write( "\t".join(first_line.keys()) + "\n" )
							is_first = False

						for row in reader:
							pers_guid = row["pers_id_global"]
							if pers_guid != "":
								w.write( "\t".join(row.values()) + "\n" )


# render map images

if is_render_images:
	os.system( "rm ../site/img/maps/lwh/*.png" )

	for place_id in sorted( LWH_places ):
		if is_debugging:
			if not "Auchinbathie" in place_id: continue

		lat, lon, src = geo_places[place_id]

		if lat == "" or lon == "": continue

		with open( "kml/tmp.tsv", "w" ) as w:
			w.write( "\t".join( [ "type", "id", "class", "label", "lat", "lon" ] ) + "\n" )
			w.write( "\t".join( [ "point", "", "highlight", "", lat, lon ] ) + "\n" )

		cmd = """Rscript --vanilla {vis_dir}/02_draw-map.R -b "kml/LWH/ALL.tsv" -s "kml/styles.tsv" -d "{img_dir}/maps/lwh" -a "kml/tmp.tsv" -o "{img_fname}.png" """.format( vis_dir=vis_dir, img_dir=img_dir, img_fname=place_id.replace(", ","_").replace(" ","-") )
		print( cmd )
		os.system( cmd )


	os.system( "rm ../site/img/maps/win/*.png" )

	for place_id in sorted( WIN_places ):

		with open( "kml/tmp.tsv", "w" ) as w:
			w.write( "\t".join( [ "type", "id", "class", "label", "lat", "lon" ] ) + "\n" )
			lat, lon, src = geo_places[place_id]
			w.write( "\t".join( [ "point", "", "highlight", "", lat, lon ] ) + "\n" )

		cmd = """Rscript --vanilla {vis_dir}/02_draw-map.R -b "kml/WIN/ALL.tsv" -s "kml/styles.tsv" -d "{img_dir}/maps/win" -a "kml/tmp.tsv" -o "{img_fname}.png" """.format( vis_dir=vis_dir, img_dir=img_dir, img_fname=place_id.replace(", ","_") )
		print( cmd )
		os.system( cmd )

# add geo-coordinates into the tsv file... necessary? should probably be added to a separate file...

with open( "^index-data.tsv", "r" ) as tsv, open( "^tmp.tsv", "w" ) as tmp:
	reader = csv.DictReader( tsv, delimiter='\t' )
	fieldnames = reader.fieldnames + ["mapping_ref"]
	writer = csv.DictWriter( tmp, delimiter='\t', fieldnames=fieldnames )
	writer.writeheader()
	for row in reader:
		if row["place_id"] in geo_places:
			lat, lon, src = geo_places[row["place_id"]]
			row["place_longitude"] = lat
			row["place_latitude"]  = lon
			row["mapping_ref"]     = src

		writer.writerow(row)

os.system( "mv ^tmp.tsv ^index-data.tsv" )

os.system( "python3 image-modify.py" )
