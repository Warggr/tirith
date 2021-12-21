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

if ! [ -f $key_filename ]; then
	echo "Error: file does not exist";
	exit 1;
fi

if [ -L $HOME/.tirith/key.pem ]; then rm $HOME/.tirith/key.pem; fi
ln -s $key_filename $HOME/.tirith/key.pem

SECURITY_GROUP=$(python3 ./aws/security_group.py create)

echo $SECURITY_GROUP > $HOME/.tirith/security_group.json

cp ./aws $HOME/.tirith -r
cp ./become-gitserver.sh $HOME/.tirith
cp ./create.sh $HOME/.tirith
cp ./terminate.sh $HOME/.tirith

cat > $HOME/.tirith/aws/config.py <<EOF
#!/bin/python3
KEYPAIR_NAME = "$(basename $key_filename .pem)"
SECURITY_GROUP = "$SECURITY_GROUP"
EOF
