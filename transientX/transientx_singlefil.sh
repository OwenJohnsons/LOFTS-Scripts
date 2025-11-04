#!/bin/bash

file_path=$1

# Time script 
time=$(date +"%H:%M")

# Check if the file exists
if [ ! -f "$file_path" ]; then 
    echo "File does not exist. Exiting..."
    exit 1
fi

# Define target and output directory
target=$(basename "$file_path" | cut -d'.' -f1)
path=$(dirname "$file_path")
output_dir="$path/${target}_singlepulse"

# Check if the output directory exists
if [ ! -d "$output_dir" ]; then 
    mkdir -p "$output_dir"
fi

echo " ======================== "
echo " Target: $target"
echo " Output directory: $output_dir"
echo " ======================== "

cd $path

transientx_fil -v -f "${file_path}" -o "${target}_singlepulse/${target}" --dms 0 --ddm 0.5 --ndm 2000 --maxw 0.2 --thre 5 -z [KadaneF fdRFI KadaneT tdRFI] --threKadaneF 2 --threKadaneT 2 --zapthre 2 --fill rand