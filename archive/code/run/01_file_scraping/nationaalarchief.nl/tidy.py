import glob
import os


def get_approx_path_if_exists( wpath ):
	if len( glob.glob( wpath + ", *" ) ) > 0:
		print( glob.glob( wpath + ", *" )[0] )
		return( glob.glob( wpath + ", *" )[0] )
	return wpath

base_dir = "/media/michael/Files/Dropbox/workspace/2.research/01.Primary/03.Maps etc/00.WWW/NAN, Nationaal Archief (NED)"

for fpath in glob.glob( "/home/michael/Downloads/NL-HaNA_*" ):
	grp = fpath.split( "NL-HaNA_", 1 )[1].rsplit( "_", 1 )[0]
	item = fpath.rsplit("_",1)[1].replace(".jpg","")

	grp = grp.replace("4.VEL","VEL")
	
	dest_path = "%s/%s/%s" % ( base_dir, grp, item )
	print( dest_path )

	if not os.path.exists( dest_path ):
		dest_path = get_approx_path_if_exists( dest_path )

	dest_path = dest_path + "/01_IMG"
	if not os.path.exists( dest_path ):
		os.mkdir( dest_path )

	os.system( "mv \"%s\" \"%s\"" % ( fpath, dest_path ) )
