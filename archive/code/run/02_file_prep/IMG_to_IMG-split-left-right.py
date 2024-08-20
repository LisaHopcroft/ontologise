import glob
import os
from PIL import Image


def split_large_images( run_dir ):
	pattern = "%s/01_IMG/*.JPG" % run_dir
	pattern = pattern.replace( "[","<" ).replace( "]",">" )
	pattern = pattern.replace( "<","[[]" ).replace( ">","[]]" )
	print( pattern )
	filelist = glob.glob(pattern)
	for filepath in sorted( filelist ):
		print( filepath )
		if "-L.jpg" in filepath: continue
		if "-R.jpg" in filepath: continue
		im = Image.open(filepath)
		width, height = im.size
		print( width, height )
		if not os.path.exists( "%s/01_IMG/@original" % run_dir ): os.mkdir( "%s/01_IMG/@original/" % run_dir )
		if width>4000:
			im.crop( (0, 0, width/1.9, height)).save(filepath.replace(".JPG","-L.jpg") )
			im.crop( (width/2.1, 0, width, height)).save(filepath.replace(".JPG","-R.jpg") )
			cmd = "mv \"%s\" \"%s\"" % ( filepath, filepath.replace( "01_IMG/","01_IMG/@original/" ) )
			print( cmd )
			os.system( cmd )


for root, dirs, files in os.walk( "/media/michael/SSD3/Dropbox/workspace/2.research/01.Primary/01.Manuscripts/01.Archives/02.ENGLAND & WALES/TNA, National Archives (UK)/CO, Colonial Office/114, British Guiana, Sessional Papers, 1805-1965/2, Berbice, Court of Policy & Criminal Justice, 1811-5" ):
	for dirname in dirs:
		if dirname == "01_IMG":
			print( "Splitting..." )
			split_large_images( root )
