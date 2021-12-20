#!/usr/bin/bash
if [ -d .git ]; then
	echo "Error: Git repo already exists"; 
	exit 1;
fi

python3 $HOME/.tirith/aws/main.py create .instances.json | tee output

INSTANCE_DNS=$(cat output | grep "DNS_NAME" | cut -d ' ' -f 2)

echo "Done! Your Flask app is deployed at http://$INSTANCE_DNS/"

# Almost-equivalent to git clone. Adapted from https://stackoverflow.com/a/18999726

git init
git config core.sshCommand "ssh -i $HOME/.tirith/key.pem -o StrictHostKeyChecking=no"

git remote add blue http://dummy_url
git remote add green http://dummy_url
cat output | grep "INSTANCE_DNS 1" | cut -d ' ' -f 3 | while read line; do git remote set-url --add blue $line
cat output | grep "INSTANCE_DNS 2" | cut -d ' ' -f 3 | while read line; do git remote set-url --add green $line
git remote set-url --delete green http://dummy_url
git remote set-url --delete blue http://dummy_url

rm output

git pull green master
git fetch blue
git branch --set-upstream-to=blue/master master
git branch --set-upstream-to=green/master master

echo > .git/hooks/post-commit <<EOF
#!/bin/bash
python3 \$HOME/.tirith/aws/main.py fill .instances.json
python3 \$HOME/.tirith/aws/main.py switch .instances.json

git push blue master

cat .git/hooks/post-commit | sed -e 's/blue/tmp/g' -e 's/green/blue/g' -e 's/tmp/green/g' > .git/hooks/post-commit 
EOF
chmod +x .git/hooks/post-commit
