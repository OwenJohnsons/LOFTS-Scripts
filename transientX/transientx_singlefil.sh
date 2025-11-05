#!/bin/bash

file_path=$1

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

cd "$output_dir"
command="transientx_fil -v -o \"${target}\" -t 4 --zapthre 3.0 --fd 1 --overlap 0.1 --ddplan /datax2/projects/LOFTS/LOFTS-Scripts/transientX/ddplan.txt --thre 7 --drop -z kadaneF 8 4 zdot -f \"${file_path}\""

# start time measurement
start_time=$(date +%s)
singularity exec --bind /datax,/datax2 /datax2/projects/LOFTS/software/dockers/transientx_lofar_v1.sif bash -c "$command"

end_time=$(date +%s)
elapsed_time=$((end_time - start_time))
echo " TransientX single pulse search completed in $elapsed_time seconds. "