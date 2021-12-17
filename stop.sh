#!/bin/bash

cat instances.txt | while read line; do aws ec2 stop-instances --instance-ids $line; done
