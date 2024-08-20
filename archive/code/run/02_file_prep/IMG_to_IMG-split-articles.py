import cv2
import numpy as np
import glob
import copy
import os
import collections
import math
import time
import datetime


lines = []
kernel2 = np.ones((2,2),np.uint8)
kernel4 = np.ones((4,4),np.uint8)
kernel5 = np.ones((5,5),np.uint8)
kernel6 = np.ones((6,6),np.uint8)

linewidth 		= 10
linewidth_el 	= 0

run_path 	= "/media/michael/SSD3/Dropbox/workspace/2.research/01.Material/01.Primary/01.Manuscripts/00.WWW/NL-HaNA, Nationaal Archief/1.05.21, Dutch Series Guyana/(5), Newspapers/(5.1), Essequebo & Demerara Royal Gazette, 1811-15"

 
def get_index_in_range(mydict, l, r):
	for key, vals in mydict.items(): 
		key = int(key[0]) #x
		if key>= l and key<= r: 
			return key
	return None

 
def count_range(mylist, l, r):
	for key in mylist: 
		key = int(key)
		if key>= l and key<= r: 
			return key
	return None

 
def col_trans( index ):
	alphabet = [ "A","B","C","D","E","F" ]
	return alphabet[ index ]


def is_first_page( fpath ):
	return "_0001." in fpath or fpath.endswith("-0.jpg")


def get_whitespace_coords( img ):
	tmp = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	tmp = 255*(tmp < 128).astype(np.uint8) # To invert the text to white
	coords = cv2.findNonZero(tmp) # Find all non-zero points (text)
	x, y, w, h = cv2.boundingRect(coords) # Find minimum spanning bounding box
	return ( y, y+h, x, x+w )


def get_blackspace_coords( img ):
	tmp = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	coords = cv2.findNonZero(tmp) # Find all non-zero points (text)
	x, y, w, h = cv2.boundingRect(coords) # Find minimum spanning bounding box
	return ( y, y+h, x, x+w )


def pre_ocr_enhancements( img, el_loop ):
	el_height, el_width, el_channels = img.shape

	# TODO: further skew correcting?

	# remove borders
	# shave off the lines...
	top = 0
	btm = el_height-linewidth_el
	if el_loop > 1:
		top = linewidth_el
	img = img[ top:btm, 0:el_width ]

	img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	img = cv2.fastNlMeansDenoising(img, None,10,7,21)#,10,7,21),4,7,21)
	img = cv2.fastNlMeansDenoising(img, None,10,7,21)#,10,7,21),4,7,21)
	img = cv2.fastNlMeansDenoising(img, None,10,7,21)#,10,7,21),4,7,21)
	img = cv2.GaussianBlur(img,(5,5),0)
	#img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
	img = cv2.copyMakeBorder(img,20,20,20,20,cv2.BORDER_CONSTANT,value=[255,255,255]) # add a white margin
	return img


def is_light_area( img, contour ):
	return False #TODO


def is_acceptable_deviation( x1, y1, x2, y2 ):
	a = abs(y2-y1)
	max_o = ( a * math.atan(math.radians(3)) ) + 30 # add some leeway
	o = abs(x2-x1)
	return( o < max_o )


def is_centred( x, w, total_width ):
	left_gap = x
	left_gap_pct = (left_gap/total_width)*100
	right_gap = total_width-(x+w)
	right_gap_pct = (right_gap/total_width)*100
	diff_left_right = abs(left_gap_pct-right_gap_pct)
	
	if left_gap_pct<15 and right_gap_pct<15:
		return True

	if min(left_gap_pct,right_gap_pct)==0: # avoid division by zero
		if max(left_gap_pct,right_gap_pct)<10:
			return True
		else:
			return False

	if max(left_gap_pct,right_gap_pct)/min(left_gap_pct,right_gap_pct) < 1.5:
		return True

	return False


log_path 	= "./IMG_to_IMG-split-articles.py.log"
is_override = False
is_debug 	= False


def get_date_from_fname( fname ):
	if "_" in fname:
		return fname.split("_")[0]
	if "-" in fname:
		return fname.split("-")[0]


def perform_split_articles( conv_files, path, expected_columns ):
	for fname in conv_files:
		if os.path.getsize( fname ) == 0: continue
		if "@" in fname: continue

		log_records = []

		t0 = time.time()
		debugpath = fname.replace(path,"/home/michael/Desktop/tmp/ocr")

		is_first_page_val = False

		print( "================================================================" )
		print( fname )

		filename = fname.rsplit("/",1)[1]
		src_date = None

		# some custom detail retrieval
		if filename.startswith( "NL-HaNA_" ): 
			identifier = filename.rsplit("_",1)[1].split(".",1)[0]
			print( identifier )
			match_pattern = "%s/%s*" % ( fname.rsplit("/",1)[0].replace("01_IMG","02_TXT"), identifier )
			txtfiles = glob.glob( match_pattern )
			for txtfile in txtfiles:
				src_date = txtfile.rsplit(", ",1)[1].split(".",1)[0]
			if len(txtfiles) > 0:
				is_first_page_val = True
		else:
			src_date = get_date_from_fname( filename )
			print( src_date )

		glob_txt = fname.replace( "/01_IMG", "/01_IMG/@ocr" ).replace( ".jpg","*" )
		if ( len(glob.glob( glob_txt) )>0 ) and not is_override:
			continue

		if not os.path.exists( debugpath.rsplit("/",1)[0] ): os.mkdir( debugpath.rsplit("/",1)[0] )
	 
		img = cv2.imread( fname )
		img = cv2.resize( img, (0,0), fx=2, fy=2, interpolation = cv2.INTER_CUBIC )


		# remove whitespace
		coords = get_whitespace_coords( img )
		img = img[ coords[0]:coords[1], coords[2]:coords[3] ]
		height, width, channels = img.shape


		# British Newspaper Archive modifications
		'''
		# shave off the bottom watermark area
		img = img[0:height-110, 0:width]
		height, width, channels = img.shape
		'''

		# pre-houghlines enhancements
		mod = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
		mod = cv2.fastNlMeansDenoising(mod, None, 10, 7, 21)
		mod = cv2.fastNlMeansDenoising(mod, None, 10, 7, 21) #,10,7,21),4,7,21)
		mod = cv2.fastNlMeansDenoising(mod, None, 10, 7, 21) #,10,7,21),4,7,21)
		mod = cv2.GaussianBlur(mod,(5,5),0)
		mod = cv2.adaptiveThreshold(mod, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)
		mod = cv2.dilate(mod,kernel2,iterations=1)
		mod = cv2.Canny(mod,50,100,apertureSize=7)
		mod = cv2.dilate(mod,kernel5,iterations=1)
		#print( debugpath.replace(".jpg",".edges.jpg") )
		if is_debug:
				
			print( "- Writing %s" % ( debugpath.replace(".jpg",".edges.jpg" ) ) )
			cv2.imwrite(debugpath.replace(".jpg",".edges.jpg"),mod)


		if not src_date: continue

		# get the number of expected columns
		for key, val in expected_columns.items():
			if src_date.isnumeric():
				if int(src_date) < int(key):
					num_expected_cols = int(val)
			else:
				num_expected_cols = int(val)

		num_expected_lines = num_expected_cols-1

		reasonable_column_width = (width/num_expected_cols)/2
		print( "- Image width: %s" % width )
		print( "- Expected columns: %s" % num_expected_cols )
		print( "- Reasonable column width: %s" % reasonable_column_width )
	 
		# STEP 1. if first page, get the major horizontal lines
		major_horizontal_y = 0

		if is_first_page( fname ) or is_first_page_val:
			print( "- **Processing first page...**" )
			debugimg = copy.deepcopy(img) 
			rows = []
			lines = cv2.HoughLinesP(image=mod, rho=1, theta=np.pi/60, threshold=5, minLineLength=500, maxLineGap=5)
			if lines is not None:
				for line in lines:
					x1,y1,x2,y2 = line[0]
					angle = np.arctan2(y2-y1,x2-x1)*180.0/np.pi
					if abs(angle)==0.0 and y1>300 and y1<height/5: # i.e. horizontal, and not right at the top but within the top fifth
						rows.append( y1 )
						cv2.line(debugimg,(x1,y1),(x2,y2),(0,0,255),10)
	 
			if rows:
				rows.sort()
				first_row = rows[0]
				mod = mod[first_row+120:height, 0:width]
				img = img[first_row+120:height, 0:width]
				print( "- Major horizontal: %s" % first_row )
				major_horizontal_y = first_row+120
			else:
				print( "- Major horizontal: *** NONE FOUND ***" )

			if is_debug:
				print( "- Writing %s" % ( debugpath.replace(".jpg",".debug-horizontal.jpg") ) )
				cv2.imwrite(debugpath.replace(".jpg",".debug-horizontal.jpg"),debugimg)
	 

		# STEP 2. get the major vertical lines

		debugimg = copy.deepcopy(img) 
		line_groups = {}
		lines1 = cv2.HoughLinesP(image=mod, rho=2, theta=np.pi/30, threshold=1, minLineLength=300, maxLineGap=5)
		lines2 = cv2.HoughLinesP(image=mod, rho=2, theta=np.pi/10, threshold=1, minLineLength=100, maxLineGap=2)
		lines = list(lines1)+list(lines2)
		lines = np.array(lines)

		if lines is not None:

			# filter values and convert to a sorted list
			lines_list = []
			for line in lines:
				x1,y1,x2,y2 = line[0]
				line_angle = np.arctan2(y2-y1,x2-x1)*180.0/np.pi
				if x1 < reasonable_column_width or x1 > (width-reasonable_column_width): continue # exclude lines close to the edges
				if not ( abs(line_angle)>85.0 and abs(line_angle)<95.0 ): continue # excluside lines outwith 5 degrees of vertical
				cv2.line(debugimg,(x1,y1),(x2,y2),(0,0,255),10)
				if y1>y2:
					y1,y2=y2,y1 #swap them
					x1,x2=x2,x1 #swap them
				midpoint = ( int((x1+x2)/2), int((y1+y2)/2) ) # add a midpoint and quarterpoints, to help the re-grouping
				lines_list.append( ( x1,y1 ) )
				lines_list.append( ( int((x1+midpoint[0])/2), int((y1+midpoint[1])/2) ) )
				lines_list.append( midpoint )
				lines_list.append( ( int((midpoint[0]+x2)/2), int((midpoint[1]+y2)/2) ) )
				lines_list.append( ( x2,y2 ) )

			lines_list = sorted(lines_list, key=lambda tup: (tup[1],tup[0])) # sort by y1, then x1
					
			# group the line coordinates which are closely aligned
			loop_count = 0
			loop_count_matched = 0
			loop_count_non = 0
			for x,y in lines_list:
				loop_count += 1
				# test the alignment
				matched_key = False
				for key in line_groups:
					nearest_x = key[0]
					nearest_y = key[1]

					dist = math.sqrt( ((x-nearest_x)**2)+((y-nearest_y)**2) )
					if dist>(height*.33):
						continue # too big a gap

					if is_acceptable_deviation( x, y, nearest_x, nearest_y ): # for efficiency, first check if nearest is within acceptable bounds
						# then check against all preceding points
						new_counter = 0
						is_wonky = False
						for prev_val in line_groups[key]:
							start_x = prev_val[0]
							start_y = prev_val[1]
							if not is_acceptable_deviation( x, y, start_x, start_y ):
								is_wonky = True
								cv2.rectangle(debugimg,(start_x-15,start_y-15),(start_x+30,start_y+30),(0,250,250),cv2.FILLED)
								cv2.rectangle(debugimg,(x-15,y-15),(x+30,y+30),(250,0,250),cv2.FILLED)
								continue # the line overall is getting too wonky!
							new_counter += 1

						if not is_wonky:
							matched_key = key

						continue


				# if aligned, add to the group (note: updating the key by creating a new one and deleting the old one...)
				new_key = (x,y)	
				if matched_key:
					line_groups[new_key] = line_groups[matched_key] + [(x,y)]
					if matched_key != new_key:
						del line_groups[matched_key]
					loop_count_matched += 1
				else:
					line_groups[new_key] = [(x,y)]
					loop_count_non += 1


		# create column entities

		lines_in_groups = 0
		for key in sorted(line_groups):
			lines_in_groups += len( line_groups[ key ] )

		cols = {}
		counter = 0
		for key in sorted(line_groups): # seems to sort the tuple keys ok !!!
			if len( line_groups[key] ) == 0:
				continue
			vals = line_groups[key]
			vals = sorted( vals, key=lambda tup: tup[1] ) # sort by y1
			top_val 	= vals[0]
			last_val 	= vals[-1]
			cols[ counter ] = {}
			cols[ counter ][ "xpos" ] 	= key[0] #x1
			cols[ counter ][ "length" ] = last_val[1]-top_val[1] #y1-y1
			cols[ counter ][ "seq" ]    = []
			cols[ counter ][ "seq" ].append( ( top_val[0], 0 ) ) # first value, inferred direct line to image top
			for val in vals:
				cols[ counter ][ "seq" ].append( ( val[0], val[1] ) )
				cv2.rectangle(debugimg,(val[0]-8,val[1]-8),(val[0]+16,val[1]+16),(0,0,0),cv2.FILLED)
			cols[ counter ][ "seq" ].append( ( last_val[0], height ) ) # last value, inferred direct line to image bottom
			counter += 1

		print( "- Number of line groups: %s" % len( cols ) )


		# if not the correct number of column entities:

		if len(cols) > num_expected_lines:

			# remove the column entities with the shortest spread...
			while len(cols) > num_expected_lines:
				sorted_cols = sorted(cols.items(), key=lambda x: x[1]['length']) # sort the cols by length, ascending
				first_index = sorted_cols[0][0]
				del cols[first_index] # remove from the top, i.e. the one with smallest length value

			# re-sequence the dictionary keys
			counter = 0
			for key in sorted(cols):
				cols[counter] = cols.pop(key)
				counter += 1

			print( "- Number of line groups (corrected): %s" % len( cols ) )


		if not len( cols ) == num_expected_lines:
			print( "- *** ERROR: UNABLE TO DISTINGUISH %s DISTINCT LINE GROUPS ***" % num_expected_lines )
			continue

	 
		# find the average gap between the major vertical lines

		col_gaps = []
		prev_xpos = None
		for col in sorted(cols):
			xpos = cols[col]["xpos"]
			if not prev_xpos: 
				prev_xpos = xpos
				continue
			gap = xpos - prev_xpos
			col_gaps.append( gap )
			prev_xpos = xpos
		avg_col_gap = int( sum(col_gaps) / float(len(col_gaps)) )
		print ( "- Average column gap: %s" % avg_col_gap )


		# add an inferred final column to the column entitites

		cols[ counter ] = {}
		cols[ counter ][ "seq" ]    = []
		for prev_coord in cols[ counter-1 ][ "seq" ]:
			cols[ counter ][ "seq" ].append( ( min( width, prev_coord[0]+avg_col_gap+20 ), prev_coord[1] ) ) # inferring the position of a final column


		# add region of interest data to the column entities

		for key, details in cols.items():
			details[ "roi_corners" ] = []
			for coord in details[ "seq" ]: # going down the right...
				details[ "roi_corners" ].append( ( coord[0]-linewidth, coord[1] ) ) # nudge to the left to avoid showing the detected line
				cv2.rectangle(debugimg,(coord[0]-8,coord[1]-8),(coord[0]+16,coord[1]+16),(255,255,0),cv2.FILLED)

			if key>0:
				for prev_coord in reversed( cols[ key-1 ][ "seq" ] ): # going up the left
					details[ "roi_corners" ].append( ( prev_coord[0]+linewidth, prev_coord[1] ) ) # nudge to the right to avoid showing the detected line
			else:
				for new_coord in reversed( cols[ key ][ "seq" ] ): # go up the "left", using inferred positions...
					details[ "roi_corners" ].append( ( max( 0, new_coord[0]-(avg_col_gap+20) ), new_coord[1] ) )

		if is_debug:
			cv2.imwrite(debugpath.replace(".jpg",".debug-vertical.jpg"),debugimg)


		# STEP 3. crop for each column
		for col, details in cols.items():
			# perform the crop...
			roi = details["roi_corners"]
			pts = np.array(roi,dtype=np.dtype('int'))

			## (1) Crop the bounding rect
			rect = cv2.boundingRect(pts)
			x,y,w,h = rect
			cropped_img = img[y:y+h, x:x+w].copy()
			## (2) make mask
			pts = pts - pts.min(axis=0)
			mask = np.zeros(cropped_img.shape[:2], np.uint8)
			cv2.drawContours(mask, [pts], -1, (255, 255, 255), -1, cv2.LINE_AA)
			## (3) do bit-op
			dst = cv2.bitwise_and(cropped_img, cropped_img, mask=mask)
			## (4) add the white background
			bg = np.ones_like(cropped_img, np.uint8)*255
			cv2.bitwise_not(bg,bg, mask=mask)
			cropped_img = bg + dst
			## (5) Crop the mod image in the same way
			cropped_mod = mod[y:y+h, x:x+w].copy()
			cropped_mod = cv2.bitwise_and(cropped_mod, cropped_mod, mask=mask)
			## (6) Rotate/skew the columns (no rotation)
			cropped_height, cropped_width, cropped_channels = cropped_img.shape
			mod_height, mod_width = cropped_mod.shape

			if is_debug:
				writepath = debugpath.replace(".jpg",".pdf.%s-noskew.jpg" % (col_trans(col)))
				cv2.imwrite(writepath,cropped_img)

			top_xs = []
			btm_xs = []
			for pt in roi:
				if pt[1] == 0: # in ROI data there is a straight line up to the top of image, so this value is still correct, despite the crop
					top_xs.append( pt[0] )
				if pt[1] == ( cropped_height + major_horizontal_y ):
					btm_xs.append( pt[0] )

			max_l 	= min( [ min( top_xs ), min( btm_xs ) ] )
			max_r 	= max( [ max( top_xs ), max( btm_xs ) ] )

			tl = ( min( top_xs )-x, 0 )
			tr = ( max( top_xs )-x, 0 )
			bl = ( min( btm_xs )-x, cropped_height )
			br = ( max( btm_xs )-x, cropped_height )

			gap_top = max( tl[0], cropped_width-tr[0] )
			gap_btm = max( bl[0], cropped_width-br[0] )

			o1 = min( top_xs ) -  min( btm_xs )
			o2 = max( top_xs ) -  max( btm_xs )
			a = cropped_height
			rot_angle1 = math.degrees(math.atan(o1/a))
			rot_angle2 = math.degrees(math.atan(o2/a))
			rot_angle = ( rot_angle1 + rot_angle2 ) / 2
			print( "- Col %s: Rotational adjustment: %s (%s/%s)" % ( col_trans(col), round(rot_angle,2), round(rot_angle1,2), round(rot_angle2,2) ) )

			if ( rot_angle1 <= 0 and rot_angle2 <= 0 ) or ( rot_angle1 >= 0 and rot_angle2 >= 0 ):
				M = cv2.getRotationMatrix2D((cropped_width/2,cropped_height/2),rot_angle,1)
				cropped_img = cv2.warpAffine(cropped_img,M,(cropped_width,cropped_height),borderValue=(255,255,255))
				cropped_mod = cv2.warpAffine(cropped_mod,M,(cropped_width,cropped_height),borderValue=(0,0,0))
			else:
				print( "- ***ROTATION ABORTED*** : CONTRARY ANGLES" )

			'''
			gap_pct = ( max( gap_btm, gap_top ) / cropped_width )
			new_height = int(cropped_height)#*(1+gap_pct))
			new_width = int(cropped_width)#*(1+gap_pct))	
			ost = 40 #offset - needed to avoid cutting off areas in concave/convex image
			pts1 = np.float32([[tl[0],tl[1]],	[tr[0],tr[1]],			[bl[0],bl[1]],			[br[0],br[1]]])
			pts2 = np.float32([[ost,ost],		[new_width-ost,ost],	[ost,new_height-ost],	[new_width-ost,new_height-ost]])

			M = cv2.getPerspectiveTransform(pts1,pts2)
			cropped_img = cv2.warpPerspective(cropped_img,M,(new_width+0,new_height+0),borderValue=(255,255,255))
			cropped_mod = cv2.warpPerspective(cropped_mod,M,(new_width+0,new_height+0),borderValue=(0,0,0))
			
			cropped_height, cropped_width, cropped_channels = cropped_img.shape	
			'''


			# some contours pre-processing
			cropped_mod = cv2.erode(cropped_mod, kernel5, iterations=1)


			# STEP 4. use contours, rather than houghlines, to find the horizontal separators

			debugimg = copy.deepcopy(cropped_img)
			wide_lines = []
			contours, hierarchy = cv2.findContours(cropped_mod,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
			for contour in contours:
				[x,y,w,h] = cv2.boundingRect(contour)
				#if cv2.contourArea(contour) < 40: # cleaning up the image by removing small specs
				#	cv2.rectangle(debugimg,(x,y),(x+w,y+h),(255,0,255),cv2.FILLED)
				#	cv2.rectangle(cropped_img,(x,y),(x+w,y+h),(255,255,255),cv2.FILLED)
				#	cv2.rectangle(cropped_mod,(x,y),(x+w,y+h),(0,0,0),cv2.FILLED)
				#elif is_light_area(cropped_img, contour): # cleaning up the image
				#	cv2.rectangle(debugimg,(x,y),(x+w,y+h),(255,0,255),cv2.FILLED)
				#	cv2.rectangle(cropped_img,(x,y),(x+w,y+h),(255,255,255),cv2.FILLED)
				#	cv2.rectangle(cropped_mod,(x,y),(x+w,y+h),(0,0,0),cv2.FILLED)
				#else:
				cv2.rectangle(debugimg,(x,y),(x+w,y+h),(255,100,100),1)

				if ( w>(cropped_width*.33) and h<75 ) or ( w>(cropped_width*.25) and h<25 ):
					if is_centred(x,w,cropped_width):
						wide_lines.append( (x,y,w,h) )
						cv2.rectangle(debugimg,(x,y),(x+w,y+h),(0,0,255),5)

			if is_debug:
				writepath = debugpath.replace(".jpg",".pdf.%s-edges.jpg" % (col_trans(col)))
				cv2.imwrite(writepath,cropped_mod)
				writepath = debugpath.replace(".jpg",".pdf.%s.jpg" % (col_trans(col)))
				cv2.imwrite(writepath,cropped_img)
				writepath = debugpath.replace(".jpg",".pdf.%s-debug.jpg" % (col_trans(col)))
				cv2.imwrite(writepath,debugimg)

			
			wide_lines = sorted( wide_lines, key=lambda tup: ( tup[1], tup[0] ) )

			if not wide_lines:
				wide_lines.append( (0,0,cropped_width,1) )
				wide_lines.append( (0,cropped_height,cropped_width,1) ) # infer a wide line at the very bottom

			if wide_lines[0][1] > 250: # if there isn't a line at the top, add one
				wide_lines.append( (0,0,cropped_width,1) )
				wide_lines = sorted( wide_lines, key=lambda tup: ( tup[1], tup[0] ) ) # sort immediately
			if wide_lines[-1][1] < cropped_height-200: # if there isn't a line at the bottom, add one
				wide_lines.append( (0,cropped_height-1,cropped_width,1) )
				wide_lines = sorted( wide_lines, key=lambda tup: ( tup[1], tup[0] ) )

			wide_lines = sorted( wide_lines, key=lambda tup: ( tup[1], tup[0] ) )
			#print( "- Wide lines: %s" % wide_lines )

			first_line	= True
			el_loop		= 1

			for x,y,w,h in wide_lines:
				if first_line:
					prev_x, prev_y, prev_w, prev_h = x,y,w,h
					first_line = False
					continue

				if y - prev_y < 200: # if hit another line less than 200 after the previous...
					#prev_x, prev_y, prev_w, prev_h = x,y,w,h # there might be some heading text that's useful, so don't cut it off...
					continue

				el_img = cropped_img[ prev_y:y+h, 0:cropped_width ] # y2:y1, x2:x1
				el_height, el_width, el_channels = el_img.shape

				el_img = pre_ocr_enhancements( el_img, el_loop )

				writepath = fname.replace( "/01_IMG", "/01_IMG/@ocr" ).replace( ".jpg",".pdf.%s.%s.mod.jpg" % ( col_trans(col), str(el_loop) ) )
				cv2.imwrite( writepath, el_img )

				prev_x, prev_y, prev_w, prev_h = x,y,w,h
				el_loop += 1

		t1 = time.time()
		print( "- Time: %s" % ( t1-t0 ) )
		log_records = [ fname, str(major_horizontal_y), str(len( cols )), str(t1-t0), str(datetime.datetime.now().time()) ]
		with open( log_path, "a" ) as w:
			w.write( "\t".join( log_records ) + "\n" )


def fetch_split_images( path, expected_columns ):
	conv_files = sorted( glob.glob("%s/*.jpg" % ( path ) ) )
	perform_split_articles( conv_files, path, expected_columns )

	if not conv_files:
		for root, dirs, files in os.walk( path ):
			for dirname in dirs:
				#del_files = glob.glob("%s/%s/*.pdf.*.jpg" % ( root, dirname ) )
				#for fname in del_files:
				#	os.system("rm '%s'" % fname)
			
				conv_files = sorted( glob.glob("%s/%s/*.jpg" % ( root, dirname ) ) )
				perform_split_articles( conv_files, path, expected_columns )


for root, dirnames, filenames in os.walk( run_path ):
	for fname in filenames:
		expected_columns = {}
		if fname == "num_cols.txt":
			seed_path = "%s/%s" % ( root, fname )
			with open( seed_path, "r" ) as r:
				for line in r.readlines():
					if "\t" in line:
						end_date = line.split("\t")[0]
						num_cols = line.split("\t")[1]
						expected_columns[ end_date ] = num_cols
			print( "- Performing split..." )
			fetch_split_images( root+"/01_IMG", expected_columns )
