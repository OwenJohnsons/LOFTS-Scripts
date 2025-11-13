#%%
'''
Code Purpose: Generate an HR diagram from a Gaia DR3 target CSV.
Author: Owen A. Johnson
Last Major Update: 11/04/2023
'''

import argparse
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
import matplotlib.colors
import scienceplots

plt.style.use(['science','ieee', 'no-latex'])  # - Plot Style 

# --- CLI argument parser ---
parser = argparse.ArgumentParser(
    description=(
        "Generate an HR diagram from a Gaia DR3 target CSV.\n\n"
        "The CSV must contain at least the following columns:\n"
        " - teff_gspphot: Effective temperature in Kelvin\n"
        " - bp_rp: BP–RP color index (magnitudes)\n"
        " - phot_g_mean_mag: G-band mean magnitude (magnitudes)\n"
        " - distance_gspphot: Distance in parsecs\n"
        " - phot_g_mean_flux: G-band flux (for additional filtering)\n"
    ),
    formatter_class=argparse.RawTextHelpFormatter
)
parser.add_argument(
    "csv_file",
    type=str,
    help="Path to the Gaia DR3 CSV file containing the required columns."
)
args = parser.parse_args()

# --- Color palette ---
color_pallette = ['#364F6B','#3FC1C9','#FC5185','white']
custom_cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", color_pallette)

# --- Load data ---
gaia = pd.read_csv(args.csv_file)
print('Number of Gaia targets in SETI Search:', len(gaia))
print(gaia.keys())

# --- Remove zero values ---
gaia = gaia[gaia['teff_gspphot'] != 0]
gaia = gaia[gaia['bp_rp'] != 0]

# --- Remove NaN values ---
gaia = gaia.dropna(subset=['bp_rp'])

print('Mean Distance:', np.round(gaia['distance_gspphot'].mean(), 3), 'pc')
print('Max Distance:', np.round(gaia['distance_gspphot'].max(), 3), 'pc')
print('Max Distance:', np.round(gaia['distance_gspphot'].max() * 3.26156, 3), 'ly')
print('Min Distance:', np.round(gaia['distance_gspphot'].mean() * 3.26156, 3), 'ly')

sf_prct_dist = gaia['distance_gspphot'].mean() + gaia['distance_gspphot'].std() 
print('Mean Distance + 1 std:', np.round(sf_prct_dist, 3) * 3.26156, 'ly')

def calculate_luminosity(absolute_magnitude):
    L_sun = 3.828e26  # Luminosity of the Sun in watts
    M_sun = 4.83      # Absolute magnitude of the Sun
    luminosity = 10**(0.4*(M_sun - absolute_magnitude))
    return luminosity / L_sun

#%%
print('Number of Gaia targets that have non-zero Teff values:', len(gaia))

bp_rp = np.array(gaia['bp_rp'])
gaia_surface_temp = np.array(gaia['teff_gspphot'])
Gmag = np.array(gaia['phot_g_mean_mag'])

print('Max Magnitude:', Gmag.max())
print('Min Magnitude:', Gmag.min())
print('Mean Magnitude:', Gmag.mean())
print('Number of Gaia targets that have non-zero Gmag values:', len(Gmag))

# --- Plotting ---
fig , ax = plt.subplots(figsize=(3, 9), rasterized=True)
h = ax.hist2d(bp_rp, Gmag, bins=400, cmin=2, norm=colors.PowerNorm(0.5), zorder=0.5, cmap=custom_cmap)

cbar_ax = fig.add_axes([0.92, 0.125, 0.04, 0.755])
cb = fig.colorbar(h[3], ax=ax, pad=0.02, cax=cbar_ax, cmap='magma')
ax.scatter(bp_rp, Gmag, alpha=0.5, s=0.1, color='k', zorder=0, facecolor='k')

ax.set_xlabel(r'$G_{BP} - G_{RP}$')
ax.set_ylabel(r'Magnitude $M_G$')
cb.set_label(r"$\mathrm{Stellar~Density}$")

# --- Spectral Type Percentages ---
def interval_percentage(arr, min_val, max_val): 
    mask = (arr >= min_val) & (arr <= max_val)
    return len(arr[mask]) / len(arr)

gaia_surface_temp = gaia_surface_temp[~np.isnan(gaia_surface_temp)]
gaia_surface_temp = gaia_surface_temp[gaia_surface_temp > 0]

per_O = interval_percentage(gaia_surface_temp, 28000, 50000)
per_B = interval_percentage(gaia_surface_temp, 10000, 28000)
per_A = interval_percentage(gaia_surface_temp, 7500, 10000)
per_F = interval_percentage(gaia_surface_temp, 6000, 7500)
per_G = interval_percentage(gaia_surface_temp, 5000, 6000)
per_K = interval_percentage(gaia_surface_temp, 3500, 5000)
per_M = interval_percentage(gaia_surface_temp, 2500, 3500)

percentage_values = np.array([per_O, per_B, per_A, per_F, per_G, per_K, per_M])
star_types = ['O', 'B', 'A', 'F', 'G', 'K', 'M']

print('Sum of percentages:', np.sum(percentage_values))
for i, val in enumerate(percentage_values): 
    print(f'Percentage of {star_types[i]} type stars: {np.round(val*100, 3)}%')
    string = f"{star_types[i]}: {np.round(val*100, 3)}$\\%$"
    ax.annotate(string, xy=(4.7, (5.3 + 0.25*i)), size='x-small', ha='left')

# --- Final formatting ---
ax.invert_yaxis()
ax.set_ylim(19, 5)
ax.set_xlim(-2, 7)

plt.tight_layout()
plt.savefig('HRD.pdf', dpi=300, bbox_inches='tight')
plt.show()
# %%
