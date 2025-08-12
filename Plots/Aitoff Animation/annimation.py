#%%

import numpy as np
import matplotlib.pyplot as plt
from astropy.coordinates import EarthLocation, AltAz, SkyCoord, Galactic
from astropy.time import Time
import astropy.units as u
from astroplan import Observer
import networkx as nx
from matplotlib.animation import FuncAnimation, PillowWriter
import scienceplots
plt.style.use(['science', 'ieee'])
color_pallette = ['#016f95', '#0098c0', '#28c062', '#f05039', '#bd2d1d']


# Define the observatory's location (latitude, longitude, elevation)
observatory_location = EarthLocation(lat=38.4317*u.deg, lon=-79.8174*u.deg, height=0*u.m)

# Create an observer object using the defined observatory location
observer = Observer(location=observatory_location)

# Generate time array for every Tuesday from 7 to 8 AM
start_time = Time('2023-01-01T07:00:00', scale='utc')
end_time = Time('2023-12-31T08:00:00', scale='utc')
time_array = start_time + np.arange(0, (end_time - start_time).to_value(u.day), 7) * u.day

# Lists to store Zenith RA, Dec, and time values
zenith_ra_values = []
zenith_dec_values = []
time_values = []

# Calculate Zenith RA, Dec, and time for each Tuesday morning
for observation_time in time_array:
    # Create a SkyCoord in AltAz frame for zenith position
    zenith_position_altaz = SkyCoord(alt=90*u.deg, az=0*u.deg, obstime=observation_time, frame='altaz', location=observatory_location)

    # Convert AltAz coordinates to RA and Dec coordinates
    zenith_position_radec = zenith_position_altaz.transform_to('icrs')
    
    zenith_ra_values.append(zenith_position_radec.ra.deg)
    zenith_dec_values.append(zenith_position_radec.dec.deg)
    time_values.append(observation_time.jd)

# Convert RA to radians for Aitoff projection
zenith_ra_radians = np.radians(np.array(zenith_ra_values))

# Create a SkyCoord in ICRS frame for Zenith positions
zenith_positions_icrs = SkyCoord(ra=zenith_ra_values*u.deg, dec=zenith_dec_values*u.deg, frame='icrs')

# Create a SkyCoord in Galactic frame for Zenith positions
zenith_positions_galactic = zenith_positions_icrs.transform_to('galactic')

# Create a 3D plot with RA, Dec, and Time
fig = plt.figure(figsize=(16,9))
ax3 = fig.add_subplot(2, 1, 2, projection='aitoff')
ax3.grid(True)
ax3.set_xlabel('Galactic Longitude (deg)')
ax3.set_ylabel('Galactic Latitude (deg)')
plt.axhspan(np.deg2rad(-5), np.deg2rad(5), alpha=0.2, color='grey', label = 'Galactic Plane')

weeks = np.arange(0, len(zenith_ra_values), 1)
skycoverage = np.pi*1.29**2*weeks
gaia_targets = np.loadtxt('indv_count.txt', skiprows=1)

def update(frame):
    ax3.clear()  # Clear the previous frame's scatter plot and annotation
    ax3.grid(True)
    ax3.set_xlabel('Galactic Longitude (deg)', fontsize=14)
    ax3.set_ylabel('Galactic Latitude (deg)', fontsize=14)
    plt.axhspan(np.deg2rad(-5), np.deg2rad(5), alpha=0.2, color='grey', label='Galactic Plane')

    ax3.scatter(zenith_positions_galactic.l.wrap_at(180*u.deg).rad[:frame], zenith_positions_galactic.b.rad[:frame], color='deepskyblue', s=10)
    # ax3.plot(zenith_positions_galactic.l.wrap_at(180*u.deg).rad[:frame], zenith_positions_galactic.b.rad[:frame], color='deepskyblue', lw=1)
    ax3.set_title(f"Week {frame}")
    
    # Add the annotation
    ax3.annotate(('Sky Coverage (deg$^2$): %s' % "{:.1f}".format(skycoverage[frame])), xy=(0.75, -0.05), xycoords='axes fraction', fontsize=8,
                 ha='left', va='center')
    ax3.annotate(('Gaia Targets ($n$): %s' % int(gaia_targets[frame])), xy=(0.75, 0), xycoords='axes fraction', fontsize=8,
                 ha='left', va='center')

    return ax3


animation = FuncAnimation(fig, update, frames=len(zenith_ra_values))
animation.save('skycoverage.gif', writer='imagemagick', fps=5)
plt.tight_layout()
plt.show()


# %%
