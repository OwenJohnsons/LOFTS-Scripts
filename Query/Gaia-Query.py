#%%
''' 
Code Purpose: To query the Gaia DR3 database for targets within provided Zenith pointings of LOFAR beam across a year. 
Author: Owen A. Johnson
Date: 2023-18-10 
'''

import pandas as pd 
import numpy as np 
import matplotlib as plt
from astroquery.vizier import Vizier
from astropy.coordinates import Angle, SkyCoord
import astropy.coordinates as coord
from astropy import units as u
from astroquery.gaia import Gaia
import time 

elasp_time = time.time()

# --- Setup Parameters --- 
Gaia.MAIN_GAIA_TABLE = "gaiadr3.gaia_source"  # Select Data Release 3
Gaia.ROW_LIMIT = -1  # No limit on number of rows returned
save_increments = 75 # Save data every 10 pointings

# --- Loading LOFAR beam pointings ---
pointings_ra, pointings_dec, times = np.loadtxt('zenith_ra_dec.txt', unpack=True, delimiter=',', skiprows=1)
pointings_vec = np.vstack((pointings_ra, pointings_dec)).T
pointing_coords = SkyCoord(ra=pointings_vec[:,0]*u.degree, dec=pointings_vec[:,1]*u.degree)
print('Number of pointings: ', len(pointings_vec))
beam_radius = 2.59/2 # degrees, FWHM at 150 MHz

data_frames = []; indv_count = []
total_count = 0; actual_count = 0; part = 0
count_2σ = 0; count_3σ = 0
# Loop through the pointing coordinates and retrieve data from Gaia
for i in (range(0, len(pointing_coords))):
    start = time.time()
    # --- Query Gaia ---
    j = Gaia.cone_search_async(pointing_coords[i], radius=u.Quantity(beam_radius, u.deg))
    r = j.get_results()
    print('\n---\nPointing %s of %s' % (i, len(pointing_coords)))
    print('RA (deg): ' '{:.3f}'.format(pointing_coords[i].ra.degree), '\nDEC (deg): ' '{:.3f}'.format(pointing_coords[i].dec.degree))
    total_count += len(r)
    indv_count.append(total_count)
    df = r.to_pandas()
    
    # --- Seperation between pointing and target ---
    sep = pointing_coords[i].separation(SkyCoord(ra=df['ra']*u.degree, dec=df['dec']*u.degree)).degree
    coord_error = np.sqrt(df['ra_error']**2 + df['dec_error']**2)
    extension = sep + coord_error; extension_2σ = sep + 2*coord_error; extension_3σ = sep + 3*coord_error
    filter_mask_1σ = extension < beam_radius
    filter_mask_2σ = extension_2σ < beam_radius
    filter_mask_3σ = extension_3σ < beam_radius
    
    # --- apply filter mask ---
    print('Number of targets in beam within 1σ: ', len(df[filter_mask_1σ]))
    print('Number of targets in beam within 2σ: ', len(df[filter_mask_2σ]))
    print('Number of targets in beam within 3σ: ', len(df[filter_mask_3σ]))
    count_2σ += len(df[filter_mask_2σ])
    count_3σ += len(df[filter_mask_3σ])

    df = df[filter_mask_1σ]
    actual_count += len(df)
    end = time.time()
    print('Time taken to query Gaia for this beam: %s secs.' % "{:.1f}".format(end - start))
    print('Elapsed time: %s secs.' % "{:.1f}".format(end - elasp_time))
    # --- Add TIC ID column ---
    df['beam_num'] = i
    data_frames.append(df)

    print('Progress: ', "{:.1f}".format((i/len(pointing_coords))*100), '%')

    if (i % save_increments == 0):
        part += 1 
        # Concatenate the individual data frames into a single total data frame
        total_dataframe = pd.concat(data_frames, ignore_index=True)
        # Remove duplicate Gaia IDs 
        total_dataframe.drop_duplicates(subset='source_id', inplace=True)
        total_dataframe.to_csv('csv/zenith-Gaia-query-part-%s.csv' % part, index=False)
        print('Dataframe Length:', len(total_dataframe))
        data_frames = []


print('\n---\nTotal number of targets found in beam: ', total_count)
print('Number of targets found in beam (1σ): ', len(total_dataframe))
print('Number of targets found in beam (2σ): ', count_2σ)
print('Number of targets found in beam (3σ): ', count_3σ)

np.savetxt('csv/indv_count.txt', indv_count, fmt='%d', delimiter=' ', header='Number of targets found in beam for each pointing', comments='# Number of targets found in beam for each pointing (cummlative)')
