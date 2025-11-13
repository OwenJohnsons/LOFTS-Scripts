#%%
import sys
import pandas as pd
from datetime import datetime
from glob import glob 
import re
import os
import numpy as np
from astropy.coordinates import Angle

def radians2hhmmss(ra_radians, dec_radians):
    # Convert RA from radians to HHMMSS
    ra_angle = Angle(ra_radians, unit="rad")
    ra_hms = ra_angle.to_string(unit="hour", sep=":")

    # Convert DEC from radians to DDMMSS
    dec_angle = Angle(dec_radians, unit="rad")
    dec_dms = dec_angle.to_string(unit="deg", sep=":")

    return ra_hms, dec_dms

def parse_observation_file(file_paths):
    data = {
        'Observation Target': [],
        'Date': [],
        'Time': [],
        'TObs (hours)': [],
        'RA': [],
        'DEC': []
    }
    
    previous_end_time = None

    for file_path in file_paths:
        print(f"Processing file: {file_path}")
        counter = 0
        with open(file_path, 'r') as file:
            lines = file.readlines()

        for line in lines:
            if line.startswith('#') or not line.strip():
                continue

            parts = line.split(':')
            # Extract observation target
            observation_target = parts[3].strip().split(' ')[0]

            # Extract date and time
            date_time_str = str(line[0:16])
            
            # Handle time string with or without minutes
            try:
                if len(date_time_str) == 13:  # '%Y-%m-%dT%H'
                    date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%dT%H')
                else:
                    date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                print(f"Error parsing date-time string: {date_time_str}")
                continue

            # Calculate observation duration (TObs)
            if previous_end_time:
                t_obs = (date_time_obj - previous_end_time).total_seconds() / 3600.0  # TObs in hours
            else:
                t_obs = 0.0
            previous_end_time = date_time_obj

            if counter == 0:
                t_obs = 1.35

            # Extract RA and DEC, ensure proper format
            matches = re.findall(r"[-+]?\d*\.\d+|\d+", parts[3])  # Finds all float numbers in the line
            ra = float(matches[-3]); dec = float(matches[-2])

            # Append data to columns
            # format date as 'YYYY-MM-DD' 
            data['Observation Target'].append(observation_target)
            data['Date'].append(date_time_obj.strftime('%Y-%m-%d'))
            data['Time'].append(date_time_obj.time())
            data['TObs (hours)'].append(t_obs)
            data['RA'].append(ra)
            data['DEC'].append(dec)

            counter += 1

    return pd.DataFrame(data)

def write_to_csv(df, output_file='observations.csv'):
    df.to_csv(output_file, index=False)

if __name__ == '__main__':

    schedule_files = glob('sched/observed/sched-REALTA-*.txt')
    print('Number of observed schedules:', len(schedule_files))
    df = parse_observation_file(schedule_files)
    print(df.head())
    write_to_csv(df)
    
    coords_df = df[['Observation Target', 'RA', 'DEC']]
    ra, dec = radians2hhmmss(coords_df['RA'], coords_df['DEC'])
    coords_df['RA'] = ra; coords_df['DEC'] = dec
    print(coords_df.head())
    coords_df.to_csv('LOFTS-coords.csv', index=False)

    os.system('rsync -avzP LOFTS-coords.csv blc00_swe:/datax2/projects/LOFTS/csv')

    print(f"Processed {len(df)} observations. Output saved to 'observations.csv'.")
