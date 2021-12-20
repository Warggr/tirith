#!/bin/bash

if ! [ $HOME/.tirith ] ; then
	echo "Was not installed";
	exit 1;
fi

python3 ./aws/security_group.py delete < $HOME/.tirith/security_group.json

rm $HOME/.tirith -r
