#!/bin/bash

# dont let root run this script on pi
if [ $UID == 0 ]; then
	su -c $0 - pi
	exit 0
fi

# find if python2 is on path
which python2 > /dev/null
if [ $? == 0 ]; then
	python_exec=python2
else 
	python_exec=python
fi

cd `dirname $0`

# loop until pilink is done
rc=100
while [ $rc == 100 ]; do
	echo "[[[ pilink ]]]"
	$python_exec pilink.py
	rc=$?
done
