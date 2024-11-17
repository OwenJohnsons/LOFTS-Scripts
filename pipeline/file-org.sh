#!/bin/bash

# Arguments
# $1 : Directory path
path=$1

# Define the project path
project_path="/datax2/projects/LOFTS"

# Find all filterbanks in sub-directories of the given path
filterbank_paths=$(find "$path" -name "*.fil")
echo "Number of filterbanks found: $(echo "$filterbank_paths" | wc -w)"

# Loop through each filterbank path
for filterbank_path in $filterbank_paths; do 
    # Extract date from the header (assuming date is on line 16)
    date=$(header "$filterbank_path" | awk -F': ' 'NR==16 {print $2}')
    date=$(echo "$date" | sed 's/\//-/g')

    # Extract source name from the filename
    src_name=$(basename "$filterbank_path")
    src_name=$(echo "$src_name" | awk -F'.' '{print $1}')

    # Create the target directory if it doesn't exist
    target_dir="$project_path/$date/$src_name"
    mkdir -p "$target_dir"

    # Move the file only if it doesn't already exist
    if [ -e "$target_dir/$(basename "$filterbank_path")" ]; then
        echo "File already exists: $target_dir/$(basename "$filterbank_path"). Skipping."
    else
        mv "$filterbank_path" "$target_dir"
        echo "Moved: $filterbank_path -> $target_dir"
    fi
done

echo "$(echo "$filterbank_paths" | wc -w) files organized successfully!"