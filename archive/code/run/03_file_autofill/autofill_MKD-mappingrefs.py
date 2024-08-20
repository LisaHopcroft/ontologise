import os

run_dir = "../"

at_val = ""
kml_val = ""

is_pin_tag_exists = False
is_place_tag_exists = False


for root, dirs, files in os.walk( run_dir ):
	for fname in files:

		if not ( fname.endswith(".txt") and "02_TXT" in root ): continue

		print( "-------------------------------------------------" )
		print( fname )

		fpath = "%s/%s" % ( root, fname )

		lines = []

		with open( fpath, "r" ) as r:
			lines = r.readlines()

		is_content_area = False
		title = ""
		tag = ""
		is_tag_line = False

		with open( fpath, "w" ) as w:
			for line in lines:

				if line.startswith( "##AT:" ):
					at_val = line.replace("##AT:","").strip()
					kml_val = at_val.replace("SCO, ","OS25-1:").replace(", ",":")

				if "![img]" in line:
					is_content_area = True

				# BLANK
				
				#if line.startswith( "###\t@[" ): continue # RUN ONCE - as values are hand edited.
				#if line.startswith( "###\t\t\tMAP[" ): continue
				#if line.startswith( "###\t\t\t^"): continue

				# FILL
				if is_content_area:

					# FILL IN PLACE IDs (1)

					if line.startswith("\t") and not line.startswith("\t\t") and title == "":
						title = line.strip()
						is_place_tag_exists = False
						print( title )

					if line.startswith("###\t@["): is_place_tag_exists = True

					if line=="\n" and not title.strip() == "" and not is_place_tag_exists:
						w.write( "###\t@[%s, %s]\n" % ( at_val, title ) )
						title = ""

					# FILL IN PIN LINES (2)

					if line.startswith( "###\t@[" ):
						tag = line.rsplit(", ",1)[1].strip()[:-1]
						title = line.rsplit(", ",1)[1].strip()[:-1]
						is_pin_tag_exists = False
						print( tag )

					if line.startswith("###\t\t\tMAP["): is_pin_tag_exists = True

					if line=="\n" and tag.strip() != "" and not is_pin_tag_exists:
						w.write( "###\t\t\tMAP[%s:%s]\n" % ( kml_val, tag ) )
						tag = ""
						

				w.write( line )

