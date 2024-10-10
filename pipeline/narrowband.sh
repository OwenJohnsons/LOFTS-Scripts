#!/bin/bash

# Arguments 
# $1 : Telescope 
# $2 : Directory path

station=$1
path=$2

project_path="/datax2/projects/LOFTS"

# Check the station and set appropriate values
if [ "$station" = "IE613" ]; then 
    station_argument='p'
    barycenter_path='/home/obs/linux_64/BaryCentricCorrection/barycentre_seti'
elif [ "$station" = "SE607" ]; then
    station_argument='p'
    barycenter_path='/home/obs/linux_64/BaryCentricCorrection/barycentre_seti'
else 
    echo "Invalid station name. Please specify IE613 or SE607."
    exit 1
fi

# Find filterbank files
filterbank_paths=$(find "$path" -name "*0000.fil")
echo "Number of filterbanks found: $(echo "$filterbank_paths" | wc -w)"

# Loop through filterbank files and display their header
for filterbank in $filterbank_paths; do 
    echo "Header of $filterbank"
    header $filterbank  # Replace this with the correct command
done 
