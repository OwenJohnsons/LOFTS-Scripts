#!/bin/bash

# Define the headers for the .csv files
headers="Beam_ID,Candidate_ID,MJD,DM,width_MS,SNR,Start_Freq,End_Freq,Image_File,Subband_ID,Filterbank_File"

# Directory to search for .cands files
directory=${1:-$(pwd)}

# Loop through each .cands file in the specified directory
find "$directory" -type f -name "*.cands" | while read -r cands_file; do
    # Define the output CSV file name
    csv_file="${cands_file%.cands}.csv"

    # Print the headers and convert .cands file content to .csv format
    {
        echo "$headers"
        awk '{print $1","$2","$3","$4","$5","$6","$7","$8","$9","$10","$11}' "$cands_file"
    } > "$csv_file"

    echo "Converted $cands_file to $csv_file"
done
