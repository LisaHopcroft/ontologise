#!/bin/bash

# 12044 - 1780, Jan 1
# 18762 - 1830, Dec 28 

for i in `seq 7564 10000`; do
	foo="wget https://www.thegazette.co.uk/Edinburgh/issue/$i"
	echo $foo
	eval $foo
done
