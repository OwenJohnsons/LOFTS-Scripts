'''
Author: Owen A. Johnson 
Date of Last Major Update: Novemeber 2025
Code Purpose: Checks if there are known pulsar in the beam of LOFTS observations. 
'''

import argparse
import pandas as pd
from astropy.coordinates import SkyCoord
from astropy import units as u
from astropy.table import Table
import numpy as np
from psrqpy import QueryATNF
from astropy.table import Table

def get_args(): 
    parser = argparse.ArgumentParser(description="Check for known pulsars in LOFTS beam.")
    parser.add_argument('-i', '--input', type=str, required=True, help='Input .csv with headers labelled ra_deg, dec_deg.')
    parser.add_argument('-b', '--beam_radius', type=float, default=2.59, help='Beam radius in degrees, deafult is 2.59 degrees for LOFAR HBAs at 150 MHz.')
    
    return parser.parse_args()

def grab_pulsar(): 
    query = QueryATNF(params=['RAJD', 'DECJD', 'P0', 'DM', 'NAME'])
    table = query.table.to_pandas()
    
    return table.dropna(subset=['RAJD', 'DECJD'])

def main():
    args = get_args()
    
    obs_tbl = pd.read_csv(args.input)
    obs_tbl = obs_tbl[obs_tbl['filename'].str.contains('0000.fil')].reset_index(drop=True)
    pulsar_tbl = grab_pulsar()
    
    fnames = obs_tbl['filename'].values
    
    beam_radius = args.beam_radius * u.deg
    
    obs_ra, obs_dec = obs_tbl['ra_deg'].values, obs_tbl['dec_deg'].values
    obs_coords = SkyCoord(ra=obs_ra*u.deg, dec=obs_dec*u.deg, frame='icrs')
    
    pulsar_ra, pulsar_dec = pulsar_tbl['RAJD'].values, pulsar_tbl['DECJD'].values
    pulsar_coords = SkyCoord(ra=pulsar_ra*u.deg, dec=pulsar_dec*u.deg, frame='icrs') 
    
    # make df of pulsars in beam
    df = pd.DataFrame(columns=['Obs', 'PSR', 'P0', 'DM', 'Sep'])
    
    paths = []; psr_names = []; p0s = []; dms = []; seps = []
        
    for i, obs_coord in enumerate(obs_coords): 
        separations = obs_coord.separation(pulsar_coords)
        in_beam = separations < beam_radius
        
        if np.any(in_beam):
            matched_pulsars = pulsar_tbl[in_beam]
            print(f"Observation File: {fnames[i]}, RA: {obs_ra[i]}, Dec: {obs_dec[i]}")
            print("Matched Pulsars:")
            for _, row in matched_pulsars.iterrows():
                sep = obs_coord.separation(SkyCoord(ra=row['RAJD']*u.deg, dec=row['DECJD']*u.deg))
                print(f" {row['NAME']}, P0: {row['P0']} s, DM: {row['DM']} pc/cm^3, Sep: {sep.to(u.deg).value:.2f} deg")
                paths.append(fnames[i]); psr_names.append(row['NAME']); p0s.append(row['P0']); dms.append(row['DM']); seps.append(sep.to(u.deg).value)
            print("\n")
            
    df['Obs'] = paths; df['PSR'] = psr_names; df['P0'] = p0s; df['DM'] = dms; df['Sep'] = seps
    df.to_csv(f"{args.input.split('.')[0]}_PSR_beam.csv", index=False)
            
if __name__ == "__main__":
    main()   