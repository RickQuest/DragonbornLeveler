import sys
import numpy as np
import cv2
import pyautogui
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QLabel, QLineEdit, QPushButton, QWidget, QFileDialog, QMessageBox
import pygetwindow as gw

class ScreenshotApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Window Screenshot Tool")
        self.setGeometry(100, 100, 400, 200)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Window Name Input
        self.window_name_label = QLabel("Enter the Window Name:")
        layout.addWidget(self.window_name_label)
        self.window_name_input = QLineEdit()
        layout.addWidget(self.window_name_input)

        # File Name Input
        self.filename_label = QLabel("Enter the Filename (including path) to save the screenshot:")
        layout.addWidget(self.filename_label)
        self.filename_input = QLineEdit()
        layout.addWidget(self.filename_input)

        # Browse Button for filename
        self.browse_button = QPushButton("Browse", self)
        self.browse_button.clicked.connect(self.browse_file)
        layout.addWidget(self.browse_button)

        # Take Screenshot Button
        self.screenshot_button = QPushButton("Take Screenshot", self)
        self.screenshot_button.clicked.connect(self.take_screenshot)
        layout.addWidget(self.screenshot_button)

        # Set Layout
        self.setLayout(layout)

    def browse_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Screenshot As", "", "Images (*.png *.jpg *.bmp)", options=options)
        if file_name:
            self.filename_input.setText(file_name)

    def take_screenshot(self):
        window_name = self.window_name_input.text().strip()
        file_name = self.filename_input.text().strip()

        if not window_name or not file_name:
            QMessageBox.warning(self, "Error", "Please enter both window name and filename.")
            return

        try:
            window = gw.getWindowsWithTitle(window_name)[0]
            window.activate()

            # Get window dimensions
            left, top, right, bottom = window.left, window.top, window.right, window.bottom
            region = (left, top, right - left, bottom - top)

            # Capture the screenshot using pyautogui
            screenshot = pyautogui.screenshot(region=region)

            # Convert to NumPy array
            screenshot = np.array(screenshot)

            # Convert RGB to BGR for OpenCV
            screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

            # Save the screenshot using OpenCV
            cv2.imwrite(file_name, screenshot)

            # Bring the focus back to the app after the screenshot
            self.activateWindow()

            QMessageBox.information(self, "Success", f"Screenshot saved as {file_name}")

        except IndexError:
            QMessageBox.warning(self, "Error", f"Window with name '{window_name}' not found.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ScreenshotApp()
    ex.show()
    sys.exit(app.exec_())
