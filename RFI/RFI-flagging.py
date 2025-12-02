import numpy as np
import glob
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pandas as pd
from matplotlib.widgets import Button


def comp_feats(log_ratio):
    """
    Compute per-channel features from log-ratio time-series.
    Returns feature matrix of shape (n_chan, n_features).
    """
    mean_lr = np.mean(log_ratio, axis=0)
    std_lr  = np.std(log_ratio, axis=0)
    p5      = np.percentile(log_ratio, 5, axis=0)
    p95     = np.percentile(log_ratio, 95, axis=0)
    p50     = np.percentile(log_ratio, 50, axis=0)

    # fraction of times channel is hot compared to its own median
    hot = (log_ratio > (p50 + 0.1)[None, :])
    frac_hot = hot.mean(axis=0)

    # ---------- local feature engineering ----------
    I = np.mean(log_ratio, axis=0)
    win = 11
    pad = win // 2
    Ipad = np.pad(I, pad, mode='reflect')

    kernel = np.ones(win) / win
    local_mean = np.convolve(Ipad, kernel, mode='valid')
    local_ratio = I / (local_mean + 1e-8)

    slope = np.gradient(I)
    curvature = np.gradient(slope)

    Iwin = np.lib.stride_tricks.sliding_window_view(I, win)
    local_var = Iwin.var(axis=1)
    local_mad = np.median(
        np.abs(Iwin - np.median(Iwin, axis=1)[:, None]),
        axis=1
    )

    local_var = np.pad(local_var, pad_width=(pad, pad), mode='edge')
    local_mad = np.pad(local_mad, pad_width=(pad, pad), mode='edge')

    features = np.vstack([
        mean_lr,
        std_lr,
        p95 - p5,
        frac_hot,
        local_ratio,
        slope,
        curvature,
        local_var,
        local_mad,
    ]).T

    return features


def iso_forest(features, contamination=0.03):
    """
    Fit IsolationForest and return boolean mask of detected outliers.
    """
    scaler = StandardScaler()
    X = scaler.fit_transform(features)

    forest = IsolationForest(
        n_estimators=400,
        contamination=contamination,
        random_state=42,
        n_jobs=-1
    )
    labels = forest.fit_predict(X)
    rfi_mask = (labels == -1)
    return rfi_mask, forest.score_samples(X)


def compress_ranges(indices):
    """Convert sorted array of indices into compact range format."""
    indices = np.asarray(indices, dtype=int)
    if indices.size == 0:
        return ""

    indices = np.sort(indices)
    ranges = []
    start = prev = indices[0]

    for x in indices[1:]:
        if x == prev + 1:
            prev = x
            continue
        if start == prev:
            ranges.append(f"{start}")
        else:
            ranges.append(f"{start}-{prev}")
        start = prev = x

    if start == prev:
        ranges.append(f"{start}")
    else:
        ranges.append(f"{start}-{prev}")

    return ",".join(ranges)


def channels_to_freq_ranges(indices, f_start, df):
    """Convert channel index ranges into frequency MHz ranges."""
    indices = np.asarray(indices, dtype=int)
    if indices.size == 0:
        return ""

    indices = np.sort(indices)
    ranges = []
    start = prev = indices[0]

    for x in indices[1:]:
        if x == prev + 1:
            prev = x
            continue

        f1 = f_start + start * df
        f2 = f_start + prev * df
        if start == prev:
            ranges.append(f"{f1:.6f}")
        else:
            ranges.append(f"{f1:.6f}-{f2:.6f}")
        start = prev = x

    f1 = f_start + start * df
    f2 = f_start + prev * df
    if start == prev:
        ranges.append(f"{f1:.6f}")
    else:
        ranges.append(f"{f1:.6f}-{f2:.6f}")

    return ",".join(ranges)


def interactive_plot(freq, avg_real_norm, ideal_norm, initial_mask):
    mask = initial_mask.copy()
    history = []

    MHz_window = 10.0
    win_left = freq.min()
    win_right = win_left + MHz_window

    fig, ax = plt.subplots(figsize=(15, 7))
    plt.subplots_adjust(bottom=0.18)

    ax.set_yscale("log")

    ax.plot(freq, ideal_norm, color="black", label="Ideal")
    ax.plot(freq, avg_real_norm, color="blue", alpha=0.8, label="Average")

    fill = ax.fill_between(freq, 1e-6, 1e6, where=mask, color='red', alpha=0.3)

    ax.set_xlim(win_left, win_right)
    ax.set_xlabel("Frequency (MHz)")
    ax.set_ylabel("Normalised Power (log)")
    ax.set_title("RFI Editor (L-drag toggle, R-drag erase, Undo/Save/←/→)")
    ax.legend(loc="upper right")

    dragging = False
    drag_mode = None
    drag_indices = set()
    last_idx = None

    def redraw():
        nonlocal fill
        for coll in ax.collections:
            coll.remove()
        fill = ax.fill_between(freq, 1e-6, 1e6, where=mask, color="red", alpha=0.3)
        ax.set_xlim(win_left, win_right)
        fig.canvas.draw()
        fig.canvas.flush_events()

    def apply_drag(idx):
        """Apply updates to mask depending on mode."""
        if drag_mode == "toggle":
            mask[idx] = not mask[idx]
        elif drag_mode == "erase":
            mask[idx] = False
        drag_indices.add(idx)

    def interpolate_drag(idx1, idx2):
        """Fill in gaps during fast drags to ensure continuous drawing."""
        if idx1 == idx2:
            apply_drag(idx1)
            return
        step = 1 if idx2 > idx1 else -1
        for k in range(idx1, idx2 + step, step):
            apply_drag(k)

    def on_press(event):
        nonlocal dragging, drag_mode, last_idx, drag_indices
        if event.inaxes != ax:
            return

        dragging = True
        drag_indices = set()
        last_idx = None

        if event.button == 1:
            drag_mode = "toggle"
        elif event.button == 3:
            drag_mode = "erase"
        else:
            drag_mode = "toggle"

        idx = np.abs(freq - event.xdata).argmin()
        last_idx = idx
        apply_drag(idx)
        redraw()

    def on_motion(event):
        nonlocal last_idx
        if not dragging or event.inaxes != ax:
            return

        idx = np.abs(freq - event.xdata).argmin()

        if last_idx is not None:
            interpolate_drag(last_idx, idx)

        last_idx = idx
        redraw()

    def on_release(event):
        nonlocal dragging, drag_indices
        if dragging and len(drag_indices) > 0:
            history.append(list(drag_indices))
        dragging = False
        drag_indices = set()

    def undo(event):
        if len(history) == 0:
            return
        region = history.pop()
        for i in region:
            mask[i] = not mask[i]  # reverse effect
        redraw()

    def save(event):
        plt.close(fig)

    def next_window(event):
        nonlocal win_left, win_right
        win_left += MHz_window
        win_right += MHz_window
        if win_right > freq.max():
            win_right = freq.max()
            win_left = win_right - MHz_window
        redraw()

    def prev_window(event):
        nonlocal win_left, win_right
        win_left -= MHz_window
        win_right -= MHz_window
        if win_left < freq.min():
            win_left = freq.min()
            win_right = win_left + MHz_window
        redraw()

    ax_undo = plt.axes([0.1, 0.02, 0.12, 0.06])
    ax_save = plt.axes([0.25, 0.02, 0.12, 0.06])
    ax_prev = plt.axes([0.55, 0.02, 0.12, 0.06])
    ax_next = plt.axes([0.70, 0.02, 0.12, 0.06])

    b_undo = Button(ax_undo, "Undo")
    b_save = Button(ax_save, "Save")
    b_prev = Button(ax_prev, "← Prev")
    b_next = Button(ax_next, "Next →")

    b_undo.on_clicked(undo)
    b_save.on_clicked(save)
    b_prev.on_clicked(prev_window)
    b_next.on_clicked(next_window)

    fig.canvas.mpl_connect("button_press_event", on_press)
    fig.canvas.mpl_connect("motion_notify_event", on_motion)
    fig.canvas.mpl_connect("button_release_event", on_release)

    plt.show()
    return mask



def main():

    # ----------------------------------------------------------
    # Load ideal spectrum
    # ----------------------------------------------------------
    ideal_data = np.loadtxt("ideal-IE-HBA.dat")
    freq  = ideal_data[:, 0]
    ideal = ideal_data[:, 1]

    # ----------------------------------------------------------
    # Load all real spectra
    # ----------------------------------------------------------
    files = sorted(glob.glob("/datax2/projects/LOFTS/spectrum-stamps/*.dat"))

    master_df = pd.read_csv(
        "/datax2/projects/LOFTS/LOFTS-observations-Progress-Master-Sheet.csv"
    )
    master_df = master_df[
        (master_df["station"] == "IE") &
        (master_df["bandpass bug "] == "No")
    ]
    print("Number of observations with full bandpass", len(master_df))

    sources = master_df["source_name"].unique()

    filtered_files = []
    for file in files:
        file_source = file.split("/")[-1].split(".")[0]
        if file_source not in sources:
            print(f"Removing {file} as source {file_source} not in master sheet")
        else:
            filtered_files.append(file)

    files = filtered_files

    spectra = [np.loadtxt(f)[:, 1] for f in files]
    specs = np.vstack(spectra)      # shape = (n_spec, n_chan)

    n_spec, n_chan = specs.shape

    # ----------------------------------------------------------
    # Ideal Ratio
    # ----------------------------------------------------------
    safe_ideal = np.where(ideal == 0, np.median(ideal), ideal)
    ratio = specs / safe_ideal[None, :]
    eps = 1e-6 * np.median(ratio)
    log_ratio = np.log10(ratio + eps)

    # ignore last 5 MHz
    valid = freq < (freq.max() - 5)

    # ----------------------------------------------------------
    # Iterative ML RFI detection
    # ----------------------------------------------------------
    max_iter = 5
    cumulative_mask = np.zeros(n_chan, dtype=bool)

    for it in range(max_iter):

        print(f"\n=== Iteration {it+1} ===")

        # Exclude previously flagged channels from feature computation
        available = (~cumulative_mask) & valid
        if not np.any(available):
            print("No valid channels left → stopping.")
            break

        lr_clean = log_ratio[:, available]

        features = comp_feats(lr_clean)
        print("Feature shape:", features.shape)

        # Fit model
        rfi_mask_iter, scores = iso_forest(
            features,
            contamination=0.03
        )

        print(f"New RFI found this iteration: {rfi_mask_iter.sum()}")

        if rfi_mask_iter.sum() == 0:
            print("No new RFI detected → stopping.")
            break

        idx_available = np.where(available)[0]
        cumulative_mask[idx_available[rfi_mask_iter]] = True

    print(f"\nTotal RFI channels flagged: {cumulative_mask.sum()}")

    cumulative_mask[~valid] = False

    # ----------------------------------------------------------
    # Compute spectra for interactive editing
    # ----------------------------------------------------------
    avg_real = specs.mean(axis=0)
    avg_real_norm  = avg_real / np.median(avg_real)
    ideal_norm     = ideal     / np.median(ideal)

    # ----------------------------------------------------------
    # Duty cycle (fraction of time RFI-like per channel)
    # ----------------------------------------------------------
    p50_all = np.percentile(log_ratio, 50, axis=0)
    hot_all = (log_ratio > (p50_all + 0.1)[None, :])
    duty_cycle = hot_all.mean(axis=0)   # 0–1

    # ----------------------------------------------------------
    # interactive mask editor
    # ----------------------------------------------------------
    final_mask = interactive_plot(freq, avg_real_norm, ideal_norm, cumulative_mask)

    # ----------------------------------------------------------
    # Save channel / frequency masks and duty cycle
    # ----------------------------------------------------------
    masked_channels = np.where(final_mask)[0]      # 0-based

    # 1) channel ranges
    channel_string = compress_ranges(masked_channels)
    with open("channel-mask.txt", "w") as f:
        f.write(channel_string + "\n")

    # 2) frequency ranges
    df = 0.02435  # MHz per channel
    f_start = 109.596859830097102
    freq_string = channels_to_freq_ranges(masked_channels, f_start, df)
    with open("frequency-mask.txt", "w") as f:
        f.write(freq_string + "\n")

    # 3) duty cycle per channel (percent)
    duty_percent = duty_cycle * 100.0
    np.savetxt(
        "rfi-duty-cycle.txt",
        np.column_stack([np.arange(len(duty_percent)), duty_percent]),
        fmt=["%d", "%.2f"],
        header="channel_index  duty_cycle_percent"
    )


if __name__ == "__main__":
    main()
