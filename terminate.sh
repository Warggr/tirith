#!/bin/bash

cat instances.txt | grep "instance" | cut -f 2 -d ' ' | while read line; do aws ec2 terminate-instances --instance-ids $line; done
rm instances.txt

git remote remove tirith
