#!/bin/bash

# Arguments 
# $1 : Telescope 
# $2 : Directory path

station=$1
path=$2


# Check the station and set appropriate values
if [ "$station" = "IE613" ]; then 
    station_argument='n'
    barycenter_path='/home/obs/linux_64/BaryCentricCorrection/barycentre_seti'
elif [ "$station" = "SE607" ]; then
    station_argument='p'
    barycenter_path='/home/owen/BaryCentricCorrection/barycentre_seti'
else 
    echo "Invalid station name. Please specify IE613 or SE607."
    exit 1
fi

# Find filterbank files
filterbank_paths=$(find "$path" -name "*0000.fil")
echo "Number of filterbanks found: $(echo "$filterbank_paths" | wc -w)"

# Loop through filterbank files and display their header
for filterbank in $filterbank_paths; do 
    target=$(basename $filterbank | awk -F'.' '{print $1}')
    echo "Target : $target"
    $barycenter_path $filterbank -site $station_argument -verbose >  $path/$target.bary.0000.fil

    # remove .bar file after barycentering
    rm polyco.bar 

    # Run turboSETI 
    turboSETI -g -n 412 -s 10 -M 4 $path/$target.bary.0000.fil
done 