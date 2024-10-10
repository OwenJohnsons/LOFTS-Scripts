# Code Purpose: Verify presence of filterbank files and then clean voltage and .raw files. 

# Arguments
# $1 : Directory path

path=$1

# LOGGING 
log_name=$(echo $path | awk -F'/' '{print $NF}')
log_file="/datax2/projects/LOFTS/logs/voltage_cleaner/${log_name}.out"
error_file="/datax2/projects/LOFTS/logs/voltage_cleaner/${log_name}.err"

# Create log file
touch $log_file
touch $error_file
exec > >(tee -a "$log_file") 2> >(tee -a "$error_file" >&2)

raw_data_path="/datax2/projects/LOFTS/raw"
echo "Running voltage cleaner on $path"

# Folders that begin with scan_
header_folders=$(find $path -type d -name "scan_*")
echo "Number of scan folders found : $(echo $header_folders | wc -w)"

for folder in $header_folders; do 
    # find file with .h extension
    h_file=$(find $folder -name "*.h")

    if grep -q "IE613" $h_file; then 
        station_prefix="IE613_16130"
        station="IE613"
    else 
        station_prefix="SE607_16070"
        station="SE607"
    fi

    # Grab scan .log file 
    log_file=$(find $folder -name "*.log" | head -n 1)
    zst_scan_path=$(awk 'NR==4 {print $2}' "$log_file")

    # replace lane0 with [[port]] and $station_prefix with $station_prefix[0:-1][[port]]
    zst_scan_path=$(echo "$zst_scan_path" | sed "s/lane0/lane[[port]]/g" | sed "s/$station_prefix/${station_prefix:0:-1}[[port]]/g")
    zst_time_suffix=$(echo "$zst_scan_path" | awk -F '.' '{print $(NF-2)}')
    obs_date=$(echo "$zst_time_suffix" | awk -F 'T' '{print $1}')
    target=$(echo "$zst_scan_path" | awk -F'/' '{print $9}')
    output_dir="$raw_data_path/$obs_date/$target"

    echo 
    echo
    echo "TARGET : $target"
    echo "--------------------------------------------------"

    # check if output_dir has 0000.fil, 0001.fil, and 0002.fil files and are not empty
    if [ -f "$output_dir/${target}.rawspec.0000.fil" ] && [ -f "$output_dir/${target}.rawspec.0001.fil" ] && [ -f "$output_dir/${target}.rawspec.0002.fil" ]; then
        # Check if file size is greater than 500 mega bytes
        if [ $(stat -c %s "$output_dir/${target}.rawspec.0000.fil") -gt 9000000000  ] && [ $(stat -c %s "$output_dir/${target}.rawspec.0001.fil") -gt 30000000000 ] && [ $(stat -c %s "$output_dir/${target}.rawspec.0002.fil") -gt 500000000 ]; then
            echo "Filterbank files exist in $output_dir." 
            # Check if there are any .raw files in the output directory
            raw_files=$(find $output_dir -name "*.raw")
            if [ ! -z "$raw_files" ]; then 
                echo "Raw files already exist in $output_dir. Cleaning raw files..."
                # Remove .raw files
                find $output_dir -name "*.raw" -print0 | xargs -0 rm
            else
                echo "No .raw files found in $output_dir."
            fi
            # Check if there are any .zst files in the source directory
            zst_files=$(find $path/scan_${target} -name "*.zst")
            if [ ! -z "$zst_files" ]; then 
                echo "ZST files exist in $path/scan_${target}. Cleaning zst files..."
                echo $zst_scan_path
                # Remove .zst files
                find $path/scan_${target} -name "*.zst" -print0 | xargs -0 rm
            else
                echo "No .zst files found in $path/scan_${target}."
            fi
            # cycle through lane0, lane1, lane2, lane3. 
            for port in {0..3}; do 
                # Check if there are any .zst files in the source directory
                # replace [[port]] with $port
                lane_path=$(echo "$zst_scan_path" | sed "s/[[port]]/$port/g")
                zst_files=$(find $lane_path -name "*.zst")
                if [ ! -z "$zst_files" ]; then 
                    echo "ZST files exist in lane${port}. Cleaning zst files..."
                    # Remove .zst files
                    find $lane_path -name "*.zst" -print0 | xargs -0 rm
                else
                    echo "No .zst files found in lane${port}."
                fi
            done

        else
            echo "Filterbank files exist in $output_dir but are smaller than expected manual check neeeded. Skipping voltage_cleaner..."
        fi
    else
        echo "Filterbank files do not exist in $output_dir. Skipping voltage_cleaner..."
    fi

done 