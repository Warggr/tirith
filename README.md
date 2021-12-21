# Automatic deployment of Flask apps on Amazon EC2

## Install

To install Tirith, follow these steps. This needs to be done only once, even if you want to launch multiple projects.

1. Download the Git repository and navigate into it: \\
	```bash git clone git@github.com:warggr/tirith.git && cd tirith```
2. Configure your credentials: get your credentials by logging in to Vocareum, then paste them into `~/.aws/credentials|`
3. Install the program on your system by running `./install.sh`. You can directly specify the location of your AWS key: `./install.sh path/mykey.pem|`.

## Run

For each project, do the following:

1. Create a new folder anywhere in your filesystem: `mkdir <PATH> && cd <PATH>`.
2. Run the creation script: `$HOME/.tirith/create.sh`
3. The necessary instances have been created, and a mock app has been deployed on these instances. A Git repository has been created in your current path.
4. To create and deploy a new version, add some files and commit.
5. You can manage the instances with: `verb|python3 ~/.tirith/aws/main.py <COMMAND> .instances.json`, where `<COMMAND>` can be:
	- \verb|stop| to stop the instances temporarily
	- \verb|start| to restart them afterwards
	- \verb|more| or \verb|less| to have the newer version be deployed 10\% more or 10\% less
6. To terminate the instances, run `$HOME/.tirith/terminate.sh`

## Uninstall

To uninstall the configuration, run

`~/.tirith/uninstall.sh`
