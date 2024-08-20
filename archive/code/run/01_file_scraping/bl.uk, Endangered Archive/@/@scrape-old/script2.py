text_file = open(r"D:\cloud\workspace\2.academia\0.Administrative\Scripts\download-these.html", "w")

for x in range(1, 558):
   x_str = ""
   if x < 10:
      x_str = "00" + str(x);
   elif x < 100:
      x_str = "0" + str(x);
   else:
      x_str = str( x )
   text_file.write( "<a href='http://eap.bl.uk/EAPDigitalItems/EAP345/EAP345_1-345_Page" + x_str + "_" + x_str + "_L.jpg'>" + str(x) + "</a><br/>\n" )

text_file.close()
