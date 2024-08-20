#!/bin/bash

mkdir 01_JPG
mogrify -format jpg -quality 95 00_TIF/*.tif
mv 00_TIF/*.jpg 01_JPG
