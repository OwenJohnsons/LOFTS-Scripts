import numpy as np 
import pandas as pd 
import argparse
import os, glob 

# postional argument 
def get_args():
    parser = argparse.ArgumentParser(description="Are there pulsars in my beam?")
    parser.add_argument('trgt', nargs='?', default=os.getcwd())
    
    return parser.parse_args()

def main():
    
    files = glob.glob("*_PSR_beam.csv")

    if files:
        latest = max(files, key=os.path.getmtime)
        print(latest)
    else:
        print("No matching files found.")

    df = pd.read_csv(latest)
    trgt = get_args().trgt
    
    # print summary for target
    matched = df[df['Obs'].str.contains(trgt)]
    
    if not matched.empty:
        print(f"Pulsars in beam for target {trgt}:")
        for _, row in matched.iterrows():
            print(f" Pulsar: {row['PSR']}, P0: {row['P0']:2f} s, DM: {row['DM']:.2f} pc/cm^3, Sep: {row['Sep']:.2f} deg")
    else:
        print(f"No pulsars found in beam for target {trgt}.")
   

if __name__ == "__main__":
    main()