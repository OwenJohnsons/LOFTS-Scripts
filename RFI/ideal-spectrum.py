import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.widgets import Button
# import scienceplots
# plt.style.use(['science','ieee','no-latex'])

# -----------------------
# Load data
# -----------------------
freq, power = np.loadtxt("IE-ideal-HBA.txt", skiprows=1, unpack=True)
orig_power = power.copy()
undo_stack = []

# -----------------------
# Setup Figure
# -----------------------
fig, ax = plt.subplots(figsize=(12,6))
line, = ax.plot(freq, power, lw=1)
ax.set_xlabel("Frequency [MHz]")
ax.set_ylabel("Arb. Power")
ax.set_yscale("log")

# Highlight patch
highlight = Rectangle((0,0), 0, 0,
                      facecolor="yellow", alpha=0.3, visible=False)
ax.add_patch(highlight)

start_idx = None
is_dragging = False


# -----------------------
# Helper functions
# -----------------------

def push_undo():
    undo_stack.append(power.copy())

def undo(event=None):
    """Undo last operation."""
    global power
    if len(undo_stack) == 0:
        print("Nothing to undo.")
        return
    power[:] = undo_stack.pop()
    refresh()

def apply_interpolation(i1,i2):
    """Interpolate over selected region."""
    left_val = power[i1]
    right_val = power[i2]
    vals = np.interp(freq[i1:i2], [freq[i1], freq[i2]],
                     [left_val, right_val])
    power[i1:i2] = vals

def refresh():
    """Redraw."""
    line.set_ydata(power)
    fig.canvas.draw_idle()

def save(event=None):
    """Save out cleaned spectrum."""
    out = np.column_stack([freq, power])
    np.savetxt("cleaned_spectrum.txt", out,
               fmt="%.6e", header="freq  power")
    print("Saved → cleaned_spectrum.txt")


# -----------------------
# Mouse events
# -----------------------

def on_press(event):
    global start_idx, is_dragging, orig_power

    if event.inaxes != ax:
        return

    push_undo()
    orig_power = power.copy()
    start_idx = np.argmin(np.abs(freq - event.xdata))
    is_dragging = True

def on_motion(event):
    if not is_dragging or event.inaxes != ax:
        return

    cur_idx = np.argmin(np.abs(freq - event.xdata))
    i1, i2 = sorted([start_idx, cur_idx])

    y0, y1 = ax.get_ylim()
    highlight.set_visible(True)
    highlight.set_x(freq[i1])
    highlight.set_y(y0)
    highlight.set_width(freq[i2] - freq[i1])
    highlight.set_height(y1 - y0)

    power[:] = orig_power
    apply_interpolation(i1,i2)
    refresh()

def on_release(event):
    global start_idx, is_dragging

    if not is_dragging or event.inaxes != ax:
        return
    
    end_idx = np.argmin(np.abs(freq - event.xdata))
    i1, i2 = sorted([start_idx, end_idx])

    apply_interpolation(i1, i2)

    highlight.set_visible(False)
    refresh()

    start_idx = None
    is_dragging = False


# -----------------------
# Keyboard shortcuts
# -----------------------

def on_key(event):
    if event.key == 'z':
        undo()
    if event.key == 's':
        save()


# -----------------------
# Buttons
# -----------------------
ax_undo = plt.axes([0.13, 0.02, 0.1, 0.06])
btn_undo = Button(ax_undo, "Undo")
btn_undo.on_clicked(undo)

ax_save = plt.axes([0.26, 0.02, 0.1, 0.06])
btn_save = Button(ax_save, "Save")
btn_save.on_clicked(save)


# -----------------------
# Connect events
# -----------------------
fig.canvas.mpl_connect("button_press_event", on_press)
fig.canvas.mpl_connect("motion_notify_event", on_motion)
fig.canvas.mpl_connect("button_release_event", on_release)
fig.canvas.mpl_connect("key_press_event", on_key)

plt.show()
