from glob import glob
import numpy as np
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from astropy.time import Time
import astropy.units as u
import your
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
# import scienceplots; plt.style.use(['science', 'no-latex'])
import smplotlib

filterbanks = glob('/datax2/projects/LOFTS/*/*/LOFTS*.fil')

source_name, filename = [], []
ra_deg, dec_deg = [], []
l_deg, b_deg = [], []
time_ut, time_mjd = [], []
size_gb, f_res = [], []
tobs, tsamp_arr = [], []
npols = []

for fil in filterbanks:
    hdr = your.Your(fil).your_header

     # Generic info
    source_name.append(hdr.source_name)
    filename.append(hdr.filename)

    # resolution and size calcs
    nchan = hdr.native_nchans
    nspec = hdr.native_nspectra
    bits = hdr.native_nbits
    npols.append(hdr.npol)

    tsamp = hdr.tsamp; tsamp_arr.append(tsamp)
    tobs.append((nspec*tsamp)/60)
    f_res.append(np.round(hdr.foff*1e3, 5)) # KHz

    size_bits = nchan*nspec*(bits/8)
    size_gb.append(np.round(size_bits/1024**3, 2))

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
print(df.head())


# --- Summary Plots ---
df.drop_duplicates(subset=['source_name'])
l_deg = df['l_deg']; b_deg = df['b_deg']
ra_deg = df['ra_deg']; dec_deg = df['dec_deg']

# --- Galactic Plane Plot ---
fig = plt.figure(figsize=(11.69, 3), dpi=200)
ax = fig.add_subplot(111, projection='aitoff')
ax.grid(True)

# galactic plane with dashed line, +5 to -5 degrees
ax.plot(np.radians([0, 720]), np.radians([5, 5]), color='black', linestyle='--', linewidth=0.5, label="Galactic Plane")
ax.plot(np.radians([0, 720]), np.radians([-5, -5]), color='black', linestyle='--', linewidth=0.5)

ax.scatter(np.radians(l_deg), np.radians(b_deg), s=1)

ax.tick_params(labelsize=8)
for label in ax.get_xticklabels():
    label.set_transform(label.get_transform() + mtransforms.ScaledTranslation(0, 5 / 72, fig.dpi_scale_trans))

plt.legend(loc='upper right', fontsize=7)
plt.xlabel("Galactic Longitude $(l)$ [deg]", fontsize=9, labelpad=10)
plt.ylabel("Galactic Latitude $(b)$ [deg]", fontsize=9)
plt.savefig("galactic-aitoff.png", bbox_inches='tight')
plt.show()


# --- Sky Plot ---
fig = plt.figure(figsize=(11.69, 3), dpi=200)
ax = fig.add_subplot(111, projection='aitoff')
ax.grid(True)

ax.scatter(np.radians(ra_deg), np.radians(dec_deg), s = 1)
ax.tick_params(labelsize=8)

plt.legend(loc='upper right', fontsize=7)
plt.xlabel("Right Ascension [deg]", fontsize=9, labelpad=10)
plt.ylabel("Declination [deg]", fontsize=9)
plt.savefig("sky-aitoff.png", bbox_inches='tight')

# --- Combined Plot ---
fig, axes = plt.subplots(
    nrows=2,
    figsize=(11.69, 6),  # Adjusted height for 2 stacked plots
    dpi=200,
    subplot_kw={'projection': 'aitoff'}
)

ax = axes[0]
ax.grid(True)
ax.plot(np.radians([0, 720]), np.radians([5, 5]), color='black', linestyle='--', linewidth=0.5, label="Galactic Plane")
ax.plot(np.radians([0, 720]), np.radians([-5, -5]), color='black', linestyle='--', linewidth=0.5)
ax.scatter(np.radians(l_deg), np.radians(b_deg), s=1)

ax.tick_params(labelsize=8)
for label in ax.get_xticklabels():
    label.set_transform(label.get_transform() + mtransforms.ScaledTranslation(0, 5 / 72, fig.dpi_scale_trans))

ax.legend(loc='upper right', fontsize=7)
ax.set_xlabel("Galactic Longitude $(l)$ [deg]", fontsize=9, labelpad=10)
ax.set_ylabel("Galactic Latitude $(b)$ [deg]", fontsize=9)

ax = axes[1]
ax.grid(True)
ax.scatter(np.radians(ra_deg), np.radians(dec_deg), s=1)
ax.tick_params(labelsize=8)
ax.legend(loc='upper right', fontsize=7)
ax.set_xlabel("Right Ascension [deg]", fontsize=9, labelpad=10)
ax.set_ylabel("Declination [deg]", fontsize=9)

# --- Text ---
from datetime import date; today = date.today().isoformat()


fig.text(0.72, 0.8, "LOFTS Observing Progress", fontsize=10)
fig.text(0.72, 0.77, "Last Updated: %s" % today, fontsize=8)
fig.text(0.72, 0.75, "Total Observations: %s" % len(df), fontsize=8)

plt.tight_layout()
plt.savefig("combined-aitoff.png", bbox_inches='tight')
plt.show()
