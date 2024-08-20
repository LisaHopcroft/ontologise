#!/bin/sh

imageDir=$1
textDir=$2

# create transcript text files directly from photos

find "$imageDir" -print0 | 
    while IFS= read -r -d $'\0' imageFileLong; do 
	imageFile=`basename "$imageFileLong"`
	echo $imageFile
	imageBase=`echo "$imageFile" | sed s/_.*$//`
	if [ $imageBase -ne $imageFile ];
	then
		textFile="$imageBase.txt"
		echo $textFile
	fi
    done
