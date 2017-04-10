#!/usr/bin/bash

DOCKER_IMAGE = "blogbuild"
REPO_NAME = "mezzaine-blog"


if [ !$(docker image | cut -d' ' -f1 | grep $DOCKER_IMAGE) ]; then
    echo " creating docker build image from docker file"
    docker build -t $DOCKER_IMAGE .
    if [ $? -ne 0 ]
    then 
    	echo "Building image unsuccessful.... Please try again"
    	exit
echo "Building the package"
docker run -i -v ${PWD}/$REPO_NAME:/$REPO_NAME -u $(id -u) $DOCKER_IMAGE:latest sh << COMMANDS
cd /$REPO_NAME
sudo /usr/bin/expect debpackage.sh
dpkg-buildpackage -us -uc
cp ../mezzaine*.deb .
COMMANDS