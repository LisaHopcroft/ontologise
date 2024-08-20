#!/bin/sh

htmldir="../01_HTML"
textdir="../02_MKD"

for htmlfile in $htmldir/*.html
do
	textfile=`basename "$htmlfile" | sed 's/html/txt/'`
	if [ ! -f "$textdir/$textfile" ]
	then
		echo "Converting file $htmlfile to $textdir/$textfile"
		html2text "$htmlfile" > "$textdir/$textfile"
	fi
done


