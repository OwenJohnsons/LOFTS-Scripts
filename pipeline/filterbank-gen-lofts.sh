# Code Purpose : Generate filterbanks for SETI purposes from raw data on the Breakthrough Listen backend. 

# Arguments 
# $1 : Directory path

path=$1
raw_data_path="/datax2/projects/LOFTS/raw"

# LOGGING 
time=$(date +"%H:%M")
log_name=$(echo $path | awk -F'/' '{print $NF}')
log_file="/datax2/projects/LOFTS/logs/filgen/${log_name}_${time}.out"
error_file="/datax2/projects/LOFTS/logs/filgen/${log_name}_${time}.err"


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

    if [ ! -d $output_dir ]; then 
        mkdir -p $output_dir
    fi

    # check if there are any .raw files in the output directory
    raw_files=$(find $output_dir -name "*.raw")
    if [ ! -z "$raw_files" ]; then 
        echo "Raw files already exist in $output_dir. Skipping lofar_udp_extractor..."
    else
        # Run lofar_udp_extractor inside the Singularity container
        singularity exec --bind /datax,/datax2 /datax2/obs/singularity/lofar-upm_latest.simg \
            lofar_udp_extractor -p 30 -M GUPPI \
            -I $h_file \
            -S 1 -b 0,412 \
            -i $zst_scan_path \
            -o "$output_dir/${target}.[[iter]].raw" \
            -m 4096
    fi

    # Check if 0000.fil, 0001.fil, and 0002.fil files exist in the output directory
    if [ -f "$output_dir/${target}.rawspec.0000.fil" ] && [ -f "$output_dir/${target}.rawspec.0001.fil" ] && [ -f "$output_dir/${target}.rawspec.0002.fil" ]; then
        echo "Filterbank files 0000.fil, 0001.fil, and 0002.fil exist in $output_dir. Skipping rawspec..."
    else
        # Run rawspec if the required .fil files do not exist
        rawspec -f 65536,8,64 -t 54,16,3072 -p 1,1,4 $output_dir/${target}
    fi
done