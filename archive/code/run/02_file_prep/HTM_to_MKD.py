import os
import fileinput
import sys
#import html2text
import re
sys.path.append("/mnt/nas3/dropbox/workspace/2.research/_bin")
#import ontologize.modules.util.all as util

#html2text.BODY_WIDTH = 0
override = False

IS_FIRST_TABLE = True
IS_IN_TABLE = False

# --------------------------------------------------------- #
# Convert HTML (01) to MKD (02)
# --------------------------------------------------------- # 

def get_collection_dirpath( filepath ):
	if "/01_" in filepath:
		col_dir = filepath.split( "/01_" )[0]
		sub_dir = filepath.split( "/01_" )[1]
		if sub_dir.count( "/" ) == 0:
			return False, False # must have matched on trailing filename... not what we want...
		if sub_dir.count( "/" ) == 1:
			return col_dir, "" # no sub dir
		if sub_dir.count( "/" ) == 2:
			return col_dir, sub_dir.split("/")[1] # return middle dir
		if sub_dir.count( "/" ) > 2:
			return False, False # must have matched earlier directory... not what we want
	return False, False


run_dir = "/mnt/nas3/dropbox/workspace/2.research/04.WWW-Publ/(A), WWW Resources/S&H, Slaves and Highlanders (D.ALSTON)/@20190325, Biographies, Scots in Surinam"

# first rename any .htm files as .html
for root, dirs, files in os.walk( run_dir ):
	for filename in files:
		filepath = root + "/" + filename
		if filename.endswith(".htm"):
			cmd = "mv \"%s\" \"%s\"" % ( escape_filepath(filepath), escape_filepath(filepath)+"l" )	
			os.system( cmd )

for root, dirs, files in os.walk( run_dir ):
	for filename in files:
		filepath = root + "/" + filename
		if filename.endswith( ".html" ) and not "_search" in root:
			col_dir, sub_dir = get_collection_dirpath( filepath )

			if col_dir:
				if sub_dir:
					filename = "%s/%s" % ( sub_dir, filename ) 

				conversion_path1 = "%s/02_MKD/%s.mkd" % ( col_dir, filename )
				conversion_path2 = "%s/02_TXT/%s.mkd" % ( col_dir, filename )
				conversion_path3 = "%s/02_MKD/%s.txt" % ( col_dir, filename )
				conversion_path4 = "%s/02_TXT/%s.txt" % ( col_dir, filename )

				if not os.path.exists( conversion_path1 ) and not os.path.exists( conversion_path2 ) and not os.path.exists( conversion_path3 ) and not os.path.exists( conversion_path4 ):
					print( "No conversion exists..." )

					# make pre-modifications...
					tmp_path = filepath + ".tmp"

					with open(filepath, 'r') as f:
						data = f.read()
						f.close()
					with open(tmp_path, 'w') as f:
						data = data.replace('\r', ' \r\n') # Sort out whitespace issues
						data = data.replace('  \r', ' \r') # Sort out whitespace issues
						data = data.replace('&amp;', '&') # HTML2TXT not handing this for some reason...
						f.write( data )
						f.close()

					with open(tmp_path, 'r') as f:
						lines = f.readlines()
						f.close()
					with open(tmp_path, 'w') as f:
						IS_FIRST_TABLE = True
						loopnum = 0

						# Remove <p> tags from inside <td> tags
						for line in lines:
							loopnum = loopnum + 1
							if "<table" in line:
								if IS_IN_TABLE:
									IS_FIRST_TABLE = False
								IS_IN_TABLE = True
							if "</table" in line:
								IS_IN_TABLE = False
							if IS_IN_TABLE and not IS_FIRST_TABLE:
								line = line.replace('\n', ' ')
								line = re.sub( "<p.*?>", "", line, flags=re.I )
								line = re.sub( "</p>","", line, flags=re.I )
								line = re.sub( "<h1.*?>", "", line, flags=re.I )
								line = re.sub( "</h1>","", line, flags=re.I )
								line = re.sub( "<br>"," [n]\n", line, flags=re.I )

							f.write( line )
						f.close()

					# convert modified html to mkd...

					writedir = "%s/02_TXT" % ( col_dir )
					if not os.path.exists( writedir ):
				 	   os.makedirs( writedir )
			
					cmd = "html2text '" + filepath + "' > '" + conversion_path2 + "'"# --body-width=0 --decode-errors=ignore"
					print( cmd )
					os.system( cmd )

					# make some final modifications...
					path = root + "/" + filename
					tmp_path = path + ".tmp"
					with open(path, 'r') as f:
						data = f.read()
					with open(tmp_path, 'w') as f:
						data = data.replace('&amp;', '&')
						f.write(data)
					os.unlink(path)
					os.rename(tmp_path, path)
