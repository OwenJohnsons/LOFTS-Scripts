import numpy as np
import glob
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


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
    local_mad = np.median(np.abs(Iwin - np.median(Iwin, axis=1)[:, None]), axis=1)

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


def interactive_plot(freq, avg_real_norm, ideal_norm, initial_mask):
    mask = initial_mask.copy()
    history = []

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.set_yscale("log")

    ax.plot(freq, ideal_norm, color="black", label="Ideal")
    ax.plot(freq, avg_real_norm, color="blue", alpha=0.8, label="Average")

    fill = ax.fill_between(freq, 1e-6, 1e6, where=mask, color='red', alpha=0.3)

    ax.set_xlabel("Frequency")
    ax.set_ylabel("Normalised Power (log)")
    ax.set_title("Interactive RFI Editor\n(click, click–drag, 'u' undo, 's' save)")
    ax.legend()

    dragging = False
    drag_start = None
    drag_end = None

    def redraw():
        nonlocal fill
        for coll in ax.collections:
            coll.remove()
        fill = ax.fill_between(freq, 1e-6, 1e6, where=mask, color='red', alpha=0.3)
        fig.canvas.draw_idle()

    def on_press(event):
        nonlocal dragging, drag_start
        if event.inaxes != ax:
            return
        dragging = True
        drag_start = event.xdata

    def on_motion(event):
        nonlocal dragging, drag_end
        if not dragging:
            return
        if event.inaxes != ax:
            return
        drag_end = event.xdata

    def on_release(event):
        nonlocal dragging, drag_start, drag_end

        if not dragging:
            return
        dragging = False

        if drag_start is None:
            return

        if drag_end is None:
            drag_end = drag_start

        x1, x2 = sorted([drag_start, drag_end])
        idx1 = np.abs(freq - x1).argmin()
        idx2 = np.abs(freq - x2).argmin()

        if idx1 == idx2:
            mask[idx1] = ~mask[idx1]
            history.append([idx1])
            redraw()
            drag_start = None
            drag_end = None
            return

        region = list(range(idx1, idx2 + 1))
        for i in region:
            mask[i] = ~mask[i]

        history.append(region)
        redraw()

        drag_start = None
        drag_end = None

    def onkey(event):
        if event.key == "u":
            if len(history) > 0:
                region = history.pop()
                for i in region:
                    mask[i] = ~mask[i]
                redraw()
        if event.key == "s":
            plt.close(fig)

    fig.canvas.mpl_connect('button_press_event', on_press)
    fig.canvas.mpl_connect('motion_notify_event', on_motion)
    fig.canvas.mpl_connect('button_release_event', on_release)
    fig.canvas.mpl_connect('key_press_event', onkey)

    plt.show()
    return mask


def main():

    # ----------------------------------------------------------
    # Load ideal spectrum
    # ----------------------------------------------------------
    ideal_data = np.loadtxt("ideal-SE-HBA.dat")
    freq  = ideal_data[:, 0]
    ideal = ideal_data[:, 1]

    # ----------------------------------------------------------
    # Load all real spectra
    # ----------------------------------------------------------
    files = sorted(glob.glob("/datax2/projects/LOFTS/spectrum-stamps/*.dat"))
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
    # interactive mask editor
    # ----------------------------------------------------------
    final_mask = interactive_plot(freq, avg_real_norm, ideal_norm, cumulative_mask)

    # ----------------------------------------------------------
    # Save channel numbers 
    # ----------------------------------------------------------
    masked_channels = np.where(final_mask)[0]      # 0-based
    np.savetxt("rfi_final_mask.txt",
               masked_channels,
               fmt="%d",
               header="channel_index (0-based)")


if __name__ == "__main__":
    main()
