#!/bin/bash

. utils

echo
echo "This command will generate the figures shown in the paper using pre-collected data."
echo "Approximate running time: 5 minutes"
# yes_or_no "Do you wish to continue?"
# if [ $? -ne 0 ]; then
#     echo 
#     echo "Aborted"
#     echo
#     exit 4
# fi
echo

. config

precollected_output_dir=$(pwd)/$SHARED_VOLUME/figures-paper

mkdir -p $precollected_output_dir
./generate-figures.sh -pprx precollected -i $(pwd)/precollected_data -o $precollected_output_dir

rm -rf $precollected_output_dir/precollected_xor_19_MAVX.pdf $precollected_output_dir/precollected_xor_19_MAVX2.pdf

echo
echo
echo "============================================="
echo "       All figures have been generated       "
echo "============================================="
echo
echo
