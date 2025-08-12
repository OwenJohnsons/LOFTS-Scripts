#!/bin/bash

# Code Purpose: Verify presence of filterbank files and then clean voltage and .raw files. 

# Arguments:
# -f : Force cleanup without checking filterbank file sizes
# $1 : Directory path to scan

# -----------------------------
# PARSE ARGS
# -----------------------------
force=0
while [[ "$1" == -* ]]; do
    case "$1" in
        -f|--force)
            force=1
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# -----------------------------
# INPUT PATH
# -----------------------------
path=$1
if [ -z "$path" ]; then
    echo "Usage: $0 [-f|--force] <scan-path>"
    exit 1
fi

# -----------------------------
# LOGGING
# -----------------------------
log_name=$(echo "$path" | awk -F'/' '{print $NF}')
log_file="/datax2/projects/LOFTS/logs/voltage_cleaner/${log_name}.out"
error_file="/datax2/projects/LOFTS/logs/voltage_cleaner/${log_name}.err"

mkdir -p "$(dirname "$log_file")"
touch "$log_file"
touch "$error_file"
exec > >(tee -a "$log_file") 2> >(tee -a "$error_file" >&2)

raw_data_path="/datax2/projects/LOFTS"
echo "Running voltage cleaner on $path"
[ "$force" -eq 1 ] && echo "Force mode: skipping file size checks"

# -----------------------------
# FIND SCAN FOLDERS
# -----------------------------
header_folders=$(find "$path" -type d -name "scan_*")
echo "Number of scan folders found : $(echo "$header_folders" | wc -w)"

for folder in $header_folders; do 
    h_file=$(find "$folder" -name "*.h")

    if grep -q "IE613" "$h_file"; then
        station_prefix="IE613_16130"
        station="IE613"
    else 
        station_prefix="SE607_16070"
        station="SE607"
    fi

    log_file=$(find "$folder" -name "*.log" | head -n 1)
    zst_scan_path=$(awk 'NR==4 {print $2}' "$log_file")
    zst_scan_path=$(echo "$zst_scan_path" | sed "s/lane0/lane__PORT__/" | sed "s/$station_prefix/${station_prefix::-1}__PORT__/")
    zst_time_suffix=$(echo "$zst_scan_path" | awk -F '.' '{print $(NF-2)}')
    obs_date=$(echo "$zst_time_suffix" | awk -F 'T' '{print $1}')
    full_target=$(echo "$zst_scan_path" | awk -F'/' '{print $9}')
    target=${full_target#scan_}  # Strip scan_ prefix if present

    # Candidate output dirs
    output_dir1="$raw_data_path/$obs_date/$target"
    prev_day=$(date -d "$obs_date -1 day" +%Y-%m-%d)
    alt_output_dir1="$raw_data_path/$prev_day/$target"

    echo
    echo
    echo "TARGET : $target"
    echo "--------------------------------------------------"
    echo "Checking for filterbank files in:"
    echo " - $output_dir1"
    echo " - $alt_output_dir1"

    check_dir=""
    for dir in "$output_dir1" "$alt_output_dir1"; do
        if [ -f "$dir/${target}.rawspec.0000.fil" ]; then
            check_dir="$dir"
            break
        fi
    done

    if [ -n "$check_dir" ]; then
        if [ -f "$check_dir/${target}.rawspec.0001.fil" ] && [ -f "$check_dir/${target}.rawspec.0002.fil" ]; then
            if [ "$force" -eq 1 ] || (
                [ $(stat -c %s "$check_dir/${target}.rawspec.0000.fil") -gt 9000000000 ] &&
                [ $(stat -c %s "$check_dir/${target}.rawspec.0001.fil") -gt 30000000000 ] &&
                [ $(stat -c %s "$check_dir/${target}.rawspec.0002.fil") -gt 500000000 ]
            ); then

                echo "Filterbank files exist in $check_dir."

                # Remove .raw files
                raw_files=$(find "$check_dir" -name "*.raw" 2>/dev/null)
                if [ -n "$raw_files" ]; then
                    echo "Cleaning .raw files in $check_dir"
                    find "$check_dir" -name "*.raw" -print0 | xargs -0 rm
                else
                    echo "No .raw files found."
                fi

                # Remove .zst files from scan or target dir
                zst_folder_path=""
                if [ -d "$path/scan_${target}" ]; then
                    zst_folder_path="$path/scan_${target}"
                elif [ -d "$path/${target}" ]; then
                    zst_folder_path="$path/${target}"
                fi

                if [ -n "$zst_folder_path" ]; then
                    zst_files=$(find "$zst_folder_path" -name "*.zst" 2>/dev/null)
                    if [ -n "$zst_files" ]; then
                        echo "Cleaning .zst files in $zst_folder_path"
                        find "$zst_folder_path" -name "*.zst" -print0 | xargs -0 rm
                    else
                        echo "No .zst files found in $zst_folder_path"
                    fi
                fi

                # Clean .zst from all lanes
                for port in {0..3}; do 
                    lane_path=$(dirname "$(echo "$zst_scan_path" | sed "s/__PORT__/$port/")")
                    # echo "Checking lane$port at path: $lane_path"
                    zst_files=$(find "$lane_path" -name "*.zst" 2>/dev/null)
                    if [ -n "$zst_files" ]; then
                        echo "Cleaning .zst files in lane$port"
                        find "$lane_path" -name "*.zst" -print0 | xargs -0 rm
                    else
                        echo "No .zst files found in lane$port"
                    fi
                done

            else
                echo "Filterbank files exist but are too small. Skipping (use -f to override)."
            fi
        else
            echo "Missing one or more filterbank files. Skipping."
        fi
    else
        echo "Filterbank files not found in any expected folders. Skipping voltage_cleaner..."
    fi
done
