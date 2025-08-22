'''
Use psrqpy to get the population of pulsars in the low frequency range
'''
#%%
from psrqpy import QueryATNF
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
# import smplotlib 
import scienceplots; plt.style.use(['science', 'ieee'])

query = QueryATNF(params = ['JNAME', 'P0', 'SURVEY', 'R_Lum', 'Dist'])
table = query.table
dataframe = table.to_pandas()

print('Number of pulsars in ATNF Catalog:', len(dataframe))
survey_tags = dataframe['SURVEY']

surveys = ['lotaas', 'tulipp', 'mwa_smart', 'gbncc', 'gbt350']
print('Checking the folling surveys:', surveys)

c = 0; idx = 0; idxs = []

for tag in survey_tags:
    tags = str(tag).split(',')
    for survey in surveys:
        if survey in tags:
            c += 1
            idxs.append(idx)
            break
    idx += 1 
    
low_freq_pulsars = dataframe.iloc[idxs]
print('Number of low frequency pulsars (sub 350 MHz):', len(low_freq_pulsars))
low_freq_pulsars = low_freq_pulsars.dropna(subset=['R_LUM'])
low_freq_pulsars = low_freq_pulsars.dropna(subset=['DIST'])

print('Number of low frequency pulsars with luminosity and distance measurements:', len(low_freq_pulsars))
print('Percentage of low frequency pulsars with luminosity and distance measurements:', len(low_freq_pulsars)/len(dataframe)*100)
print('Period Range: %s (ms) - %s (s)' % (np.min(low_freq_pulsars['P0'])*1000, np.max(low_freq_pulsars['P0'])))

def luminosity_scale(L1, f1, distance): 
    '''
    L_2 = L_1 * (f_2/f_1)^a
    '''
    f2 = 400 # MHz
    a = -1.6

    return (L1*(f2/f1)**a)/(4*np.pi*distance**2)

L_lo = luminosity_scale(low_freq_pulsars['R_LUM'], 150, low_freq_pulsars['DIST'])

print('Flux Range: %s - %s Jy' % (np.min(L_lo), np.max(L_lo)))
print('Pulsar with the radio luminosity:', low_freq_pulsars.iloc[np.argmax(L_lo)]['JNAME'])

# --- 2D histogram of period and luminosity --- 
plt.figure(dpi = 300, figsize = (5, 4))
# plt.title('Low Frequency Pulsar Population (sub 350 MHz) : n = %s' % len(low_freq_pulsars))
plt.scatter(low_freq_pulsars['P0'], L_lo, edgecolors='k', s=2)
plt.xlabel('Period (s)')
plt.ylabel('Flux Density (Jy)')
plt.yscale('log'); plt.xscale('log')
# plt.axhline(0.37, color='r', linestyle='--', label='One Hour Sensitivity Limit (Jy)')
print('Number of pulsars with flux greater than 0.37 Jy:', len(L_lo[L_lo > 0.37]))
# plt.axhline(0.2, color='b', linestyle='--', label='LOFAR Sensitivity Limit (Jy)')
plt.xlim(0.001, 50)

annotate_name = True
keypulsars = ['J0534+2200', 'J1921+2153', 'J0332+5434', 'J0857+3349']
if annotate_name == True: 
    for name in low_freq_pulsars['JNAME']:
        if name in keypulsars: 
            plt.scatter(low_freq_pulsars[low_freq_pulsars['JNAME'] == name]['P0'], L_lo[low_freq_pulsars['JNAME'] == name], edgecolors='r', s=5)
            plt.text(low_freq_pulsars[low_freq_pulsars['JNAME'] == name]['P0'], L_lo[low_freq_pulsars['JNAME'] == name], name, fontsize=5)

plt.savefig('lo-frequency-pulsar-population.png', dpi=200)
