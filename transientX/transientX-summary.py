#!/home/ojohnson/djarin/bin/python
import argparse
import glob as glob
import os as os
import numpy as np 
import scipy.stats as stats
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import scienceplots 
import subprocess
plt.style.use(['science', 'no-latex'])

def fetch_args(): 
    '''
    Fetches the arguments from the command line 
    '''
    parser = argparse.ArgumentParser(description='Single Pulse Analysis for PRESTO on UWL Data')
    parser.add_argument('-i', '--input', type=str, help='Input directory', required=True)
    parser.add_argument('-t', '--threshold', type=float, help='Threshold for single pulse detection (default = 0)', required=False)
    parser.add_argument('-dmin', '--dmin', type=float, help='Minimum DM to plot (default = 0)', required=False)
    parser.add_argument('-dmax', '--dmax', type=float, help='Maximum DM to plot', required=False)
    parser.add_argument('-pdf', '--pdf', help='Save as pdf (default = False)', required=False, action='store_true')
    parser.add_argument('-convert', '--convert', help='Use imagik convert function for pdf (default = False)', required=False, action='store_true')
    parser.add_argument('-log', '--log', help='Log scale for time vs DM plot (default = False)', required=False, action='store_true')
    
    return parser.parse_args()

def read_transientx(cands_file):
    mjd, dm, width, snr, png, ifile = np.loadtxt(cands_file, usecols=(2, 3, 4, 5, 8, 10), unpack=True, dtype=str)
    mjd = mjd.astype(float); dm = dm.astype(float); width = width.astype(float); snr = snr.astype(float)
    time = mjd - mjd.min()
    
    return time, dm, width, snr, png, ifile

def marker_scaling(sig, threshold=10.0):
    """
    Scales the marker size based on S/N. Mimicing what is done by PRESTO in the same plot. 
    """
    min_size = 20; max_size = 1000 
        
    log_base = 30.0  # Higher values give a stronger effect
    marker_sizes = min_size + log_base * np.log1p(sig - threshold)
    
    return marker_sizes

def main(): 
    
    args = fetch_args()
    
    if args.threshold is None:
        args.threshold = 0.0
    if args.dmin is None:
        args.dmin = 0 
    
    # Read in the transientx file
    cands_files = glob.glob(f"{args.input}/*.cands")
    print('Number of candidates files:', len(cands_files))
    
    # Cat all the candidates
    time = []; dm = []; width = []; snr = []; png = []; ifile = []
    
    for cands_file in cands_files:
        time_, dm_, width_, snr_, png_, ifile_ = read_transientx(cands_file)
        
        time.extend(time_)
        dm.extend(dm_)
        width.extend(width_)
        snr.extend(snr_)
        png.extend(png_)
        ifile.extend(ifile_)
    
    print(f"Read in {len(time)} candidates from {cands_file}")
    
    # filter by threshold and dm 
    snr = np.array(snr); dm = np.array(dm); time = np.array(time); width = np.array(width); png = np.array(png); ifile = np.array(ifile)
    
    if args.threshold:
        mask = snr > args.threshold
        snr = snr[mask]
        time = time[mask]
        width = width[mask]
        dm = dm[mask]
        png = png[mask]
        ifile = ifile[mask]
    
    if args.dmin:
        mask = dm > args.dmin
        snr = snr[mask]
        time = time[mask]
        width = width[mask]
        dm = dm[mask]
        png = png[mask]
        ifile = ifile[mask]
        
        if args.dmax:
            mask = dm > args.dmax
            snr = snr[mask]
            time = time[mask]
            width = width[mask]
            dm = dm[mask]
            png = png[mask]
            ifile = ifile[mask]
    
    if len(dm) == 0:
        print('⚠️ No single pulses found in {} for current setup'.format(cands_file))
        return
    
    filename = ifile[0].split('.')[0]
    
    fig = plt.figure(figsize=(12, 8))
    gs = gridspec.GridSpec(2, 3, height_ratios=[1, 2])
    plt.suptitle('%s | DM $>$ %s | S/N  $>$ %s | $N_{pulse} =$ %s' % (filename, args.dmin, args.threshold, len(dm)), fontsize=16)

    # Top row (3 plots)
    ax1 = plt.subplot(gs[0, 0])
    ax2 = plt.subplot(gs[0, 1])
    ax3 = plt.subplot(gs[0, 2])

    # Bottom row (1 plot spanning 3 columns)
    ax4 = plt.subplot(gs[1, :])

    # Histogram of S/N
    ax1.hist(snr, bins=100, color='black', histtype='step')
    ax1.set_xlabel('S/N')
    ax1.set_ylabel('Pulses')
    ax1.set_xlim(snr.min(), snr.max())

    # Histogram of DM
    ax2.hist(dm, bins=60, color='black', histtype='step')
    ax2.set_xlabel('DM (pc cm$^{-3}$)')
    ax2.set_ylabel('Pulses')

    # DM vs. S/N scatter plot
    ax3.scatter(dm, snr, color='black', s=1)
    ax3.axhline(snr.mean(), color='red', linestyle='--')
    ax3.text(0.05, 0.95, 'Mean S/N: %.2f' % snr.mean(), transform=ax3.transAxes, verticalalignment='top')
    ax3.set_xlabel('DM (pc cm$^{-3}$)')
    ax3.set_ylabel('S/N')
    ax3.set_ylim(snr.min(), snr.max())
    
    # Time vs. DM scatter plot spanning full bottom row
    t_fact = 24*60*60 # Convert days to seconds
    time = time * t_fact
    marker_sizes = snr**2
    
    ax4.scatter(time, dm,  s = marker_sizes, edgecolor='black', facecolor='none', alpha=0.3)
    ax4.set_xlabel('Time (s)')
    ax4.set_ylabel('DM (pc cm$^{-3}$)')
    ax4.set_xlim(0, float(time.max()))
    
    if args.log:
        # ax2.set_xscale('log')
        # ax3.set_xscale('log')
        ax4.set_yscale('log')
    else:
        ax2.set_xlim(0, dm.max())
        # ax3.set_xlim(0, dm.max())
        ax4.set_ylim(0, dm.max())
    
    plt.tight_layout()
    output_file = os.path.join(args.input, f'{filename}_transx_t{args.threshold}_DM{args.dmin}.png')
    plt.savefig(output_file)
    print(f'Saved {output_file}')
    plt.close()
    
    # cd to input directory
    os.chdir(args.input)

    # Save pngs to a single pdf
    if args.pdf:
        # Sort files by SNR 
        snr_sort = np.argsort(snr)[::-1]
        png = png[snr_sort]
        png = [str(i) for i in png]
        png.insert(0, output_file)
    
        # use convert subprocess to convert png to pdf
        subprocess.run(['convert'] + png + [f'{filename}_transx_t{args.threshold}_DM{args.dmin}.pdf'])
        print(f'Saved {filename}_transx_t{args.threshold}_DM{args.dmin}.pdf')

if __name__ == "__main__":
    main()