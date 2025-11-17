#!/usr/bin/env python3

import argparse
import os
import glob 
import your
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.ticker import FixedLocator
import scienceplots; plt.style.use(['science','ieee', 'no-latex'])
from tqdm import tqdm

fil_list = glob.glob('/datax2/projects/LOFTS/*/*/*0001*.fil')
out_dir = '/datax2/projects/LOFTS/spectrum-stamps/'

def main(): 

    print('Number of filterbanks: ', len(fil_list))
    
    for fil in tqdm(fil_list):
        fil_obj = your.Your(fil)
        header = fil_obj.your_header
        
        # grab 10% segments of an observation 
        n_seg = 10
        seg_len = int(header.native_nspectra / n_seg)

        total_spectrum = []

        segments = []
        for i in range(n_seg):
            strt_samp = i * seg_len
            fil_data = fil_obj.get_data(nstart=strt_samp, nsamp=seg_len)
            spectrum = np.mean(fil_data, axis=0)
            # freq and power to .dat 
            freq = np.linspace(header.fch1, header.fch1 + header.foff * header.nchans, header.nchans)
            out_dat = np.column_stack((freq, spectrum))
            out_file = os.path.join(out_dir, f"{os.path.basename(fil).replace('.fil', '')}_seg{i}.dat")
            np.savetxt(out_file, out_dat, fmt='%.6f', header='Frequency(MHz) Power(Arb.)')
            total_spectrum.append(spectrum)
        
    # plot total spectrum
    total_spectrum = np.mean(np.array(total_spectrum), axis=0)
    freq_axis = np.linspace(header.fch1, header.fch1 + header.foff * header.nchans, header.nchans)
    plt.figure(figsize=(10, 6))
    plt.plot(freq_axis, total_spectrum, color='blue')
    plt.xlabel('Frequency (MHz)')
    plt.ylabel('Mean Power')
    plt.savefig('RFI_spectrum.png', dpi=300)
        
        

if __name__ == "__main__":
    main()