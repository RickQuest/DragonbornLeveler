# coding:utf-8
import os
from config.logging_config import setup_logging
from config.config import cfg
import sys
from PyQt5.QtCore import Qt  # Importing Qt for setting application attributes
from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtGui import QPixmap
from gui.main_window import MainWindow
import logging
from importlib import resources

def main():
    try:
        cfg.load()
        # Setup logging configuration
        setup_logging()

        if cfg.get(cfg.gui_dpiScale) == "Auto":
            QApplication.setHighDpiScaleFactorRoundingPolicy(
                Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
            QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        else:
            os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
            os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.gui_dpiScale.value))

        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

        app = QApplication(sys.argv)
        pixmap = QPixmap(str(resources.files('gui.resources.icons') / 'skyrim.ico'))  # Use a small, quick-to-load image
        splash = QSplashScreen(pixmap, Qt.WindowStaysOnTopHint)
        splash.show()

        window = MainWindow()
        splash.finish(window)
        window.show()
        sys.exit(app.exec_())

    except SystemExit:
        logging.info("Application exited normally.")
        # SystemExit is expected, no need to log as an error
        pass
    except Exception as e:
        logging.error("Unhandled exception occurred", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
