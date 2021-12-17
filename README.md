# Automatic deployment of Flask apps on Microsoft Azure and Amazon EC2
## OVERVIEW
The goal of this project is to allow the user to deploy a Flask app and continously update it only by using Git.
Additionally, it could provide an abstraction layer over Amazon and Microsoft cloud services, allowing the user to deploy its app using one or the other interchangeably. This feature might or might not be implemented during the project, depending on how much time the first goal takes to implement. If it is not implemented, deployment will only be possible on Amazon EC2.
Another possible way to extend the project would be to set up a full CI/CD pipeline, testing for each commit whether the app/website still works, allowing users to deploy their apps to more than one instance at once, and implementing blue-green deployment.
## METHODS
Essentially, this project will take away from the user the necessity of creating his own cloud instances, so that he will only have to write and commit the code.
The process as seen from the user should be as follows:
- run the script, specifying whether they want to use Microsoft Azure, Amazon EC2 or both.
- The script will create the necessary cloud instances, and create an empty Git repository in the user’s current working directory.
- Committing to the repo will automatically update the remote servers.
- Another use case of the script would be to shut down the instances and remove the Git hook.
This behaviour will be implemented as follows:
- The newly created Git repository will have a hook which will update the files on the server every time a commit is made.
- The instance IDs and state will be saved into a text document on creation, allowing the script to shut them down or terminate them.
