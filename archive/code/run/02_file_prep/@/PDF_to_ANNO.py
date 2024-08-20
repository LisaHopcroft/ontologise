import poppler
import sys
import urllib
import os
import glib


#run_dir = "/media/michael/Files/Dropbox/workspace/2.research/1.Material"
run_dir = "/media/michael/Files/Dropbox/workspace/2.research/01.Primary/03.Publications/(B), Newspapers/(A), GBR/InvC, Inverness Courier (est.1817)"


for root, dirs, files in os.walk( run_dir ):
	for fname in files:
		if fname.endswith(".pdf"):
			path = root + "/" + fname
			f = open(path, 'r')

			#exit
			if "#" in path:
				continue

			try:
				document = poppler.document_new_from_file( "file:///" + path, None )
			except glib.GError:
				#print path
				print "CORRUPTED"
				continue

			n_pages = document.get_n_pages()

			annots_text = ""
			all_annots = 0
			for i in range(n_pages):
				page = document.get_page(i)
				annot_mappings = page.get_annot_mapping()
				num_annots = len(annot_mappings)
				if num_annots > 0:
					for annot_mapping in annot_mappings:
						if  annot_mapping.annot.get_annot_type().value_name != 'POPPLER_ANNOT_LINK':
							all_annots += 1
							annots_text = annots_text + '----------------------------------------\npage: {0}\ncoordinates: {1}\nmodified: {2}\ntype: {3}\ncontent: {4}\n'.format(
								i+1, 
								annot_mapping.annot, 
								str(annot_mapping.annot.get_modified()).replace("D:",""), 
								annot_mapping.annot.get_annot_type().value_nick, 
								annot_mapping.annot.get_contents())

			if all_annots > 0:
				branch_dir = path.rsplit("/",2)[0] #move up two dirs
				nested_dir = path.rsplit("/",2)[1]
				#print "branch:" + branch_dir
				#print "nested:" + nested_dir
				if nested_dir.startswith( "0" ): #i.e. not really nested at all...
					nested_dir = ""
				else:
					branch_dir = os.path.dirname( branch_dir )
					nested_dir = "/" + nested_dir

				#print path
				writefile = root + '/^%s.anno' % ( fname )
				print "file:" + writefile
				f = open( writefile, 'w' )
				f.write( annots_text )
				f.close()
				print str(all_annots) + " annotation(s) found"
			#else:
			#	print ""
