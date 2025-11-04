import sys
import pandas as pd
from datetime import datetime

def parse_observation_file(file_path):
    data = {
        'Observation Target': [],
        'Date': [],
        'Time': [],
        'TObs (hours)': [],
        'RA': [],
        'DEC': []
    }
    
    previous_end_time = None

    with open(file_path, 'r') as file:
        lines = file.readlines()

    for line in lines:
        if line.startswith('#') or not line.strip():
            continue

        parts = line.split(':')
        if len(parts) < 3:
            continue
        
        # Extract observation target
        observation_target = parts[1].strip().split()[0]

        # Extract date and time
        date_time_str = parts[0].strip()
        
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

        # Extract RA and DEC, ensure proper format
        print(parts[3])
        ra_dec_str = parts[2].strip().strip("[]").split(',')
        if len(ra_dec_str) >= 2:
            try:
                ra = float(ra_dec_str[0].strip())
                dec = float(ra_dec_str[1].strip())
            except ValueError:
                print(f"Error parsing RA/DEC values in line: {line}")
                continue
        else:
            print(f"RA/DEC information missing or incomplete in line: {line}")
            continue

        # Append data to columns
        data['Observation Target'].append(observation_target)
        data['Date'].append(date_time_obj.date())
        data['Time'].append(date_time_obj.time())
        data['TObs (hours)'].append(t_obs)
        data['RA'].append(ra)
        data['DEC'].append(dec)

    return pd.DataFrame(data)

def write_to_csv(df, output_file='observations.csv'):
    df.to_csv(output_file, index=False)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python script.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    df = parse_observation_file(input_file)
    write_to_csv(df)

    print(f"Processed {len(df)} observations. Output saved to 'observations.csv'.")
