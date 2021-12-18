#!/bin/bash

apt update
apt install -y python3-flask

mkdir /home/ubuntu/repo.git
cd /home/ubuntu/repo.git
git init
git config user.name "Tirith Initialization"
git config user.email "init@tiri.th"
git config receive.denyCurrentBranch ignore

cat > .git/hooks/post-receive <<EOF
#!/bin/bash
git reset --hard
EOF
chmod +x .git/hooks/post-receive

cat > app.py <<EOF
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

if __name__ == "__main__":
    app.run()
EOF

cat > README.md <<EOF
Project created with Tirith (contact: pierre.ballif@polymtl.ca)
EOF

cat > .gitignore <<EOF
instances.txt
EOF

git add app.py README.md .gitignore && git commit -m "Initializing repository"

chown ubuntu . -R

export FLASK_APP=/home/ubuntu/repo.git/app.py
export FLASK_ENVIRONMENT=development

nohup flask run -p 80 -h 0.0.0.0 > /home/ubuntu/log.txt 2>&1 &
