#!/bin/bash

eval "$(ssh-agent -s)" &&
ssh-add -k ~/.ssh/id_rsa &&
cd /home/ubuntu/panenin-backend
sudo git pull
source ~/.profile
sudo echo "$DOCKERHUB_PASS" | docker login --username $DOCKERHUB_USER --password-stdin 
sudo docker stop test-project
sudo docker rm test-project 
sudo rmi trastanechora/project_green:production
sudo docker run -d --name test-project -p 5000:5555 trastanechora/project_green:production