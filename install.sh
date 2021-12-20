#!/bin/bash

if ! [ -d $HOME/.tirith ] ; then
	echo "Creating folder $HOME/.tirith";
	mkdir $HOME/.tirith
fi

if [ $# -eq 0 ]; then 
	echo "Where is your AWS key situated? (Please enter the full path - the ~ character is not allowed)";
	read key_filename;
else
	key_filename=$1;
fi

ln -s $key_filename $HOME/.tirith/key.pem

SECURITY_GROUP=$(python3 ./aws/security_group.py create)

echo $SECURITY_GROUP > $HOME/.tirith/security_group.json

cat > aws/config.py <<EOF
#!/bin/python3
KEYPAIR_NAME = "$(basename $key_filename .pem)"
SECURITY_GROUP = "$SECURITY_GROUP"
EOF

cp ./aws $HOME/.tirith -r
cp ./become-gitserver.sh $HOME/.tirith
cp ./create.sh $HOME/.tirith
