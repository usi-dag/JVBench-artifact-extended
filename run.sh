#!/bin/bash

. config
. utils

if [ $# -lt 1 ]; then
    echo -e "\nNo command provided.\nPlease chose one of [verify, precollected, evaluation, clean]\n\n"
    echo -e "Example: ./run.sh verify\n\n"
    exit 2
fi

cmd=$1
shift

if [ ! $cmd == "verify" ] && [ ! $cmd == "precollected" ] && [ ! $cmd == "evaluation" ] && [ ! $cmd == "clean" ]; then
    echo -e "\n\nInvalid '$cmd' command provided.\nPlease chose one of [verify, precollected, evaluation, clean]\n\n"
    exit 3
elif [ $cmd == "clean" ]; then
    yes_or_no "This command will delate the $SHARED_VOLUME folder and all its content. Do you wish to continue?"

    if [ $? -eq 0 ]; then
        echo 
        echo "Deleting folder $SHARED_VOLUME... (requires sudo)"
        echo
        sudo rm -rf $(pwd)/$SHARED_VOLUME
        echo
        echo "The $SHARED_VOLUME folder has been deleted"
        echo
        exit 0
    fi 

    echo 
    echo "Aborted"
    echo
    exit 4
fi

function check_dependency() (
  cmd=$1
  error_message=$2

  cmd_bin=`which $1`
  if [ -z ${cmd_bin} ]; then
      echo "$TOOL_NAME requires Docker"
      echo "Please install node from https://nodejs.org/"
      exit 1
  fi
)

echo "Checking dependencies..."
check_dependency "docker" "Please install Docker from https://docs.docker.com/install/"

echo "Checking docker service status..."
systemctl is-active --quiet docker
status=$?
if [ $status -ne 0 ]; then
    echo "Starting docker service... (requires sudo)"
    sudo service docker start
fi

username=$(whoami)
if ! groups $username | grep -q '\bdocker\b'; then
    echo "Adding user $username to docker group... (requires sudo)"
    sudo usermod -a -G docker $username
    echo "User " $username " added to group docker"
    echo "Please logout and login again to re-evaluate your group membership"
    exit 13
fi

echo "Loading $TOOL_NAME docker image... (this may take several minutes)"
mkdir -p output
docker load -i $DOCKER_IMG_FILENAME

echo "Running command '$cmd $@' in a docker container..."
mkdir -p $(pwd)/$SHARED_VOLUME
docker run -v $(pwd)/$SHARED_VOLUME:/artifact/$SHARED_VOLUME -i -t $DOCKER_IMAGE_NAME ./$cmd.sh $@
