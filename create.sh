#!/usr/bin/bash
if [ -d .git ]; then
	echo "Error: Git repo already exists"; 
	exit 1;
fi

echo "Creating instance..."

INSTANCE_ID=$(
	aws ec2 run-instances \
--image-id ami-09e67e426f25ce0d7 \
--instance-type t2.micro \
--key-name lightningbolt \
--security-groups "white-guard-v1" \
--user-data file:///$HOME/.tirith/become-gitserver.sh \
--tag-specifications 'ResourceType=instance,Tags=[{Key=name, Value=minas}]' \
--query Instances[0].InstanceId | tr -d '"'
)

echo "instance" $INSTANCE_ID >> instances.txt

INSTANCE_DNS=$(
	aws ec2 describe-instances \
--instance-ids "$INSTANCE_ID" \
--query Reservations[0].Instances[0].PublicDnsName | tr -d '"'
)

echo "Waiting for instance to come online..."
aws ec2 wait instance-status-ok --instance-ids "$INSTANCE_ID"
echo "Done! Your Flask app is deployed at http://$INSTANCE_DNS/"

# Almost-equivalent to git clone. Adapted from https://stackoverflow.com/a/18999726

git init
git config core.sshCommand "ssh -i $HOME/.tirith/key.pem -o StrictHostKeyChecking=no"
git remote add tirith ubuntu@$INSTANCE_DNS:/home/ubuntu/repo.git
git pull tirith master
git branch --set-upstream-to=tirith/master master

echo -e '#!/bin/bash\ngit push' > .git/hooks/post-commit

chmod +x .git/hooks/post-commit
