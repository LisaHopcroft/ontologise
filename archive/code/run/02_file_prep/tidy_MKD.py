import sys
import os

sys.path.append("/media/michael/SSD3/Dropbox/workspace/2.research/_bin")
import ontologize.modules.data_transformation.all as prep


rundir = "/media/michael/SSD3/Dropbox/workspace/2.research/01.Primary/01.Manuscripts/01.Archives/01.SCOTLAND/NRAS, National Register of Archives Scotland/2696, FRASER of Reelig/Vol41, Wastebook - re. Pln 28, 1805-11/02_TXT"


for root, dirnames, filenames in os.walk( rundir ):

	for filename in filenames:

		filepath = "%s/%s" % ( root, filename )

		if prep.is_MKD( filepath ):

			rel_img_path = ""

			with open( filepath, "r" ) as r:
				lines = r.readlines()

			for line in lines:
				if line.startswith("[img]"):
					rel_img_path = line.replace("[img]: ","").strip()

			with open( filepath, "w" ) as w:
				for line in lines:
					if line == "![img]\n" and rel_img_path != "":
						line = "![img](%s)\n" % rel_img_path
					if line.startswith( "[img]: " ) and rel_img_path != "":
						line = "[END]"

					if line.startswith( "======" ):
						line = "================================================================================\n"
					elif line.startswith( "---------------" ):
						line = "--------------------------------------------------------------------------------\n"
					elif line.strip().startswith( "---" ) and line.strip().endswith("---"):
						num_chars = len( line.strip() )
						num_spaces = 80 - num_chars # notional line-length is 80...
						line = " "*(num_spaces/2) + line.strip() + "\n"
					elif line.strip().startswith( "-#-" ) and line.strip().endswith("-#-"):
						line = "-#- %s -#-" % (" ".join(line.replace("-#-","").strip())) + "\n"
						num_chars = len( line.strip() )
						num_spaces = 80 - num_chars # notional line-length is 80...
						line = " "*(num_spaces/2) + line.strip() + "\n"

					'''elif line == "DEATHS\n":
						line = "--- DEATHS ---\n#[BDM-DEATH]\n"
					elif line == "MARRIAGES\n":
						line = "--- MARRIAGES ---\n#[BDM-MARRIAGE]\n"
					elif line == "BIRTHS\n":
						line = "--- BIRTHS ---\n#[BDM-BIRTH]\n"'''
					if line.startswith( "###[" ):
						line = line.replace( "###[", "###\t[" )
					if line.startswith( "###>" ):
						line = line.replace( "###>", "###\t>\t" )
					if line.startswith( "###::" ):
						line = line.replace( "###::", "###\t::" )
					if line.startswith( "###DIED" ):
						line = line.replace( "###DIED", "###\t\tDIED" )
					if line.startswith( "###AT" ):
						line = line.replace( "###AT", "###\t\tAT" )
					if line.startswith( "###RE" ):
						line = line.replace( "###RE", "###\t\tRE" )
					if line.startswith( "###EX" ):
						line = line.replace( "###EX", "###\t\tEX" )
					if line.startswith( "###BORN" ):
						line = line.replace( "###BORN", "###\t\tBORN" )
					if line.startswith( "###OCC" ):
						line = line.replace( "###OCC", "###\t\tOCC" )
					if line.startswith( "###WILL" ):
						line = line.replace( "###WILL", "###\t\tWILL" )
					if line.startswith( "###MEMORIAL" ):
						line = line.replace( "###MEMORIAL", "###\t\tMEMORIAL" )
					if line.startswith( "###MARRIED" ):
						line = line.replace( "###MARRIED", "###\t\tMARRIED" )
					if line.startswith( "###+[" ):
						line = line.replace( "###+[", "###\t+[" )
					if line.startswith( "###\t+[" ):
						line = line.replace( "###\t+[", "###\t+\t[" )
					if line.startswith( "###\t::[" ):
						line = line.replace( "###\t::[", "###\t::\t[" )

					line = line.replace( "\tOCC[", "\tOCC-ROLE[" ).replace( "-IN[", ":[" ).replace( "]IN[", "]:[" )

					'''if line.startswith( "###" ):
						if not "::" in line:
							line = line.replace( "]@[", "\n###\t\t\t@[" )
							line = line.replace( "###\t\tAT[", "###\t\tAT\n###\t\t\t@[" )'''

					w.write( line )
