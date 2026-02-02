import mne
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

# Path to the EDF file
edf_path = r"D:\Files\KIT\Master\1.Semester\Praktikum - SUS\Dataset\studie001_2019.05.08_10.15.34.edf"

 # Load the EDF file
raw = mne.io.read_raw_edf(edf_path, preload=True)
#print(raw.info) # info about the data (channel names, num of channels, sample frequency ...)
"""Channels COUNTER, INTERPOLATED are not EEG channels and should be ignored for plotting EEG data."""

# Get data and times
data, times = raw.get_data(return_times=True)
sfreq = int(raw.info['sfreq'])  # e.g., 256 Hz
channel_index = 8               # which channel

y_raw = data[channel_index, :]
print("min:", np.min(y_raw), "max:", np.max(y_raw))

# Window size in samples (1 second)
window_size = sfreq

# Prepare figure
fig, ax = plt.subplots(figsize=(12, 4))
line, = ax.plot([], [], lw=1.5)
ax.set_xlabel("Time (s)")
ax.set_ylabel("Amplitude (µV)")
ax.set_title(f"EEG Channel: {raw.info['ch_names'][channel_index]}")
ax.grid(True)

# Fix y-axis limits
#ax.set_ylim(0.004175, 0.00425) # hardcored values for y for channel 5, better visualization for the first 6 seconds

# y values from min to max of the whole signal
ax.set_ylim(np.min(y_raw), np.max(y_raw))

# --- Update function ---
def update(frame):
    start = frame
    end = start + window_size
    if end > data.shape[1]:
        ani.event_source.stop()
        return line,

    # Absolute time x-axis
    x = times[start:end]
    y = data[channel_index, start:end]

    line.set_data(x, y)

    # Slide x-axis to follow the window
    ax.set_xlim(x[0], x[-1])
    return line,

# --- Animation ---
step = int(sfreq / 10)  # shift window by 0.1 s per frame
ani = animation.FuncAnimation(
    fig,
    update,
    frames=range(0, data.shape[1]-window_size, step),
    interval=1000,   # 100 ms per frame
    blit=False      # Important: disable blit to allow axis updates
)

plt.tight_layout()
plt.show() 


"""

#Display diagram of channel 5 of the first second

# Get the data as a NumPy array
data, times = raw.get_data(return_times=True)
print("Shape:", data.shape)  # (n_channels, n_samples)
print("First few samples:", data[:5, :10])
print("First few times:", times[:10])

# Take the first 10 values
x = times[:256] # the frequancy is 256 Hz, so this means the first second
y = data[5, :256]   # 5th channel, 

# Create the plot
plt.figure(figsize=(6, 4))
plt.plot(x, y, marker='o')  
plt.xlabel('Time (s)')
plt.ylabel('Amplitude (µV)')
plt.title('First second from 5th EEG channel')
plt.grid(True)
plt.show()  

"""



