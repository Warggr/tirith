#!/bin/bash

python3 $HOME/.tirith/aws/main.py delete .instances.json

git remote remove blue
git remote remove green
rm .git/hooks/post-commit
