from glob import glob
import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u
import your
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
import matplotlib.image as mpimg
from datetime import date
import smplotlib
import argparse

def get_args():
    parser = argparse.ArgumentParser(description="LOFTS Progress")
    parser.add_argument('-s', '--station', type=str, required=True, help='LOFAR station (IE or SE)')
    parser.add_argument('-p', '--plot', action='store_true', help='Generate plots')
    

    return parser.parse_args()

def wrap_angle(deg_array):
    """Wrap angles to [-180, +180) degrees for Aitoff projection."""
    return np.remainder(deg_array + 180, 360) - 180

args = get_args()
station = args.station # 'IE' or 'SE'
if station not in ['IE', 'SE']:
    raise ValueError("Station must be 'IE' or 'SE'")

filterbanks = glob('/datax2/projects/LOFTS/*/*/LOFTS*.fil')
logo_img = mpimg.imread('./breakthrough-listen.png')

source_name, filename = [], []
ra_deg, dec_deg = [], []
l_deg, b_deg = [], []
time_ut, time_mjd = [], []
size_gb, f_res = [], []
tobs, tsamp_arr = [], []
npols = []

for fil in filterbanks:
    hdr = your.Your(fil).your_header

    source_name.append(hdr.source_name)
    filename.append(hdr.filename)
    
    nchan = hdr.native_nchans
    nspec = hdr.native_nspectra
    bits = hdr.native_nbits
    npols.append(hdr.npol)

    tsamp = hdr.tsamp
    tsamp_arr.append(tsamp)
    tobs.append((nspec * tsamp) / 60)  # minutes
    f_res.append(np.round(hdr.foff * 1e3, 5))  # kHz

    size_bits = nchan * nspec * (bits / 8)
    size_gb.append(np.round(size_bits / 1024**3, 2))

    # Coord stuff
    ra = hdr.ra_deg
    dec = hdr.dec_deg

    ra_deg.append(ra)
    dec_deg.append(dec)

    time_ut.append(hdr.tstart_utc)
    time_mjd.append(hdr.tstart)

    coord = SkyCoord(ra=ra*u.deg, dec=dec*u.deg, frame='icrs')
    gal = coord.galactic
    l_deg.append(gal.l.deg)
    b_deg.append(gal.b.deg)

# ---------------------------
# Build dataframe
# ---------------------------
data = {
    'source_name': source_name,
    'filename': filename,
    'ra_deg': ra_deg,
    'dec_deg': dec_deg,
    'l_deg': l_deg,
    'b_deg': b_deg,
    'time_utc': time_ut,
    'time_mjd': time_mjd,
    'size_gb': size_gb,
    'fres_khz': f_res,
    'tsamp': tsamp_arr,
    'tobs_min': tobs,
    'npol': npols
}

df = pd.DataFrame(data)
df.to_csv('LOFTS-observations-Progress-%s-%s.csv' % (date.today().isoformat(), station), index=False)
print('Number of files:', len(df))

uniqdf = df[df['filename'].str.contains('0000.fil')].reset_index(drop=True)
print('Number of unique observations:', len(uniqdf))

sky_cov = len(uniqdf) * np.pi * 2.59**2   # deg^2

# Wrap longitudes
l_plot = wrap_angle(uniqdf['l_deg'])
b_plot = uniqdf['b_deg']
ra_plot = wrap_angle(uniqdf['ra_deg'])
dec_plot = uniqdf['dec_deg']

if not args.plot:
    exit()
# ---------------------------
# Galactic Plane Plot
# ---------------------------
fig = plt.figure(figsize=(11.69, 3), dpi=200)
ax = fig.add_subplot(111, projection='aitoff')
ax.grid(True)

ax.plot(np.radians([-180, 180]), np.radians([5, 5]), color='black', linestyle='--', linewidth=0.5, label="Galactic Plane")
ax.plot(np.radians([-180, 180]), np.radians([-5, -5]), color='black', linestyle='--', linewidth=0.5)
ax.scatter(np.radians(l_plot), np.radians(b_plot), s=1)

ax.tick_params(labelsize=8)
for label in ax.get_xticklabels():
    label.set_transform(label.get_transform() + mtransforms.ScaledTranslation(0, 5 / 72, fig.dpi_scale_trans))

plt.legend(loc='upper right', fontsize=7)
plt.xlabel("Galactic Longitude $(l)$ [deg]", fontsize=9, labelpad=10)
plt.ylabel("Galactic Latitude $(b)$ [deg]", fontsize=9)
plt.savefig("galactic-aitoff.png", bbox_inches='tight')

# ---------------------------
# Sky (RA/Dec) Plot
# ---------------------------
fig = plt.figure(figsize=(11.69, 3), dpi=200)
ax = fig.add_subplot(111, projection='aitoff')
ax.grid(True)

ax.scatter(np.radians(ra_plot), np.radians(dec_plot), s=1)
ax.tick_params(labelsize=8)
plt.xlabel("Right Ascension [deg]", fontsize=9, labelpad=10)
plt.ylabel("Declination [deg]", fontsize=9)
plt.savefig("sky-aitoff.png", bbox_inches='tight')


# ---------------------------
# Combined Plot (Galactic + Equatorial)
# ---------------------------
fig, axes = plt.subplots(
    nrows=2,
    figsize=(11.69, 6),
    dpi=200,
    subplot_kw={'projection': 'aitoff'}
)

# Galactic
ax = axes[0]
ax.grid(True)
ax.plot(np.radians([-180, 180]), np.radians([5, 5]), color='black', linestyle='--', linewidth=0.5, label="Galactic Plane")
ax.plot(np.radians([-180, 180]), np.radians([-5, -5]), color='black', linestyle='--', linewidth=0.5)
ax.scatter(np.radians(l_plot), np.radians(b_plot), s=1)
ax.tick_params(labelsize=8)
for label in ax.get_xticklabels():
    label.set_transform(label.get_transform() + mtransforms.ScaledTranslation(0, 5 / 72, fig.dpi_scale_trans))
ax.legend(loc='upper right', fontsize=7)
ax.set_xlabel("Galactic Longitude $(l)$ [deg]", fontsize=9, labelpad=10)
ax.set_ylabel("Galactic Latitude $(b)$ [deg]", fontsize=9)

# Equatorial
ax = axes[1]
ax.grid(True)
ax.scatter(np.radians(ra_plot), np.radians(dec_plot), s=1)
ax.tick_params(labelsize=8)
ax.legend(loc='upper right', fontsize=7)
ax.set_xlabel("Right Ascension [deg]", fontsize=9, labelpad=10)
ax.set_ylabel("Declination [deg]", fontsize=9)

today = date.today().isoformat()
fig.text(0.72, 0.6, "LOFTS Observing Progress", fontsize=10)
fig.text(0.72, 0.57, f"Last Updated: {today}", fontsize=8)
fig.text(0.72, 0.55, f"Total Unique Observations: {len(uniqdf)}", fontsize=8)
fig.text(0.72, 0.53, f"Total Data Volume: {np.sum(df['size_gb']):.1f} GB", fontsize=8)
fig.text(0.72, 0.51, f"Total Observing Time: {np.sum(uniqdf['tobs_min'])/60:.1f} hours", fontsize=8)
fig.text(0.72, 0.49, f"Total Sky Coverage: {sky_cov:.1f} deg$^2$", fontsize=8)

logo_ax = fig.add_axes([0.72, 0.88, 0.15, 0.15]) 
logo_ax.imshow(logo_img[::-1, :,], )
logo_ax.axis("off")

plt.tight_layout()
plt.savefig("../plots/combined-aitoff.png", bbox_inches='tight')