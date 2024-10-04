# Code Purpose : Organize files in a directory based on their header! 

# Arguments 
# $1 : Directory path

path=$1

project_path="/datax2/projects/LOFTS"

# find all filterbanks in sub-directories of the given path
filterbank_paths=$(find $path -name "*.fil")
echo "Number of filterbanks found : $(echo $filterbank_paths | wc -w)"

for path in $filterbank_paths; do 
    date=$(header "$path" | awk -F': ' 'NR==16 {print $2}')
    date=$(echo $date | sed 's/\//-/g')
    if [ -d $project_path/$date ]; then 
        mv $path $project_path/$date
    else 
        mkdir $project_path/$date
        mv $path $project_path/$date
    fi
done

echo "$(echo $filterbank_paths | wc -w) files organized successfully!"