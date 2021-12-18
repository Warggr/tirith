#!/bin/bash

if ! [ $HOME/.tirith ] ; then
	echo "Was not installed";
	exit 1;
fi

rm $HOME/.tirith -r

aws ec2 delete-security-group --group-name "white-guard-v1"
