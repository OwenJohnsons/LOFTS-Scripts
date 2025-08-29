#!/bin/bash

# Arguments
# $1 : Directory path
# $2 : Station prefix: IE or SE

path=$1
station=$2

# check station prefix
if [ "$station" != "IE" ] && [ "$station" != "SE" ]; then
    echo "Invalid station prefix. Use IE or SE. Exiting..."
    exit 1
fi

if [ "$station" == "IE" ]; then
    port_prefix=1613
    station_prefix="IE613_16130"
else
    port_prefix=1607
    station_prefix="SE607_16070"
fi

# LOGGING
time=$(date +"%H:%M")
log_name=$(echo $path | awk -F'/' '{print $NF}')
log_dir="/datax2/projects/LOFTS/logs/filgen"
mkdir -p "$log_dir"
log_file="${log_dir}/${log_name}_${time}.out"
error_file="${log_dir}/${log_name}_${time}.err"

{
echo "===== Script started at $(date) ====="
echo "Directory: $path"
echo "Station: $station"

folders=$(find $path -type d \( -name "*scan_*" -o -name "*scan_B*" \))
date=$(echo $path | awk -F'/' '{print $(NF)}' | sed 's/^.*sid\([0-9]\{8\}\)T.*/\1/' | sed 's/\([0-9]\{4\}\)\([0-9]\{2\}\)\([0-9]\{2\}\)/\1-\2-\3/')

echo "Number of folders found : $(echo $folders | wc -w)"
echo "Date of observations: $date"

for folder in $folders; do
    echo "-------------------------------"
    echo "Processing folder: $folder"
    target=$(echo $folder | awk -F'/' '{print $NF}' | sed 's/^.\{5\}//')
    echo "Processing Target : $target"

    output_dir="/datax2/projects/LOFTS/$date/$target"
    if [ ! -d "$output_dir" ]; then
        mkdir -p "$output_dir"
    fi

    echo "Output directory: $output_dir"

    # check if there are any .fil files in the output directory
    fil_files=$(find "$output_dir" -name "*.fil")
    if [ ! -z "$fil_files" ]; then
        echo "Filterbank files already exist in $output_dir. Skipping lofar_udp_extractor..."
        fil_exist=true
    else
        fil_exist=false
        h_file=$(find "$folder" -name "*.h")
        log_file_scan=$(find "$folder" -name "*.log" | head -n 1)
        zst_scan_path=$(awk 'NR==4 {print $2}' "$log_file_scan")
        zst_scan_path=$(echo "$zst_scan_path" | sed "s/lane0/lane[[port]]/g" | sed "s/$station_prefix/${station_prefix:0:-1}[[port]]/g")
        echo "Scan path: $zst_scan_path"

        metadata=$h_file

        raw_files=$(find "$output_dir" -name "*.raw")
        if [ ! -z "$raw_files" ]; then
            echo "Raw files already exist in $output_dir. Skipping lofar_udp_extractor..."
        else
            echo "Running lofar_udp_extractor..."
            singularity exec --bind /datax,/datax2 /datax2/obs/singularity/lofar-upm_latest.simg \
                lofar_udp_extractor -p 30 -M GUPPI \
                -S 1 -b 0,412 \
                -i "${zst_scan_path}" \
                -o "${output_dir}/${target}.[[iter]].raw" \
                -m 4096 -I "${metadata}"
        fi
    fi

    # Check if 0000.fil, 0001.fil, and 0002.fil files exist in the output directory
    if [ -f "$output_dir/${target}.rawspec.0000.fil" ] && [ -f "$output_dir/${target}.rawspec.0001.fil" ] && [ -f "$output_dir/${target}.rawspec.0002.fil" ]; then
        echo "Filterbank files 0000.fil, 0001.fil, and 0002.fil exist in $output_dir. Skipping rawspec..."
    else
        echo "Running rawspec..."
        rawspec -f 65536,8,64 -t 54,16,3072 -p 1,1,4 "$output_dir/${target}"
    fi

    # === PLOT CANDIDATES ===ß
    png_count=$(find "$output_dir" -maxdepth 1 -type f -name "*.png" | wc -l)

    if [ "$png_count" -eq 0 ]; then
        echo "No PNG plots found in $output_dir. Generating plots..."

        fil_count=$(find "$output_dir" -maxdepth 1 -type f -name "*.fil" | wc -l)
        if [ "$fil_count" -eq 0 ]; then
            echo "No .fil files found in $output_dir. Cannot generate plots. Skipping Slack upload."
        else
            for fil in "$output_dir"/*.fil; do
                [ -e "$fil" ] || continue
                python "/datax2/projects/LOFTS/LOFTS-Scripts/pipeline/plot-bandpass.py" -f "$fil" -s "$station"
            done

            echo "Uploading plots to Slack..."
            python "/datax2/projects/LOFTS/LOFTS-Scripts/pipeline/slack-bandpass.py" "$output_dir"
        fi
    else
        echo "Found $png_count PNG plot(s) in $output_dir. Skipping plotting and Slack upload."
    fi

    # clean .raw files after filterbank generation
    if [ -f "$output_dir/${target}.rawspec.0000.fil" ] && [ -f "$output_dir/${target}.rawspec.0001.fil" ] && [ -f "$output_dir/${target}.rawspec.0002.fil" ]; then
        echo "Cleaning raw files..."
        rm -f "$output_dir/${target}"*.raw
    fi
done

echo "===== Script finished at $(date) ====="

} 2> >(tee -a "$error_file" >&2) | tee -a "$log_file"

echo "Log written to: $log_file"
echo "Errors written to: $error_file"
