import os
from uuid import UUID


run_dir = "/mnt/SSD3/Dropbox/workspace/2.research/01.Sources/01.Primary/02.Publications/(A), Books, Pamphlets &c/[BY-SUBJECT]/(WIN)"


def is_valid_uuid(uuid_to_test, version=4):
    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test
    
    
local_ids = []


for root, dirs, files in os.walk( run_dir ):
	for fname in files:
		if fname == "peo_guid.tsv":
			with open( "%s/%s" % ( root, fname ), "r" ) as r:
				i = 1
				for line in r.readlines():
					#print( line )
					if not "\t" in line: print( "LINE %s: no tab" % i )
					else:
						line = line.strip()
						local_id = line.split("\t")[0]
						global_id = line.split("\t")[1]
						#print( "\t".join( [ local_id, global_id ] ) )
						if local_id in local_ids: print( "LINE %s: duplicate local id: %s" % (i,local_id) )
						local_ids.append( local_id )
						if not is_valid_uuid( global_id ) and global_id != ".": print( "LINE %s: bad uuid" % i )
					i+=1
