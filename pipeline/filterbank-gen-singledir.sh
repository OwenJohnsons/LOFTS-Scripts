# Arguments 
# $1 : Directory path
# $2 : Station prefix: ie or se 

path=$1
station=$2

# check station prefix
if [ "$station" != "IE" ] && [ "$station" != "SE" ]; then 
    echo "Invalid station prefix. Use IE or SE. Exiting..."
    exit 1
fi
if [ "$station" == "IE" ]; then 
    port_prefix=1613
else
    port_prefix=1607
fi

# LOGGING 
time=$(date +"%H:%M")
log_name=$(echo $path | awk -F'/' '{print $NF}')
log_file="/datax2/projects/LOFTS/data/LOFTS/logs/filgen/${log_name}_${time}.out"
error_file="/datax2/projects/LOFTS/data/LOFTS/logs/filgen/${log_name}_${time}.err"

folders=$(find $path -type d \( -name "*scan_*" -o -name "*scan_B*" \))
date=$(echo $path | awk -F'/' '{print $(NF)}' | sed 's/^.*sid\([0-9]\{8\}\)T.*/\1/' | sed 's/\([0-9]\{4\}\)\([0-9]\{2\}\)\([0-9]\{2\}\)/\1-\2-\3/')

echo "Number of folders found : $(echo $folders | wc -w)"
echo "Date of observations: $date"

for folder in $folders; do 
    echo "Processing folder: $folder"
    # last part of the path ignore the first 8 characters
    target=$(echo $folder | awk -F'/' '{print $NF}' | sed 's/^.\{5\}//')
    echo "Processing Target : $target"

    output_dir="/datax2/projects/LOFTS/$date/$target"
    if [ ! -d $output_dir ]; then 
        mkdir -p $output_dir
    fi

    echo "Output directory: $output_dir"

    # check if there are any .fil files in the output directory
    fil_files=$(find $output_dir -name "*.fil")
    if [ ! -z "$fil_files" ]; then 
        echo "Filterbank files already exist in $output_dir. Skipping lofar_udp_extractor..."
    else
        voltages=$(find $folder -name "*${port_prefix}0*.zst")
        

        # zst_scan_path=$(sed 's/udp_16130/udp_1613[[port]]/' <<< "${voltages[0]}")
        zst_scan_path=$(echo "${voltages[0]}" | sed "s/udp_${port_prefix}0/udp_${port_prefix}[[port]]/")
        echo "Scan path: $zst_scan_path"


        metadata=$(find $folder -name "*.h")

        raw_files=$(find $output_dir -name "*.raw")
        if [ ! -z "$raw_files" ]; then 
            echo "Raw files already exist in $output_dir. Skipping lofar_udp_extractor..."
        else
            # Run lofar_udp_extractor inside the Singularity container
            echo "Running lofar_udp_extractor..."
            singularity exec --bind /datax,/datax2 /datax2/obs/singularity/lofar-upm_latest.simg \
                lofar_udp_extractor -p 30 -M GUPPI \
                -S 1 -b 0,412 \
                -i ${zst_scan_path} \
                -o "${output_dir}/${target}.[[iter]].raw" \
                -m 4096 -I "${metadata}" 
        fi
    fi

    # Check if 0000.fil, 0001.fil, and 0002.fil files exist in the output directory
    if [ -f "$output_dir/${target}.rawspec.0000.fil" ] && [ -f "$output_dir/${target}.rawspec.0001.fil" ] && [ -f "$output_dir/${target}.rawspec.0002.fil" ]; then
        echo "Filterbank files 0000.fil, 0001.fil, and 0002.fil exist in $output_dir. Skipping rawspec..."
    else
        echo "Running rawspec..."
        # Run rawspec if the required .fil files do not exist
        rawspec -f 65536,8,64 -t 54,16,3072 -p 1,1,4 $output_dir/${target}
    fi

    # clean .raw files after filterbank generation
    if [ -f "$output_dir/${target}.rawspec.0000.fil" ] && [ -f "$output_dir/${target}.rawspec.0001.fil" ] && [ -f "$output_dir/${target}.rawspec.0002.fil" ]; then
        echo "Cleaning raw files..."
        rm -f $output_dir/${target}*.raw
    fi
done
