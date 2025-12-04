import sys
import mne
import numpy as np

from PyQt6 import QtWidgets, uic, QtCore
import pyqtgraph as pg


edf_path = r"D:\Files\KIT\Master\1.Semester\Praktikum - SUS\Dataset\studie001_2019.05.08_10.15.34.edf"


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Load UI from Qt Designer 6
        uic.loadUi("main.ui", self)

        # ----------------------------
        # Attach pyqtgraph to plotWidget
        # ----------------------------
        self.graph = pg.PlotWidget()
        layout = QtWidgets.QVBoxLayout(self.plotWidget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.graph)

        self.graph.setLabel("bottom", "Time", units="s")
        self.graph.setLabel("left", "Amplitude", units="µV")
        self.graph.showGrid(x=True, y=True)

        # ----------------------------
        # Load EEG data using MNE
        # ----------------------------
        raw = mne.io.read_raw_edf(edf_path, preload=True)
        data, times = raw.get_data(return_times=True)

        self.sfreq = int(raw.info["sfreq"])
        self.channel = 8

        self.signal = data[self.channel]
        self.times = times

        self.window_size = self.sfreq      # 1-second window
        self.step = self.sfreq // 10       # move 0.1 sec each update

        self.ptr = 0

        # Create graph curve
        self.curve = self.graph.plot([], [])

        # Fix y-range
        self.graph.setYRange(np.min(self.signal), np.max(self.signal))

        # ----------------------------
        # Button connects to start
        # ----------------------------
        self.pushButton.clicked.connect(self.start_stream)

        # Timer used for updating the plot
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)

    def start_stream(self):
        self.ptr = 0
        self.timer.start(100)   # update every 100 ms
        self.pushButton.setText("Clicked!")

    def update_plot(self):
        start = self.ptr
        end = start + self.window_size

        if end >= len(self.signal):
            self.timer.stop()
            return

        x = self.times[start:end]
        y = self.signal[start:end]

        self.curve.setData(x, y)
        self.graph.setXRange(x[0], x[-1])

        self.ptr += self.step


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
