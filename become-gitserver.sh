#!/bin/bash

apt update
apt install -y python3-flask

export TIRITH_HOME=/home/ubuntu/repo.git

mkdir $TIRITH_HOME
cd $TIRITH_HOME
git init
git config user.name "Tirith Initialization"
git config user.email "init@tiri.th"

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

git add app.py README.md && git commit -m "Initializing repository"

chown ubuntu $TIRITH_HOME -R

export FLASK_APP=$TIRITH_HOME

flask run
