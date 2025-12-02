#!/bin/bash
TODAY=$(date +%Y-%m-%d)

# SE Progress Report 
ssh -t blc00_swe 'bash -lc "source /home/owen/anaconda3/etc/profile.d/conda.sh && conda activate SATP38 && cd /datax2/projects/LOFTS/LOFTS-Scripts/Progress  && python LOFTS-progress.py -s SE"'
csv_file_se="/datax2/projects/LOFTS/LOFTS-Scripts/Progress/LOFTS-observations-Progress-$TODAY-SE.csv"
scp blc00_swe:$csv_file_se ./master-csv 

# IE Progress Report
ssh -t blc00_irl 'bash -lc "source /opt/conda/etc/profile.d/conda.sh && conda activate IATP38 && cd /datax2/projects/LOFTS/LOFTS-Scripts/Progress  && python LOFTS-progress.py -s IE"'
csv_file_ie="/datax2/projects/LOFTS/LOFTS-Scripts/Progress/LOFTS-observations-Progress-$TODAY-IE.csv"
scp blc00_irl:$csv_file_ie ./master-csv 

# Call merge script 
python merge.py ./master-csv/LOFTS-observations-Progress-$TODAY-SE.csv ./master-csv/LOFTS-observations-Progress-$TODAY-IE.csv