#!/usr/bin/env python
import time

start 	= None
logtxt 	= ""

def timer( txt ):
	global start
	global logtxt

	if start: # default usage: one timer starting ends another...
		print( "~~~ %s: %s" % (logtxt, round( time.time() - start, 2 ) ) )

	logtxt 	= txt
	start 	= time.time()

def ender():
	global start
	global logtxt

	print( "~~~ %s: %s" % (logtxt, round( time.time() - start, 2 ) ) )
