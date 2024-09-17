# bot_window.py
from importlib import resources
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import (NavigationItemPosition, FluentWindow, SplashScreen)
from qfluentwidgets import FluentIcon as FIF
from gui.setting_interface import SettingInterface
from gui.bot_interface import BotInterface
from config.config import cfg

class MainWindow(FluentWindow):

    def __init__(self):
        super().__init__()
        self.initWindow()

        # create sub interface
        self.botInterface = BotInterface(self)
        self.settingInterface = SettingInterface(self)  # Use the ParameterPage class


        # enable acrylic effect
        self.navigationInterface.setAcrylicEnabled(True)

        # Add items to navigation interface
        self.initNavigation()
        self.splashScreen.finish()

    def initNavigation(self):
        self.addSubInterface(self.botInterface, FIF.ROBOT, self.tr('Bot'))
        # self.addSubInterface(self.configInterface, FIF.SETTING, self.tr('Logic Settings'))
        self.addSubInterface(self.settingInterface, FIF.SETTING, self.tr('Gui Settings'), NavigationItemPosition.BOTTOM)

    def initWindow(self):
        self.resize(960, 780)
        self.setMinimumWidth(760)
        self.setWindowIcon(QIcon(str(resources.files('gui.resources.icons') / 'skyrim.ico')))

        self.setWindowTitle('Dragonborn Leveler')

        self.setMicaEffectEnabled(cfg.get(cfg.gui_micaEnabled))

        # create splash screen
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(106, 106))
        self.splashScreen.raise_()

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)
        self.show()
        QApplication.processEvents()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, 'splashScreen'):
            self.splashScreen.resize(self.size())



