#!/bin/bash

python3 $HOME/.tirith/aws/main.py delete .instances.json

git remote remove tirith
rm .git/hooks/post-commit
