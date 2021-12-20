#!/bin/bash

yum install python34-setuptools git -y
pip3 install flask #flask-sqlalchemy

cd /home/ec2-user

mkdir repo.git && cd repo.git
git init
git config core.sshCommand "ssh -o StrictHostKeyChecking=no"
git remote add origin https://github.com/Warggr/default-tirith-app.git
git pull origin master
git remote remove origin
git config receive.denyCurrentBranch ignore

cat > .git/hooks/post-receive <<EOF
#!/bin/bash
git reset --hard

sudo lsof -i :80 | tail -1 | tr -s ' ' |  cut -d ' ' -f 2 | xargs sudo kill
sudo nohup /usr/local/bin/flask run -p 80 -h 0.0.0.0 > /home/ec2-user/log.txt 2>&1 &
EOF
chmod +x .git/hooks/post-receive

chown ec2-user . -R

export FLASK_APP=/home/ec2-user/repo.git/app.py
export FLASK_ENVIRONMENT=development

touch log.txt
chown ec2-user log.txt

nohup /usr/local/bin/flask run -p 80 -h 0.0.0.0 > /home/ec2-user/log.txt 2>&1 &
