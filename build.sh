#!/bin/bash

. config

OUT_BUILD_DIR="$OUT_DIR/build"
OUT_RELEASE_DIR="$OUT_DIR/release"

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
check_dependency "node" "Please install node from https://nodejs.org/"
check_dependency "npm" "Please follow the npm installation instructions at https://docs.npmjs.com/downloading-and-installing-node-js-and-npm"

echo "Checking docker service status..."
systemctl is-active --quiet docker
status=$?
if [ $status -ne 0 ]; then
    echo "Starting docker service..."
    sudo service docker start
fi

username=$(whoami)
if ! groups $username | grep -q '\bdocker\b'; then
    echo "Adding user to docker group..."
    sudo usermod -a -G docker $username
    echo "User " $username " added to group docker"
    echo "Please logout and login"
    exit 13
fi

echo "Packing $TOOL_NAME... Please wait..."

echo "Building $TOOL_NAME"
docker build --pull --rm -f "Dockerfile" -t $DOCKER_IMAGE_NAME --build-arg shared_volume=$SHARED_VOLUME "."
if [ $? -ne 0 ]; then
    echo -e "\n\nError: cannot build $TOOL_NAME\nExit\n\n"
    exit 13
fi

echo "Exporting $TOOL_NAME image to '$OUT_BUILD_DIR' directory. This may take several minutes.. "
mkdir -p $OUT_DIR/
rm -rf $OUT_DIR/*
mkdir -p $OUT_BUILD_DIR/
docker save -o $OUT_BUILD_DIR/$TOOL_NAME.img $DOCKER_IMAGE_NAME

echo "Generating README.pdf from README.md"
FILE=/etc/resolv.conf
if [ ! -f "artifact/README.md" ]; then
  echo -e "Cannot find file artifact/README.md"
  echo -e "Please create file artifact/README.md to build the artifact"
  exit 1
fi
cd md2pdf
npm install
node md2pdfREADME.js
cd ..
mv README.pdf $OUT_BUILD_DIR/
cp artifact/README.md run.sh config utils $OUT_BUILD_DIR/

echo "Exporting archive to to '$OUT_RELEASE_DIR' directory."
mkdir -p $OUT_RELEASE_DIR/
pigzbin=`command -v pigz`
prev_pwd=$PWD
cd $OUT_BUILD_DIR
if [ -z ${pigzbin} ]; then
  tar cvfz $prev_pwd/${OUT_FILENAME}.tar.gz *
else
  tar cvf $prev_pwd/${OUT_FILENAME}.tar *
  pigz $prev_pwd/${OUT_FILENAME}.tar
fi
cd $prev_pwd
mv ${OUT_FILENAME}.tar.gz $OUT_RELEASE_DIR/${OUT_FILENAME}.tgz
cd $OUT_RELEASE_DIR
md5sum ${OUT_FILENAME}.tgz > ${OUT_FILENAME}.tgz.md5

echo "Done!"
