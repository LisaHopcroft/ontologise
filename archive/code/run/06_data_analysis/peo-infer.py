import os
import csv


run_dir = "/mnt/SSD3/Dropbox/workspace/2.research/01.Sources/01.Primary/01.Manuscripts/00.WWW/FS, FamilySearch"


for root, dirs, files in os.walk( run_dir ):
	for fname in files:
		if fname.endswith( ".PEOPLA.tsv" ) and fname.startswith( "^" ) and "03_^DAT" in root:

			inferences = []

			with open( "%s/%s" % ( root, fname ), "r" ) as tsv:
				reader = csv.DictReader( tsv, delimiter='\t' )
				for row in reader:
					if row["place_id"].startswith( "WIN" ):
						inferences.append( { 
							"pers_id": row["pers_id"], 
							"pers_id_context": row["pers_id_context"], 
							"src_filepath": row["src_filepath"],
							"key": "WIN",
							"value": 1 } )
					
			if inferences:
				writepath = "%s/%s" % ( root, fname.replace(".PEOPLA.tsv",".PEO-INFERRED.tsv") )
				with open( writepath, "w" ) as tsv:		
					dict_writer = csv.DictWriter( tsv, inferences[0].keys(), delimiter='\t' )
					dict_writer.writeheader()
					dict_writer.writerows( inferences )
				print( writepath )
