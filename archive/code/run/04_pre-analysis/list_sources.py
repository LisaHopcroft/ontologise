import os


start_dir = "/mnt/SSD3/Dropbox/workspace/2.research/01.Sources"

list_of_dirs = []

for root, dirs, files in os.walk(start_dir):
	for fname in files:
		if "##DEMERARA1823" in fname:
			list_of_dirs.append( root )
			
with open( "/mnt/SSD3/Dropbox/workspace/2.research/02.Intermediary/DEMERARA1823.tsv", "w" ) as w:

	for dirname in sorted( list_of_dirs ):

		for root, dirs, files in os.walk( dirname ):
			for fname in sorted( files ):
				if "02_TXT" in root and fname.endswith(".txt"):
					fpath = "%s/%s" % ( root, fname )
					first_src = True
					with open( fpath, "r" ) as r:
						src_type = ""
						date = ""
						auth = ""
						pris = ""
						word_count = 0
						for line in r.readlines():
							if not line.startswith(">") and not line.startswith("#"):
								word_count += len(line.split())
							if line.startswith("##DATE:"): date = line.replace("##DATE:","").strip()
							if line.startswith("##AUTH:"): auth = line.replace("##AUTH:","").strip()
							if line.startswith("##PRIS:"): pris = line.replace("##PRIS:","").strip()
							if line.startswith("[END]") or ( line.startswith("#[") and not first_src ):
								first_src = False
								w.write( "\t".join( [ 
									dirname.replace(start_dir,""), 
									fpath.replace(dirname,""), 
									src_type, 
									date,
									pris, 
									auth,
									str(word_count) ] ) + "\n" )
							if line.startswith("#["): 
								first_src = False
								src_type = line.strip().replace("#[","").replace("]","")
								auth = ""
								word_count = 0
