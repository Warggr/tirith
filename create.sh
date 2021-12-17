#!/usr/bin/bash
if [ -d .git ]; then
	echo "Error: Git repo already exists"; 
	exit 1;
else
	git init;
fi

git config core.sshCommand "ssh -i ~/Poly/Cloud_8415/lightningbolt.pem"

cat > .git/hooks/post-commit << EOF
#!/bin/bash

git push
EOF

chmod +x .git/hooks/post-commit

echo "Creating instance..."

INSTANCE_ID=$(
	aws ec2 run-instances \
--image-id ami-09e67e426f25ce0d7 \
--instance-type t2.micro \
--key-name lightningbolt \
--security-groups "white-guard" \
--user-data file:///home/pierre/.tirith/become-gitserver.sh \
--tag-specifications 'ResourceType=instance,Tags=[{Key=name, Value=minas}]' \
--query Instances[0].InstanceId | tr -d '"'
)

echo $INSTANCE_ID >> instances.txt

INSTANCE_DNS=$(
	aws ec2 describe-instances \
--instance-ids "$INSTANCE_ID" \
--query Reservations[0].Instances[0].PublicDnsName | tr -d '"'
)

git remote add tirith ubuntu@$INSTANCE_DNS:/home/ubuntu/repo.git

echo "Waiting for instance to come online..."

aws ec2 wait instance-status-ok --instance-ids "$INSTANCE_ID"

git pull tirith master < 'y'

echo "Done! Your Flask app is deployed at https://$INSTANCE_DNS/"
