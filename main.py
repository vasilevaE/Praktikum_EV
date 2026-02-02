import sys
import mne
import numpy as np

from PyQt6 import QtWidgets, uic, QtCore
from PyQt6.QtGui import QIcon
from scipy.interpolate import make_interp_spline
import pyqtgraph as pg


edf_path = r"D:\Files\KIT\Master\1.Semester\Praktikum - SUS\Dataset\studie001_2019.05.08_10.15.34.edf"


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Load UI from Qt Designer 6
        uic.loadUi("main3.ui", self)

        # ----------------------------
        # ConfidencePlot setup
        # ----------------------------

        # 1. Setup the Layout 
        self.graph = pg.GraphicsLayoutWidget()
        self.graph.setBackground((27, 26, 31))
        layout = QtWidgets.QVBoxLayout(self.confidencePlot)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.graph)

        # 2. Add a Plot Area
        self.plot_area = self.graph.addPlot()
        self.plot_area.showGrid(x=False, y=True, alpha=0.2)

        # 3. Define Static Data
        # Example: Time (0 to 10) and Confidence levels
        x = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        y = np.array([50, 55, 45, 70, 85, 80, 95, 90, 92, 85, 88])

        # 4. Smooth the Data
        x_smooth = np.linspace(x.min(), x.max(), 200) # 200points
        spline = make_interp_spline(x, y, k=3) # k=3 creates the smooth "S" curves
        y_smooth = spline(x_smooth)

        # 5. Plot with Style
        pen = pg.mkPen(color=(0, 255, 255), width=3) # Cyan line
        self.plot_area.plot(x_smooth, y_smooth, pen=pen, antialias=True)

        # Optional: Add a subtle fill under the curve
        brush = pg.mkBrush(0, 255, 255, 50) # Transparent cyan
        self.plot_area.plot(x_smooth, y_smooth, fillLevel=0, fillBrush=brush)



        # ----------------------------
        # Attach pyqtgraph to plotWidget
        # ----------------------------
        self.graph = pg.GraphicsLayoutWidget()
        self.graph.setBackground((27, 26, 31))
        layout = QtWidgets.QVBoxLayout(self.plotWidget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.graph)

        # ----------------------------
        # Load EEG data using MNE
        # ----------------------------
        raw = mne.io.read_raw_edf(edf_path, preload=True)

        # Pick only available EEG channels
        eeg_names = ['AF3','F7','F3','FC5','T7','P7','O1','O2','P8','T8','FC6','F4','F8','AF4']
        available_eeg = [ch for ch in eeg_names if ch in raw.ch_names]
        raw.pick_channels(available_eeg)
        self.data, self.times = raw.get_data(return_times=True)

        self.sfreq = int(raw.info["sfreq"])
        self.ch_names = raw.info["ch_names"]
        self.n_channels = len(self.ch_names)

        # streaming parameters
        self.window_sec = 5
        self.window_samples = self.window_sec * self.sfreq
        self.step = int(self.sfreq / 20)    # 50ms update
        self.ptr = 0
        self.streaming = False              # paused at start

        # ----------------------------
        # Build stacked EEG layout
        # ----------------------------
        colors = [
            (28, 159, 71), # green
            (100, 46, 169), # purple
            (226, 46, 29), # red
            (29, 111, 226), # blue
            (244, 148, 70), # orange
        ]
        
        self.curves = []
        for i, ch in enumerate(self.ch_names):
            lbl = pg.LabelItem(ch, justify='right')
            self.graph.addItem(lbl, row=i, col=0)

            p = self.graph.addPlot(row=i, col=1)
            p.hideAxis('left')
            p.hideAxis('bottom')
            p.setMouseEnabled(x=False, y=False)
            pen = pg.mkPen(color=colors[i % len(colors)], width=1)
            curve = p.plot(np.zeros(self.window_samples), pen=pen)
            self.curves.append(curve)

        # ----------------------------
        # Stream Button pressed
        # ----------------------------
        self.streamBtn.setCheckable(False)
        self.streamBtn.clicked.connect(self.start_stream)

        # ----------------------------
        # Record Button pressed
        # ----------------------------
        self.recordBtn.clicked.connect(self.start_record)

        # ----------------------------
        # History Button pressed
        # ----------------------------
        self.historyBtn.clicked.connect(self.start_history)

        # ----------------------------
        # Display Thresholds Button pressed
        # ----------------------------
        self.thresholdBtn.clicked.connect(self.display_thresholds)

        # Timer used for updating the plot
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(200)     # refresh rate

    def start_stream(self):
        if not self.streaming:
            # Start streaming
            self.streaming = True
            self.timer.start(100)
            self.streamBtn.setIcon(QIcon("icons/pause.svg"))
            self.streamBtn.setStyleSheet("""
                QToolButton {
                    background-color: orange;
                    border-radius: 25px;
                }
            """)
        else:
            # Pause streaming
            self.streaming = False
            self.timer.stop()
            self.streamBtn.setIcon(QIcon("icons/play.svg"))
            self.streamBtn.setStyleSheet("""
                QToolButton {
                    background-color: green;
                    border-radius: 25px;
                }
            """)

    def start_record(self):
        if self.recordBtn.isChecked():
            # Toggle recording state
            self.recordBtn.setIcon(QIcon("icons/square.svg"))
            self.recordBtn.setStyleSheet("""
                QToolButton {
                    background-color: #E22E1D;
                    border-radius: 25px;
                }
            """)
            # TBD: add functionality to start recording data
        else:
            # Stop recording
            self.recordBtn.setIcon(QIcon("icons/circle.svg"))
            self.recordBtn.setStyleSheet("""
                QToolButton {
                    background-color: #E22E1D; 
                    border-radius: 25px;
                }
            """)
            # TBD: add functionality to save recorded data

    def update_plot(self):
        if not self.streaming:
            return

        if self.ptr + self.window_samples >= self.data.shape[1]:
            self.ptr = 0

        sl = slice(self.ptr, self.ptr + self.window_samples)

        for ci in range(self.n_channels):
            self.curves[ci].setData(self.data[ci, sl])

        self.ptr += self.step

    def start_history(self):
        self.history_window = HistoryWindow()
        self.history_window.show()

    def display_thresholds(self):
        # 1. Get values from both labels
        val1 = float(self.value_t1.text())
        val2 = float(self.value_t2.text())
        
        # 2. Setup Pens 
        pen1 = pg.mkPen(color='r', width=2)
        pen1.setStyle(QtCore.Qt.PenStyle.DashLine)
        
        pen2 = pg.mkPen(color='y', width=2)
        pen2.setStyle(QtCore.Qt.PenStyle.DotLine) # Dotted for variety

        # 3. Clean up existing lines 
        if hasattr(self, 'line_a'):
            self.plot_area.removeItem(self.line_a)
        if hasattr(self, 'line_b'):
            self.plot_area.removeItem(self.line_b)
            
        # 4. Create and add both lines
        self.line_a = pg.InfiniteLine(pos=val1, angle=0, pen=pen1)
        self.line_b = pg.InfiniteLine(pos=val2, angle=0, pen=pen2)
        
        self.plot_area.addItem(self.line_a)
        self.plot_area.addItem(self.line_b)

        # Optional: Auto-scale the view to make sure both lines are visible
        self.plot_area.enableAutoRange()


class HistoryWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("history.ui", self) 
        self.populate_table()

    def populate_table(self):
        # Set 3 columns
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setRowCount(4)  # example 4 rows

        # Set header labels
        self.tableWidget.setHorizontalHeaderLabels(["TIMESTAMP", "EVENT", "STATUS"])

        # Example data
        data = [
            ["12:05:32", "Login attempt", "Success"],
            ["12:15:07", "Login attempt", "Failed"],
            ["12:20:45", "EEG scan", "Success"],
            ["12:30:12", "Logout", "Success"]
        ]

        # Fill the table
        for row_idx, row_data in enumerate(data):
            for col_idx, value in enumerate(row_data):
                self.tableWidget.setItem(row_idx, col_idx, QtWidgets.QTableWidgetItem(value))

        # Make table resize to content
        self.tableWidget.resizeColumnsToContents()

            # Stretch columns
        self.tableWidget.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.Stretch
        )

        # Optional: hide row numbers
        self.tableWidget.verticalHeader().setVisible(False)



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
