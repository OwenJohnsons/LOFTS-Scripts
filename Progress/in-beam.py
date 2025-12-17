'''
Author: Owen A. Johnson 
Date of Last Major Update: December 2025
Code Purpose: Checks if a provided coordinate is within the beam of a LOFTS observation. 
'''

import argparse
import pandas as pd
import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord

def get_args(): 
    parser = argparse.ArgumentParser(description="Check for known pulsars in LOFTS beam.")
    parser.add_argument('-i', '--input', type=str, default="./master-csv/LOFTS-total-progress.csv", help='Input .csv with headers labelled ra_deg, dec_deg.')
    parser.add_argument('-b', '--beam_radius', type=float, default=2.59, help='Beam radius in degrees, deafult is 2.59 degrees for LOFAR HBAs at 150 MHz.')
    # positional ra and dec 
    parser.add_argument('ra', nargs='?', type=str, help='Right Ascension')
    parser.add_argument('dec', nargs='?', type=str, help='Declination')
    
    return parser.parse_args()


def main(): 
    args = get_args()
    
    obs_tbl = pd.read_csv(args.input)
    obs_tbl = obs_tbl[obs_tbl['filename'].str.contains('0002.fil')].reset_index(drop=True)
    obs_ra, obs_dec = obs_tbl['ra_deg'].values, obs_tbl['dec_deg'].values
    obs_coords = SkyCoord(ra=obs_ra*u.deg, dec=obs_dec*u.deg, frame='icrs')
    
    search_coord = SkyCoord(ra=float(args.ra)*u.deg, dec=float(args.dec)*u.deg, frame='icrs')
    
    print("Searching within %s degrees beam radius for coordinate (%s, %s)." % (args.beam_radius, args.ra, args.dec))
    
    beam_radius = args.beam_radius * u.deg
    seperation = search_coord.separation(obs_coords)
    
    in_beam = seperation < beam_radius
    
    # print results
    if np.any(in_beam): 
        matched_obs = obs_tbl[in_beam]
        print("Matched Observations:")
        for _, row in matched_obs.iterrows(): 
            sep = search_coord.separation(SkyCoord(ra=row['ra_deg']*u.deg, dec=row['dec_deg']*u.deg))
            print(f"Station: {row['station']}, Filename: {row['filename']}, RA: {row['ra_deg']:.2f}, Dec: {row['dec_deg']:.2f}, Sep: {sep.deg:.2f} degrees")
    else: 
        print("No observations found within the specified beam radius.")

if __name__ == "__main__": 
    main()