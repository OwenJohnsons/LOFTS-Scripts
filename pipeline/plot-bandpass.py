import argparse
import os
import your
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.ticker import FixedLocator
import scienceplots; plt.style.use(['science','ieee', 'no-latex'])
from tqdm import tqdm

def get_args():
    # --- Parser ---
    parser = argparse.ArgumentParser(description='Dynamic Spectra Plotter for LOFTS data.')
    parser.add_argument('-f', '--fil', type=str, help='Path of the filterbank file.', required = True)
    parser.add_argument('-s', '--station', type=str, help='Station where observation was taken.', required = True)
    return parser.parse_args()

def obs_slice(hdr, len):
    # depending on the type of observation, taking a slice of the data to see what the data looks like.
    nsamples = hdr.native_nspectra

    ctr_sample = int(nsamples/2)

    if len > nsamples:
        print(f"Requested length {len} exceeds available samples {nsamples}. Adjusting to maximum available samples.")
        return (0, nsamples)

    return (ctr_sample - len/2), (len)

def set_color(station):
    if station == 'IE':
        return 'Greens'
    elif station == 'SE':
        return 'Blues'
    else:
        return 'RdPu'

def get_metadata(hdr, station):

    trgt = hdr.basename.split('.')[0]
    strt_date = hdr.tstart_utc

    metadata = f"Station: {station}\n"
    # metadata += f"Path: {hdr.filename}\n"
    metadata += f"Target: {trgt}\n"
    metadata += f"Start Date: {strt_date}\n"
    metadata += f"Total Bandwidth (MHz): {hdr.nchans * abs(hdr.foff)}\n"
    metadata += f"Sample Rate (s): {hdr.tsamp}\n"
    metadata += f"Number of Channels: {hdr.nchans}\n"
    metadata += f"Number of Samples: {hdr.native_nspectra}\n"
    metadata += f"Channel Width (MHz): {abs(hdr.foff)}\n"
    metadata += f"Observation Length (mins): {(hdr.native_nspectra * hdr.tsamp)/60:.1f}\n"
    metadata += f"$t_0$ (s): {hdr.native_nspectra/2 * hdr.tsamp:.1f}\n"

    return metadata

def set_xticks(hdr, data_shape, nticks=8):
    top_freq = hdr.fch1
    bottom_freq = hdr.fch1 + (hdr.nchans - 1) * hdr.foff
    tick_positions = np.linspace(0, data_shape[1] - 1, nticks)
    xtick_vals = np.linspace(top_freq, bottom_freq, nticks)

    return xtick_vals, tick_positions

def set_yticks(hdr, data_shape, nend, nticks=8):
    duration = nend * hdr.tsamp
    ytick_pos = np.linspace(0, data_shape[0] - 1, nticks)
    ytick_vals = np.linspace(0, duration, nticks)

    return ytick_pos, ytick_vals

def plot_0000(fil_obj, hdr, save_path, station='N/A'):
    nstrt, nend = obs_slice(hdr, 16)
    fil_data = fil_obj.get_data(nstart=nstrt, nsamp=nend)

    print(fil_data.shape)
    spectrum = np.mean(fil_data, axis=0)

    stix_len = 9 # Number of frequency slices
    freq_slice = fil_data.shape[1] // stix_len

    # --- Plotting ---
    fig = plt.figure(figsize=(10, 8))
    gs = gridspec.GridSpec(4, 3, figure=fig)

    ax0 = plt.subplot(gs[0, :])
    ax0.plot(spectrum, color='k', lw=1)
    ax0.set_yscale('log')
    # ax0.set_xlabel("Frequency [MHz]")
    ax0.set_ylabel("Power [Arb.]")

    xtick_vals, tick_positions = set_xticks(hdr, fil_data.shape)
    tick_labels = [str(int(round(val))) for val in xtick_vals]
    ax0.set_xticks(tick_positions)
    ax0.set_xticklabels(tick_labels)

    axes = [plt.subplot(gs[(i // 3) + 1, i % 3]) for i in range(stix_len)]

    for i, ax in tqdm(enumerate(axes), total=len(axes), desc='Plotting Frequency Slices'):
        strt_idx = i * freq_slice
        end_idx = strt_idx + freq_slice
        data_slice = fil_data[:, strt_idx:end_idx]
        ax.imshow(data_slice, aspect='auto', cmap=set_color(station), origin='lower',
                  vmin=np.percentile(data_slice, 5), vmax=np.percentile(data_slice, 95))

        top_freq = hdr.fch1 + strt_idx * hdr.foff
        bottom_freq = hdr.fch1 + (end_idx - 1) * hdr.foff

        xtick_vals = np.linspace(top_freq, bottom_freq, 5)
        tick_positions = np.linspace(0, data_slice.shape[1] - 1, 5)

        ax.set_xticks(tick_positions)
        ax.set_xticklabels([f"{val:.1f}" for val in xtick_vals])

        if i > 5:
            ax.set_xlabel("Frequency [MHz]")

        if i % 3 == 0:
            ytick_pos, ytick_vals = set_yticks(hdr, fil_data.shape, nend, nticks=7)
            ax.set_yticks(ytick_pos[1:-1])
            ax.set_yticklabels([f"{val:.1f}" for val in ytick_vals[1:-1]])
            ax.set_ylabel("Time [s]")
        else:
            ax.set_yticks([])


    # --- Metadata ---
    metadata = get_metadata(hdr, station)
    ax0.text(0.5, 1.05, metadata, transform=ax0.transAxes, ha='left', va='bottom')

    # --- Save ---
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Saved plot to {save_path}")

def plot_0001(fil_obj, hdr, save_path, station='N/A'):

    nstrt, nend = obs_slice(hdr, 1000)
    fil_data = fil_obj.get_data(nstart=nstrt, nsamp=nend)
    print(fil_data.shape)

    spectrum = np.mean(fil_data, axis=0)
    print(spectrum.shape)

    # --- Plotting ---
    fig = plt.figure(figsize=(5, 4))

    gs = gridspec.GridSpec(2, 1, height_ratios=[1, 3], hspace=0)

    ax0 = plt.subplot(gs[0])
    ax1 = plt.subplot(gs[1], sharex=ax0)
    ax0.plot(spectrum, color='k', lw=1)
    ax0.set_yscale('log')
    ax0.tick_params(labelbottom=False)

    imshow_col = set_color(station)
    vmin, vmax = np.percentile(fil_data, [5, 95])
    ax1.imshow(fil_data, aspect='auto', cmap=imshow_col, origin='lower', vmin=vmin, vmax=vmax)

    xtick_vals, tick_positions = set_xticks(hdr, fil_data.shape)
    tick_labels = [str(int(round(val))) for val in xtick_vals]
    ax1.set_xticks(tick_positions); ax1.set_xticklabels(tick_labels)
    ax1.set_xlabel('Frequency [MHz]')

    ytick_pos, ytick_vals = set_yticks(hdr, fil_data.shape, nend)
    ax1.set_yticks(ytick_pos)
    ax1.set_yticklabels([f"{val:.1f}" for val in ytick_vals])
    ax1.set_ylabel('Time [s]')

    # --- Metadata ---
    metadata = get_metadata(hdr, station)
    ax0.text(0.5, 1.05, metadata, transform=ax0.transAxes, ha='left', va='bottom')

    # --- Save ---
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Saved plot to {save_path}")

def plot_0002(fil_obj, hdr, save_path, station='N/A'):

    nstrt, nend = obs_slice(hdr, 256)
    fil_data = fil_obj.get_data(nstart=nstrt, nsamp=nend, npoln=4)
    print(fil_data.shape)

    spec_I = np.mean(fil_data[0], axis=0)
    spec_Q = np.mean(fil_data[1], axis=0)
    spec_U = np.mean(fil_data[2], axis=0)
    spec_V = np.mean(fil_data[3], axis=0)

    # --- Plotting ---
    fig = plt.figure(figsize=(5, 8))

    gs = gridspec.GridSpec(5, 1, height_ratios=[2, 3, 3, 3, 3], hspace=0)

    ax0 = plt.subplot(gs[0])
    ax1 = plt.subplot(gs[1], sharex=ax0)
    ax2 = plt.subplot(gs[2], sharex=ax0)
    ax3 = plt.subplot(gs[3], sharex=ax0)
    ax4 = plt.subplot(gs[4], sharex=ax0)

    # Plotting Stokes Spectra
    ax0.plot(spec_I, color='k', lw=1, label ='Stokes I', alpha = 0.3, linestyle='-')
    ax0.plot(spec_Q, color='b', lw=1, label ='Stokes Q', alpha = 0.3, linestyle='-')
    ax0.plot(spec_U, color='r', lw=1, label ='Stokes U', alpha = 0.3, linestyle='-')
    ax0.plot(spec_V, color='g', lw=1, label ='Stokes V', alpha = 0.3, linestyle='-')
    ax0.set_yscale('log')
    ax0.legend(loc='upper right', fontsize=4)
    ax0.tick_params(labelbottom=False)

    imshow_col = set_color(station)

    # --- Dynamic Spectra : Stokes I ---
    stokesI = fil_data[:,0,:]
    vmin, vmax = np.percentile(stokesI[0], [5, 95])
    ax1.imshow(stokesI, aspect='auto', cmap=imshow_col, origin='lower', vmin=vmin, vmax=vmax)

    ytick_pos, ytick_vals = set_yticks(hdr, fil_data.shape, nend, nticks=7)
    ax1.set_yticks(ytick_pos[1:-1])
    ax1.set_yticklabels([f"{val:.1f}" for val in ytick_vals[1:-1]])
    ax1.set_ylabel('Time [s]')
    ax1.tick_params(labelbottom=False)

    # --- Dynamic Spectra : Stokes Q ---
    stokesQ = fil_data[:,1,:]
    vmin, vmax = np.percentile(stokesQ[0], [5, 95])
    ax2.imshow(stokesQ, aspect='auto', cmap=imshow_col, origin='lower', vmin=vmin, vmax=vmax)

    ytick_pos, ytick_vals = set_yticks(hdr, fil_data.shape, nend, nticks=7)
    ax2.set_yticks(ytick_pos[1:-1])
    ax2.set_yticklabels([f"{val:.1f}" for val in ytick_vals[1:-1]])
    ax2.set_ylabel('Time [s]')
    ax2.tick_params(labelbottom=False)

    # --- Dynamic Spectra : Stokes U ---
    stokesU = fil_data[:,2,:]
    vmin, vmax = np.percentile(stokesU[0], [5, 95])
    ax3.imshow(stokesU, aspect='auto', cmap=imshow_col, origin='lower', vmin=vmin, vmax=vmax)

    ytick_pos, ytick_vals = set_yticks(hdr, fil_data.shape, nend, nticks=7)
    ax3.set_yticks(ytick_pos[1:-1])
    ax3.set_yticklabels([f"{val:.1f}" for val in ytick_vals[1:-1]])
    ax3.set_ylabel('Time [s]')
    ax3.tick_params(labelbottom=False)

    # --- Dynamic Spectra : Stokes V ---
    stokesV = fil_data[:,3,:]
    vmin, vmax = np.percentile(stokesV[0], [5, 95])
    ax4.imshow(stokesV, aspect='auto', cmap=imshow_col, origin='lower', vmin=vmin, vmax=vmax)

    ax4.set_yticks(ytick_pos[1:-1])
    ax4.set_yticklabels([f"{val:.1f}" for val in ytick_vals[1:-1]])
    ax4.set_ylabel('Time [s]')
    ax4.tick_params(labelbottom=False)

    xtick_vals, _ = set_xticks(hdr, fil_data.shape)

    n_channels = fil_data.shape[-1]
    tick_positions_scaled = [
        i * (n_channels - 1) / (len(xtick_vals) - 1)
        for i in range(len(xtick_vals))
    ]

    ax1.xaxis.set_major_locator(FixedLocator(tick_positions_scaled))
    ax1.set_xticklabels([str(int(round(val))) for val in xtick_vals])
    ax4.set_xlabel('Frequency [MHz]')

    # --- Metadata ---
    metadata = get_metadata(hdr, station)
    ax0.text(0.5, 1.05, metadata, transform=ax0.transAxes, ha='left', va='bottom')

    # --- Save ---
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Saved plot to {save_path}")

def main():
    args = get_args()

    # For interactive debugging
    # args = {'fil': './B1508+55/B1508+55.rawspec.0000.fil',
    #         'station': 'IE'}

    # --- Loading filterbank data ---
    fil_path = args.fil
    station = args.station
    # fil_path = args['fil']
    # station = args['station']
    save_plt = fil_path.replace('.fil', '.png')

    header = your.Your(fil_path).your_header
    fil_obj = your.Your(fil_path)

    fil_basename = os.path.basename(fil_path)
    print('Plotting %s' % fil_basename)

    if '0000.fil' in fil_basename:
        print('Narrowband filterbank ingested.')
        plot_0000(fil_obj, header, save_plt, station=station)

    elif '0001.fil' in fil_basename:
        print('Fast transient filterbank ingested.')
        plot_0001(fil_obj, header, save_plt, station=station)

    elif '0002.fil' in fil_basename:
        print('Full stokes mid resoltution filterbank ingested.')
        plot_0002(fil_obj, header, save_plt, station=station)


    else:
        raise ValueError("No BL data product detected.")


if __name__ == "__main__":
    main()
