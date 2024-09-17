from PyQt5.QtCore import QObject, pyqtSignal
import logging

class TextEditLogger(logging.Handler, QObject):
    appendText = pyqtSignal(str)

    def __init__(self, widget):
        super().__init__()
        QObject.__init__(self)
        self.widget = widget
        self.setLevel(logging.DEBUG)
        self.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s'))
        self.appendText.connect(self.widget.append)

    def emit(self, record):
        msg = self.format(record)
        self.appendText.emit(msg)