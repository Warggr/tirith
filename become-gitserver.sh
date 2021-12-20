#!/bin/bash

sudo ln -sf /usr/bin/python3 /usr/bin/python #use python3

yum install pip git -y
pip install flask #flask-sqlalchemy

cd /home/ec2-user

mkdir repo.git && cd repo.git
git init
git config core.sshCommand "ssh -o StrictHostKeyChecking=no"
git remote add origin git@github.com:Warggr/default-tirith-app.git
git pull origin main
git remote remove origin
git config receive.denyCurrentBranch ignore

cat > .git/hooks/post-receive <<EOF
#!/bin/bash
git reset --hard
EOF
chmod +x .git/hooks/post-receive

chown ec2-user . -R

export FLASK_APP=/home/ec2-user/repo.git/app.py
export FLASK_ENVIRONMENT=development

nohup flask run -p 5000 -h 0.0.0.0 > /home/ec2-user/log.txt 2>&1 &
