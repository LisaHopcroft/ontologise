text_file = open(r"D:\cloud\workspace\2.academia\0.Administrative\Scripts\download-these.html", "w")

for x in range(574, 937):
        text_file.write( "<a href='http://eap.bl.uk/EAPDigitalItems/EAP345/EAP345_2-345_Page" + str(x) + "_" + str(x) + "_L.jpg'>" + str(x) + "</a><br/>\n" )
	
text_file.close()
