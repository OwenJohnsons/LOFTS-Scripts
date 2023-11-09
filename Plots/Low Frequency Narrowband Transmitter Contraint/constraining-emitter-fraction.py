#%%
'''
Code Purpose: Plot the constraining emitter fraction for a narrowband survey given the number of targets and the SEFD. 
Input: .csv with distances and IDs of targets observed in the Study. Tsys .csv file with specific Tsys values for various frequencies. 
Output: Narrowband constraining emitter fraction plot.
Author: Owen A. Johnson 
Last Major Update: 08/11/2023 
'''


import numpy as np 
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import scienceplots
plt.style.use(['science','ieee'])
import pandas as pd 
import time 
from EIRP_functions import *
cols =['#008DF9','#FFC33B','#009F81','#E20134','#8400CD','#FF6E3A','#00FCCF','#9F0162','#008DF9' ,
       '#FF5AAF','#00C2F9','#FFB2FD']

# --- Constants for LOFAR Survey --- #
Jansky = 1e-26 # 1 Jansky = 1e-26 Watts/m^2/Hz
obs_time = 15*60 # 15 minutes in seconds
# SEFD = 5e3*Jansky # System Equivalent Flux Density for LOFAR-HBA
lofar_dish_area = 1677.6
freqs = np.arange(110, 200, 10) # MHz

# # --- Transmitter EIRP --- 
EIRP_IP_radar = np.log10(pow(10,17)) # EIRP of a K1-type transmitter
# EIRP_typeII = np.log10(pow(10,26)) # EIRP of a K2-type transmitter
EIRP_LR_radar = np.log10(pow(10,13)) # EIRP of a planetary radar
EIRP_TV_broadcase = np.log10(pow(10,10)) # EIRP of a Aircraft radar
EIRP_EARTH = np.log10(0.7*pow(10, 17)) # EIRP of the Earth


# --- Reading in Gaia Data ---
start = time.time()
filename_lofar = 'input-csv/GDR3_LOFAR_trgts_Gmagd_filtered.csv'
filename_nenufar = 'input-csv/NENU_far_candidates.csv'
filename_lofts = 'input-csv/LOFTS_candidates.csv'
colsneeded_1 = ['distance_gspphot', 'TIC_ID']
colsneeded_2 = ['distance_gspphot', 'source_id']

chunk_size = 10 ** 6  # 1 million rows per chunk
data_chunks = []

def csv_reader(filename, chunk_size, colsneeded): 
    # Iterate over the file in chunks and append them to the list
    c = 0 # Chunk counter
    for chunk in pd.read_csv(filename, chunksize=chunk_size, usecols=colsneeded):
        c += 1; print('Chunk %s: length' % c , len(chunk))
        data_chunks.append(chunk)
    # Make a DataFrame from the list of chunks
    df = pd.concat(data_chunks)
    return df

# Chunk Loading  
LOFAR_chunks = csv_reader(filename_lofar, chunk_size, colsneeded_1)
LOFTS_chunks = csv_reader(filename_lofts, chunk_size, colsneeded_2)

# Concatenate the data chunks into a single DataFrame
print('Length of LOFAR df: %s' % len(LOFAR_chunks))
print('Length of LOFTS df: %s' % len(LOFTS_chunks))

end = time.time()
print('Time to read in Gaia data: %s' % (end - start))

# --- Reading in Tsys Data ---
Tsys_df = pd.read_csv('Tsys/Tsys.csv')
tsys_v = Tsys_df[Tsys_df['freq'] == 150]['Tsys'].mean()
print('Tsys at 150 MHz: %s' % tsys_v)

SEFD = calc_SEFD(lofar_dish_area, tsys_v, eff = 1.0)
print('SEFD: %s' % SEFD)

narrowband_LOFAR = np.log10(obsEIRP(5, SEFD*Jansky, LOFAR_chunks['distance_gspphot'], obs_time, 3, 0.1))
narrowband_LOFTS = np.log10(obsEIRP(5, SEFD*Jansky, LOFTS_chunks['distance_gspphot'], obs_time, 3, 0.1))

print('LOFAR Mean Narrowband (W/Hz): %s' % narrowband_LOFAR.mean())
print('LOFTS Mean Narrowband (W/Hz): %s' % narrowband_LOFTS.mean())
print('NenuFAR Mean Narrowband (W/Hz): %s' % narrowband_NenuFAR.mean())

# --- Narrowband Producing Fraction Calculations ---
max_narrowband_LOFAR = narrowband_LOFAR.max(); min_narrowband_LOFAR = narrowband_LOFAR.min()
max_narrowband_LOFTS = narrowband_LOFTS.max(); min_narrowband_LOFTS = narrowband_LOFTS.min()

LOFAR_trgt_count = []; LOFTS_trgt_count = []; NenuFAR_trgt_count = []

erip_values_LOFAR = np.linspace(min_narrowband_LOFAR, max_narrowband_LOFAR, 100)
erip_values_LOFTS = np.linspace(min_narrowband_LOFTS, max_narrowband_LOFTS, 100)

def value_function(narrowband_array, EIRP_array): 
    count_array = []
    for value in EIRP_array: 
        count = len(narrowband_array[narrowband_array < value])
        count_array.append(count)
    return count_array

LOFAR_trgt_count = value_function(narrowband_LOFAR, erip_values_LOFAR)
LOFTS_trgt_count = value_function(narrowband_LOFTS, erip_values_LOFTS)

# --- According to Geherls (1986) for 0 found civilisation the one side poission value is 2.995  ---
LOFAR_trgt_count = 2.995/np.array(LOFAR_trgt_count)
LOFTS_trgt_count = 2.995/(np.array(LOFTS_trgt_count)) 

LOFAR_erip_values = pow(10, erip_values_LOFAR)
LOFTS_erip_values = pow(10, erip_values_LOFTS)

print(len(LOFTS_erip_values), len(LOFTS_trgt_count))
print(len(LOFAR_erip_values), len(LOFAR_trgt_count))

# --- Plotting ---
fig, ax = plt.subplots(figsize=(8, 6))

ax.plot(LOFAR_erip_values, LOFAR_trgt_count, color=cols[3], lw=1, ls = '--')
plt.fill_between(LOFAR_erip_values, LOFAR_trgt_count, 3, color="none",hatch="X",edgecolor=cols[3], ls = '--', zorder = 2, label = 'Johnson et al. (2023)')

ax.plot(LOFTS_erip_values, LOFTS_trgt_count, color=cols[0], lw=1, ls = '-')
plt.fill_between(LOFTS_erip_values, LOFTS_trgt_count, 3, color="none",hatch="X",edgecolor=cols[0], ls = '-', zorder = 0, label = 'LOFTS')


plt.ylabel('Narrowband Producing Fraction $(f^n_c)$', fontsize=14)
plt.xlabel('Narrowband EIRP [W/Hz]', fontsize=14)

# Annotating the plot
plt.yscale('log')
plt.xscale('log')
plt.legend(loc='lower left', fontsize=14)

plt.xticks(fontsize=12); plt.yticks(fontsize=12)
plt.xlim(LOFTS_erip_values.min(), LOFAR_erip_values.max())
# ax.annotate('$\lambda = 0^{+ 2.995}_{-0.000}$', xy=(erip_values.min() + 0.2, 1e-6), fontsize=14)
plt.ylim(1e-10, 1e0)

# plt.show()
plt.savefig('output-plots/narrowband-fraction-2D.png', bbox_inches='tight', transparent=True, dpi=300)