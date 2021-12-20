#!/bin/bash

if ! [ $HOME/.tirith ] ; then
	echo "Was not installed";
	exit 1;
fi

if python3 $HOME/.tirith/aws/security_group.py delete < $HOME/.tirith/security_group.json; then
	rm $HOME/.tirith -r
fi
