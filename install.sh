#!/bin/bash

if ! [ -d $HOME/.tirith ] ; then
	echo "Creating folder $HOME/.tirith";
	mkdir $HOME/.tirith
fi

cp ./become-gitserver.sh $HOME/.tirith/become-gitserver.sh
if [ $# -eq 0 ]; then 
	echo "Where is your AWS key situated? (Please enter the full path - the ~ character is not allowed)";
	read key_filename;
else
	key_filename=$1;
fi

ln -s $key_filename $HOME/.tirith/key.pem

if aws ec2 describe-security-groups --group-names "white-guard-v1" --query SecurityGroups[0] > /dev/null ; then
	echo "Security group already exists"
	GROUP_ID=$(aws ec2 describe-security-groups --group-names "white-guard-v1" --query SecurityGroups[0].GroupId | tr -d '"');
else
	echo "Creating security group"
		GROUP_ID=$(
		aws ec2 create-security-group \
		--description "Allow SSH, HTTP and HTTPS" \
		--group-name "white-guard-v1" \
		--tag-specifications "ResourceType=security-group,Tags=[{Key=codeline,Value=white-guard},{Key=version,Value=1}]"\
		--query GroupId | tr -d '"'
	)
	echo "sec-group" $GROUP_ID >> $HOME/.tirith/instances.txt
fi

aws ec2 authorize-security-group-ingress --group-id $GROUP_ID --ip-permissions '[
{"IpProtocol": "tcp","FromPort": 22,"ToPort": 22, "IpRanges": [{"CidrIp": "0.0.0.0/0"}]},
{"IpProtocol": "tcp","FromPort": 80,"ToPort": 80,"IpRanges": [{"CidrIp": "0.0.0.0/0"}]},
{"IpProtocol": "tcp","FromPort": 443,"ToPort": 443,"IpRanges": [{"CidrIp": "0.0.0.0/0"}]}
]' > /dev/null
