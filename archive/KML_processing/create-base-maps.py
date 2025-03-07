import os
import csv
from collections import defaultdict
from collections import OrderedDict


vis_dir = "/mnt/SSD3/Dropbox/workspace/2.research/_bin/ontologize/run/07_data_visualisation"
img_dir = "../site/img"


cmd = """Rscript --vanilla {vis_dir}/02_draw-map.R -b "kml/SCO/ALL.tsv" -s "kml/styles.tsv" -d "{img_dir}/maps" -o "base-sco.png" """.format(
			vis_dir=vis_dir,
			img_dir=img_dir )

print( cmd )

os.system( cmd )


cmd = """Rscript --vanilla {vis_dir}/02_draw-map.R -b "kml/REN/ALL.tsv" -s "kml/styles.tsv" -d "{img_dir}/maps" -o "base-ren.png" """.format(
			vis_dir=vis_dir,
			img_dir=img_dir )

print( cmd )

os.system( cmd )


cmd = """Rscript --vanilla {vis_dir}/02_draw-map.R -b "kml/WIN/ALL.tsv" -s "kml/styles.tsv" -d "{img_dir}/maps" -o "base-win.png" """.format(
			vis_dir=vis_dir,
			img_dir=img_dir )

print( cmd )

os.system( cmd )


cmd = """Rscript --vanilla {vis_dir}/02_draw-map.R -b "kml/LWH/ALL.tsv" -s "kml/styles.tsv" -d "{img_dir}/maps" -o "base-lwh.png" """.format(
			vis_dir=vis_dir,
			img_dir=img_dir )

print( cmd )

os.system( cmd )
