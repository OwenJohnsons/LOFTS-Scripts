import argparse 
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
import matplotlib.image as mpimg
from datetime import date
import smplotlib

def wrap_angle(deg_array):
    """Wrap angles to [-180, +180) degrees for Aitoff projection."""
    return np.remainder(deg_array + 180, 360) - 180

def get_args():
    parser = argparse.ArgumentParser(description="Merge two LOFTS Progress CSV files.")
    parser.add_argument("file1", type=str, help="Path to the first CSV file.")
    parser.add_argument("file2", type=str, help="Path to the second CSV file.")
    parser.add_argument("--publication", action="store_true", help="Generate publication-quality plots without annotations.", default=False)
    return parser.parse_args()

def main(): 
    args = get_args()
    
    df1 = pd.read_csv(args.file1)
    df2 = pd.read_csv(args.file2)
    
    merged_df = pd.concat([df1, df2], ignore_index=True)
    merged_df.to_csv("./master-csv/LOFTS-total-progress.csv", index=False)
    
    unique_df = merged_df.drop_duplicates(subset=['source_name'])
    
    IE_subset = merged_df[merged_df['station'] == 'IE']
    SE_subset = merged_df[merged_df['station'] == 'SE']

    SE_files = SE_subset['filename'].str.split('/').str[-1].tolist()
    IE_files = IE_subset['filename'].str.split('/').str[-1].tolist()
    
    print("============================")
    print("LOFTS Progress Report")
    print("============================")
    
    print(f'Total time on sky (hours): {unique_df["tobs_min"].sum() / 60:.2f}')
    print(f'Total file size (TB): {merged_df["size_gb"].sum() / 1024:.2f}')
    
    print("\n--- IE Observation Files ---")
    print(f"Total IE files: {len(IE_files)}")
    print(f"Number of 0000 files: {len([f for f in IE_files if f.endswith('0000.fil')])}")
    print(f"Number of 0001 files: {len([f for f in IE_files if f.endswith('0001.fil')])}")
    print(f"Number of 0002 files: {len([f for f in IE_files if f.endswith('0002.fil')])}")  
    
    print("\n--- SE Observation Files ---")
    print(f"Total SE files: {len(SE_files)}")
    print(f"Number of 0000 files: {len([f for f in SE_files if f.endswith('0000.fil')])}")
    print(f"Number of 0001 files: {len([f for f in SE_files if f.endswith('0001.fil')])}")
    print(f"Number of 0002 files: {len([f for f in SE_files if f.endswith('0002.fil')])}")
    
    print("\n--- Concidence Observation Files ---")
    matches = set(SE_files).intersection(set(IE_files))
    print(f"Number of matching files between SE and IE: {len(matches)}")
    print(f"Number of matching 0000 files between SE and IE: {len([f for f in matches if f.endswith('0000.fil')])}")
    print(f"Number of matching 0001 files between SE and IE: {len([f for f in matches if f.endswith('0001.fil')])}")
    print(f"Number of matching 0002 files between SE and IE: {len([f for f in matches if f.endswith('0002.fil')])}")
    
    # ---------------------------
    # Galactic Plane Plot
    # ---------------------------
    print("\nGenerating Plots...")
    logo_img = mpimg.imread('./breakthrough-listen.png')
    
    # Wrap longitudes
    l_plot = wrap_angle(unique_df['l_deg'])
    b_plot = unique_df['b_deg']
    ra_plot = wrap_angle(unique_df['ra_deg'])
    dec_plot = unique_df['dec_deg']
    uniqdf = unique_df[unique_df['filename'].str.contains('0000.fil')].reset_index(drop=True)

    sky_cov = len(uniqdf) * np.pi * 2.59**2   # deg^2
        
    
    fig = plt.figure(figsize=(11.69, 3), dpi=200)
    ax = fig.add_subplot(111, projection='aitoff')
    ax.grid(True)

    ax.plot(np.radians([-180, 180]), np.radians([5, 5]), color='black', linestyle='--', linewidth=0.5, label="Galactic Plane")
    ax.plot(np.radians([-180, 180]), np.radians([-5, -5]), color='black', linestyle='--', linewidth=0.5)
    ax.scatter(np.radians(l_plot), np.radians(b_plot), s=1, color='black')

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
    ax.scatter(np.radians(l_plot), np.radians(b_plot), s=1, color='black')
    ax.tick_params(labelsize=8)
    for label in ax.get_xticklabels():
        label.set_transform(label.get_transform() + mtransforms.ScaledTranslation(0, 5 / 72, fig.dpi_scale_trans))
    ax.legend(loc='upper right', fontsize=7)
    ax.set_xlabel("Galactic Longitude $(l)$ [deg]", fontsize=9, labelpad=10)
    ax.set_ylabel("Galactic Latitude $(b)$ [deg]", fontsize=9)

    # Equatorial
    ax = axes[1]
    ax.grid(True)
    ax.scatter(np.radians(ra_plot), np.radians(dec_plot), s=1, color='black')
    ax.tick_params(labelsize=8)
    ax.legend(loc='upper right', fontsize=7)
    ax.set_xlabel("Right Ascension [deg]", fontsize=9, labelpad=10)
    ax.set_ylabel("Declination [deg]", fontsize=9)

    today = date.today().isoformat()

    if not args.publication:
        fig.text(0.72, 0.6, "LOFTS Observing Progress", fontsize=10)
        fig.text(0.72, 0.57, f"Last Updated: {today}", fontsize=8)
        fig.text(0.72, 0.55, f"Total Unique Observations: {len(uniqdf)}", fontsize=8)
        fig.text(0.72, 0.53, f"Total Data Volume: {np.sum(merged_df['size_gb'])/1024:.1f} TB", fontsize=8)
        fig.text(0.72, 0.51, f"Total Observing Time: {np.sum(uniqdf['tobs_min'])/60:.1f} hours", fontsize=8)
        fig.text(0.72, 0.49, f"Total Sky Coverage: {sky_cov:.1f} deg$^2$", fontsize=8)

        logo_ax = fig.add_axes([0.72, 0.88, 0.15, 0.15]) 
        logo_ax.imshow(logo_img[::-1, :,], )
        logo_ax.axis("off")

    plt.tight_layout()
    plt.savefig("../plots/combined-aitoff.png", bbox_inches='tight')
    
if __name__ == "__main__":
    main()