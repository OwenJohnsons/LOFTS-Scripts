'''
Code Purpose: Make PDF of all LOFTS spectrums 
Author: Owen A. Johnson
'''

import numpy as np
import matplotlib.pyplot as plt 
import matplotlib
matplotlib.use("Agg") 
import glob 
from tqdm import tqdm
import smplotlib

files = sorted(glob.glob("/datax2/projects/LOFTS/spectrum-stamps/*seg0.dat"))
# 1:1.414


for spec in tqdm(files): 
    freq, power = np.loadtxt(spec, skiprows=1, unpack=True)
    source_name = spec.split('/')[-1].split('.')[0]
    plt.figure(figsize=(6*1.414, 6), dpi=100)
    plt.plot(freq, power, color='k')
    plt.xlabel('Frequency (MHz)')
    plt.ylabel('Power Arb.')
    plt.yscale('log')
    plt.title(source_name)
    plt.savefig('spectrum-plots/%s.png' % source_name)
    plt.close()
    