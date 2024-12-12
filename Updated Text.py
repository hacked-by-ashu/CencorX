import cv2
import pytesseract
import numpy as np
import mss
from PIL import ImageGrab
from PyQt5 import QtWidgets, QtGui, QtCore
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# Load abusive words from bad.txt
with open("C:/Users/Moham/Desktop/Test codes/bad.txt", "r", encoding="utf-8") as f:
    BAD_WORDS = set(word.strip().lower() for word in f.readlines())

class ScreenMonitor:
    def __init__(self):
        # Set Tesseract-OCR path if needed
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    def capture_screen(self):
        with mss.mss() as screen_capture:
            monitor = screen_capture.monitors[1]  # Primary monitor
            screen = np.array(screen_capture.grab(monitor))
            return cv2.cvtColor(screen, cv2.COLOR_BGRA2RGB)

    def detect_and_blur(self, frame):
        # Convert frame to grayscale for OCR
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Use Tesseract to extract text and bounding boxes
        data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)

        blurred_regions = []
        for i in range(len(data['text'])):
            word = data['text'][i].lower()
            if word in BAD_WORDS:
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                if w > 0 and h > 0:  # Ensure valid bounding box
                    blurred_regions.append((x, y, x + w, y + h))
        return blurred_regions


class OverlayWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint |
                            QtCore.Qt.WindowStaysOnTopHint |
                            QtCore.Qt.WindowTransparentForInput |
                            QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setGeometry(QtWidgets.QApplication.primaryScreen().geometry())
        self.blur_regions = []

    def set_blur_regions(self, regions):
        self.blur_regions = regions
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        for region in self.blur_regions:
            x1, y1, x2, y2 = region
            rect = QtCore.QRect(x1, y1, x2 - x1, y2 - y1)
            painter.fillRect(rect, QtGui.QColor(0, 0, 0, 250))  # Semi-transparent black for blur effect


class GUIApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.monitor_thread = None
        self.worker = None
        self.overlay = OverlayWindow()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Screen Monitor")
        self.setGeometry(100, 100, 400, 200)

        self.start_btn = QtWidgets.QPushButton('Start Monitoring', self)
        self.start_btn.clicked.connect(self.start_monitoring)

        self.stop_btn = QtWidgets.QPushButton('Stop Monitoring', self)
        self.stop_btn.clicked.connect(self.stop_monitoring)
        self.stop_btn.setEnabled(False)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)
        self.setLayout(layout)

    def start_monitoring(self):
        self.overlay.show()  # Show the overlay

        # Start the monitoring thread
        self.monitor_thread = QtCore.QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.monitor_thread)

        # Connect signals
        self.monitor_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.monitor_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.update_overlay.connect(self.overlay.set_blur_regions)
        self.monitor_thread.finished.connect(self.monitor_thread.deleteLater)

        # Enable/disable buttons
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        self.monitor_thread.start()

    def stop_monitoring(self):
        if self.worker:
            self.worker.stop()
        self.monitor_thread.quit()
        self.monitor_thread.wait()
        self.overlay.hide()  # Hide the overlay

        # Enable/disable buttons
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)


class Worker(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    update_overlay = QtCore.pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.screen_monitor = ScreenMonitor()
        self.running = True

    def run(self):
        while self.running:
            frame = self.screen_monitor.capture_screen()
            blurred_regions = self.screen_monitor.detect_and_blur(frame)
            self.update_overlay.emit(blurred_regions)  # Send regions to overlay
        self.finished.emit()

    def stop(self):
        self.running = False


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    gui = GUIApp()
    gui.show()
    sys.exit(app.exec_())
