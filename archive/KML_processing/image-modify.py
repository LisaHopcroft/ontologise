import os
import glob


# trim

for fname in glob.glob( "../site/img/maps/lwh/*.png" ):
	if ".mod.png" in fname: continue
	cmd = "convert %s -trim  %s" % ( fname, fname.replace(".png",".mod.png" ) )
	os.system( cmd )

for fname in glob.glob( "../site/img/maps/base*.png" ):
	if ".mod.png" in fname: continue
	cmd = "convert %s -trim  %s" % ( fname, fname.replace(".png",".mod.png" ) )
	os.system( cmd )


# watermark

for fname in glob.glob( "../site/img/maps/lwh/*.mod.png" ):
	cmd = "composite -watermark 15% -gravity SouthWest -geometry +20+20 {watermark} {in_file} {out_file}".format( watermark="../site/img/watermark.png", in_file=fname, out_file=fname )
	os.system( cmd )

for fname in glob.glob( "../site/img/maps/base*.mod.png" ):
	cmd = "composite -watermark 15% -gravity SouthWest -geometry +20+20 {watermark} {in_file} {out_file}".format( watermark="../site/img/watermark.png", in_file=fname, out_file=fname )
	os.system( cmd )
