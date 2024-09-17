# coding:utf-8
from typing import Union
import cv2
import numpy as np
import mss
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QFont, QIntValidator, QImage, QPixmap
from PyQt5.QtWidgets import (QDialog,QVBoxLayout, QPushButton, QLabel)
from qfluentwidgets import (FluentIconBase, SettingCard, TogglePushButton,ConfigValidator,TransparentToolButton, getFont, FluentLabelBase,qconfig, ConfigItem, LineEdit)
from qfluentwidgets import FluentIcon as FIF
from typing import List
from gui.components.custom_fluenticon import CustomFluentIcon


class TogglePushSettingCard(SettingCard):
    """ Setting card with a push button """

    clicked = pyqtSignal()

    def __init__(self, text, icon: Union[str, QIcon, FluentIconBase], title, content=None, parent=None):
        """
        Parameters
        ----------
        text: str
            the text of push button

        icon: str | QIcon | FluentIconBase
            the icon to be drawn

        title: str
            the title of card

        content: str
            the content of card

        parent: QWidget
            parent widget
        """
        super().__init__(icon, title, content, parent)
        self.button = TogglePushButton(FIF.PLAY, 'Toggle push button', self)
        self.button = QPushButton(text, self)
        self.hBoxLayout.addWidget(self.button, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)
        self.button.clicked.connect(self.clicked)

class CustomTitleLabel(FluentLabelBase):
    """ Sub title text label

    Constructors
    ------------
    * TitleLabel(`parent`: QWidget = None)
    * TitleLabel(`text`: str, `parent`: QWidget = None)
    """

    def getFont(self):
        return getFont(20, QFont.Normal)

class LineEditSettingCard(SettingCard):
    """ Setting card with a line edit """

    textChanged = pyqtSignal(str)

    def __init__(self, icon: Union[str, QIcon, FluentIconBase], title, content=None,
                 configItem: ConfigItem = None, parent=None, width=300):
        """
        Parameters
        ----------
        icon: str | QIcon | FluentIconBase
            the icon to be drawn

        title: str
            the title of card

        content: str
            the content of card

        configItem: ConfigItem
            configuration item operated by the card

        parent: QWidget
            parent widget
        """
        super().__init__(icon, title, content, parent)
        self.configItem = configItem
        self.lineEdit = LineEdit(self)

        # Set the width of the LineEdit widget
        self.lineEdit.setFixedWidth(width)

        if configItem:
            self.setValue(qconfig.get(configItem))
            configItem.valueChanged.connect(self.setValue)

        # Add line edit to layout
        self.hBoxLayout.addWidget(self.lineEdit, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

        self.lineEdit.textChanged.connect(self.__onTextChanged)

    def __onTextChanged(self, text: str):
        """ Line edit text changed slot """
        self.setValue(text)
        self.textChanged.emit(text)

    def setValue(self, text: str):
        if self.configItem:
            qconfig.set(self.configItem, text)

        self.lineEdit.setText(text)

    def setText(self, text: str):
        self.setValue(text)

    def text(self) -> str:
        return self.lineEdit.text()

class StringValidator(ConfigValidator):
    """ Validator to check if the value is a string """

    def validate(self, value):
        return isinstance(value, str)

    def correct(self, value):
        if self.validate(value):
            return value
        return ""

class RegionValidator(ConfigValidator):
    """ Validator to check if the value is a list of four integers """

    def validate(self, value):
        # Check if the value is a list of four items
        if not isinstance(value, list) or len(value) != 4:
            return False
        # Check if all items in the list are integers
        return all(isinstance(item, int) for item in value)

    def correct(self, value):
        # If the value is valid, return it as is
        if self.validate(value):
            return value
        # Otherwise, return a default list
        return [0, 0, 0, 0]

class RegionSettingCard(SettingCard):
    """ Setting card with four line edits for region values (x, y, width, height) """
    regionChanged = pyqtSignal(list)

    def __init__(self, icon: Union[str, QIcon, FluentIconBase], title, content=None,
                 configItem: ConfigItem = None, parent=None, width=60):
        super().__init__(icon, title, content, parent)
        self.configItem = configItem

        # Initialize LineEdits for the region coordinates
        self.lineEdits = {
            'x': LineEdit(self),
            'y': LineEdit(self),
            'width': LineEdit(self),
            'height': LineEdit(self)
        }

        # Configure each LineEdit
        int_validator = QIntValidator(0, 9999)
        for lineEdit in self.lineEdits.values():
            lineEdit.setFixedWidth(width)
            lineEdit.setValidator(int_validator)
            lineEdit.textChanged.connect(self.__onRegionChanged)
            self.hBoxLayout.addWidget(lineEdit)

        # Add a button for displaying the region
        self.viewButton = TransparentToolButton(CustomFluentIcon.EYETRACKING, self)
        self.viewButton.clicked.connect(self.showImageDialogWithRegion)
        self.hBoxLayout.addSpacing(16)
        self.hBoxLayout.addWidget(self.viewButton)

        if configItem:
            self.setValue(configItem.value)
            configItem.valueChanged.connect(self.setValue)

        # Create an instance of the ImageDialog
        self.dialog = ImageDialog(parent=self)

    def __onRegionChanged(self):
        """ LineEdit text changed slot """
        region = self.getRegion()
        self.setValue(region)
        self.regionChanged.emit(region)

    def setValue(self, region):
        """ Set the region values to each corresponding LineEdit. """
        if self.configItem:
            qconfig.set(self.configItem, region)
        if len(region) == 4:
            self.lineEdits['x'].setText(str(region[0]))
            self.lineEdits['y'].setText(str(region[1]))
            self.lineEdits['width'].setText(str(region[2]))
            self.lineEdits['height'].setText(str(region[3]))

    def getRegion(self) -> list:
        """ Return the current values from all LineEdits as a list. """
        return [
            int(self.lineEdits['x'].text() or 0),
            int(self.lineEdits['y'].text() or 0),
            int(self.lineEdits['width'].text() or 0),
            int(self.lineEdits['height'].text() or 0)
        ]

    def showImageDialogWithRegion(self):
        """ Opens the ImageDialog and refreshes the image dynamically """
        region = self.getRegion()

        # Update the dialog with the first frame
        self.dialog.updateImage(region)

        # Show the dialog
        self.dialog.show()

        # Set up a QTimer to refresh the image dynamically
        self.timer = QTimer(self)
        self.timer.timeout.connect(lambda: self.dialog.updateImage(region))
        self.timer.start(1000 // 15)  # 15 FPS

    def stopTimer(self):
        """ Stop the QTimer to prevent further updates when the dialog is closed """
        if hasattr(self, 'timer'):
            self.timer.stop()

class ImageDialog(QDialog):
    """Custom dialog to display and update an image"""

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize the image label
        self.imageLabel = QLabel(self)
        self.imageLabel.setFixedSize(400, 300)  # Adjust the size of the image label
        self.imageLabel.setAlignment(Qt.AlignCenter)

        # Set up the layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.imageLabel)
        self.setLayout(layout)

        # Set window properties
        self.setWindowTitle("Region Viewer")
        self.setFixedSize(420, 320)  # Adjust the dialog size

    def setImage(self, q_img: QImage):
        """Set the image in the QLabel"""
        pixmap = QPixmap.fromImage(q_img)
        self.imageLabel.setPixmap(pixmap)

    def updateImage(self, region):
        """Capture the region and update the image in the dialog dynamically"""
        with mss.mss() as sct:
            monitor = {
                'top': region[1],
                'left': region[0],
                'width': region[2],
                'height': region[3]
            }
            img = np.array(sct.grab(monitor))

            # Convert BGRA image to RGB
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)

            # Convert the image to QImage
            height, width, channel = img_rgb.shape
            bytes_per_line = 3 * width
            q_img = QImage(img_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)

            # Set the new image in the dialog
            self.setImage(q_img)



