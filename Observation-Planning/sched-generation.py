import os
from astropy.time import Time, TimeDelta
from astropy.coordinates import EarthLocation
import astropy.units as u
import pandas as pd
import argparse

def zenith_ra_dec_formatted(latitude, longitude, start_time_utc, interval_minutes=80, total_hours=24, freq_range="110e6:190e6", duration="80m", start_lofts_number=1):
    # Create the observer's location on Earth
    location = EarthLocation(lat=latitude*u.deg, lon=longitude*u.deg)

    # Convert start time to astropy Time object
    start_time = Time(start_time_utc)

    # Total time available in minutes (to calculate non-overlapping intervals)
    total_minutes = total_hours * 60
    current_time = start_time
    results = []

    # Create a 'sched' subfolder if it doesn't exist
    if not os.path.exists("sched"):
        os.makedirs("sched")

    # Insert pulsar observation every 12 hours, and regular zenith observations with a 1-minute gap
    next_pulsar_time = start_time + TimeDelta(12 * 3600, format='sec')  # Every 12 hours
    lofts_count = start_lofts_number  # Start from the specified LOFTS number

    while current_time < start_time + TimeDelta(total_minutes * 60, format='sec'):
        # Check if it's time for the pulsar observation, and it should only happen after the LOFTS observation is finished
        if current_time >= next_pulsar_time:
            pulsar_start_time = current_time + TimeDelta(60, format='sec')  # 1-minute gap after LOFTS observation
            pulsar_end_time = pulsar_start_time + TimeDelta(5 * 60, format='sec')  # 5 minute duration

            results.append({
                'Name': "PULSAR_OBS",
                'Time': f"{pulsar_start_time.datetime.strftime('%H:%M')} - {pulsar_end_time.datetime.strftime('%H:%M')}",
                'Time_ISO': f"{pulsar_start_time.iso} - {pulsar_end_time.iso}",
                'RA': "RA_PLACEHOLDER",
                'DEC': "DEC_PLACEHOLDER",
                'freqrng': freq_range,
                'dur': "5m"
            })

            # Update the current time to be 1 minute after the pulsar observation
            current_time = pulsar_end_time + TimeDelta(60, format='sec')
            next_pulsar_time += TimeDelta(12 * 3600, format='sec')  # Set the next pulsar observation time

        else:
            # Zenith observation: 80 minutes with a 1-minute gap afterward
            obs_end_time = current_time + TimeDelta(interval_minutes * 60, format='sec')
            lofts_name = f"LOFTS{lofts_count:04d}"

            # Get the RA in radians
            ra_in_radians = current_time.sidereal_time('mean', longitude).to(u.rad).value
            # Latitude (Dec) in radians
            dec_in_radians = latitude * (u.deg).to(u.rad)

            results.append({
                'Name': lofts_name,
                'Time': f"{current_time.datetime.strftime('%H:%M')} - {obs_end_time.datetime.strftime('%H:%M')}",
                'Time_ISO': f"{current_time.iso} - {obs_end_time.iso}",
                'RA': ra_in_radians,
                'DEC': dec_in_radians,
                'freqrng': freq_range,
                'dur': duration
            })

            # Increment the LOFTS number for the next observation
            lofts_count += 1

            # Update the current time to be 1 minute after the zenith observation
            current_time = obs_end_time + TimeDelta(60, format='sec')

    # Convert results to a DataFrame for better readability
    df = pd.DataFrame(results)

    # Extract date for the filenames
    date_str = start_time.datetime.strftime("%d-%m-%Y")

    ilisa_file = os.path.join("sched", f"sched-iLiSA-{date_str}.txt")
    realta_file = os.path.join("sched", f"sched-REALTA-{date_str}.txt")

    with open(ilisa_file, "w") as f:
        f.write("Name Time RA DEC freqrng dur\n")
        for index, row in df.iterrows():
            f.write(f"{row['Name']} {row['Time']} {row['RA']} {row['DEC']} {row['freqrng']} {row['dur']}\n")

    with open(realta_file, "w") as f:
        f.write("#LOFTS Survey, PI: Owen Johnson (ojohnson@tcd.ie), Date: %s\n" % date_str)
        for index, row in df.iterrows():
            f.write(f"{row['Time_ISO']} : {row['Name']} [{row['RA']}, {row['DEC']}, 'J2000']\n")

    # Print success message
    print(f"Files saved as:\n- {ilisa_file}\n- {realta_file}")

    return df


def main(): 
    parser = argparse.ArgumentParser(description='Generate LOFTS scheduling files')
    parser.add_argument('-date', type=str, help='Start date of the observation in the format YYYY-MM-DD HH:MM:SS', required=False, default=Time.now().iso)
    parser.add_argument('-n', type=int, help='Starting number for LOFTS targets', required=False, default=1)

    args = parser.parse_args()

    latitude_se =  57.39885  # Latitude of SE607
    longitude_se = 11.93029  # Longitude of the SE607
    latitude_irl =  53.349805  # Latitude of Ireland
    longitude_irl = -7  # Longitude of Ireland
    
    half_latitude = (latitude_se + latitude_irl) / 2
    half_longitude = (longitude_se + longitude_irl) / 2

    print(f"Half Latitude: {half_latitude}, Half Longitude: {half_longitude}")

    start_time_utc = args.date  # UTC start time of the observation

    zenith_ra_dec_formatted(half_latitude, half_longitude, start_time_utc, start_lofts_number=args.n)


if __name__ == "__main__":
    main()
