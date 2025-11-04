#!/bin/bash 

filterbank=$1

target=$(basename "$filterbank" | cut -d'.' -f1)
path=$(dirname "$filterbank")

# check if file exists
if [ ! -f "$filterbank" ]; then
    echo "File does not exist. Exiting..."
    exit 1
fi

# check if directory exists, create it if it doesn't
if [ ! -d "${path}/${target}_prestomask" ]; then
    mkdir -p "${path}/${target}_prestomask"
fi

# check if mask exists
if [ -f "${path}/${target}_prestomask/${target}_rfifind.mask" ]; then
    echo "Mask already exists. Exiting..."

else
    echo "Generating mask for $target using PRESTO"
    docker run --rm -u root -v "$PWD":"$PWD" -w "$PWD" alex88ridolfi/presto5:latest rfifind -time 10 -ncpus 4 -noclip -freqsig 8 -timesig 8 -chanfrac 0.6 -intfrac 0.6 -o "${target}_prestomask/${target}" "$filterbank"

    # Uncomment the following lines if you want to convert .ps files to .png
    # for file in "${path}/${target}_prestomask/"*.ps; do
    #     convert -density 300 -rotate 90 "$file" "${file%.ps}.png"
    # done
fi
