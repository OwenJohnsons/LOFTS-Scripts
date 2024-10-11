# Arguments 
# $1 : Directory path

path=$1

# LOGGING 
time=$(date +"%H:%M")
log_name=$(echo $path | awk -F'/' '{print $NF}')
log_file="/mnt/ucc3_data2/data/LOFTS/logs/filgen/${log_name}_${time}.out"
error_file="/mnt/ucc3_data2/data/LOFTS/logs/filgen/${log_name}_${time}.err"

folders=$(find $path -type d \( -name "*LOFTS*" -o -name "*B*" \))
date=$(echo $path | awk -F'/' '{print $(NF)}' | sed 's/\([0-9]\{4\}\)\([0-9]\{2\}\)\([0-9]\{2\}\).*/\1-\2-\3/')
echo "Number of folders found : $(echo $folders | wc -w)"
echo "Date of observations: $date"

for folder in $folders; do 
    # last part of the path ignore the first 8 characters
    target=$(echo $folder | awk -F'/' '{print $NF}' | cut -c 15-)
    echo "Processing Target : $target"

    output_dir="/mnt/ucc3_data2/data/LOFTS/filterbanks/$date/$target"
    if [ ! -d $output_dir ]; then 
        mkdir -p $output_dir
    fi

    # check if there are any .fil files in the output directory
    fil_files=$(find $output_dir -name "*.fil")
    if [ ! -z "$fil_files" ]; then 
        echo "Filterbank files already exist in $output_dir. Skipping lofar_udp_extractor..."
    else
        voltages=$(find $folder -name "*.zst")
        
        # Check if there are four .zst voltages 
        if [ $(echo $voltages | wc -w) -ne 4 ]; then 
            echo "There are not four .zst files in $folder. Skipping lofar_udp_extractor..."
            continue
        fi

        scan_path=$(echo ${voltages[0]} | sed 's/udp_16131/udp_1613[[port]]/')
        echo "Scan path : $scan_path"

         raw_files=$(find $output_dir -name "*.raw")
        if [ ! -z "$raw_files" ]; then 
            echo "Raw files already exist in $output_dir. Skipping lofar_udp_extractor..."
        else
            # Run lofar_udp_extractor inside the Singularity container
            singularity exec --bind /datax,/datax2 /datax2/obs/singularity/lofar-upm_latest.simg \
                lofar_udp_extractor -p 30 -M GUPPI \
                -S 1 -b 0,412 \
                -i $zst_scan_path \
                -o "$output_dir/${target}.[[iter]].raw" \
                -m 4096
        fi
    fi

    # Check if 0000.fil, 0001.fil, and 0002.fil files exist in the output directory
    if [ -f "$output_dir/${target}.rawspec.0000.fil" ] && [ -f "$output_dir/${target}.rawspec.0001.fil" ] && [ -f "$output_dir/${target}.rawspec.0002.fil" ]; then
        echo "Filterbank files 0000.fil, 0001.fil, and 0002.fil exist in $output_dir. Skipping rawspec..."
    else
        # Run rawspec if the required .fil files do not exist
        rawspec -f 65536,8,64 -t 54,16,3072 -p 1,1,4 $output_dir/${target}
    fi
done
