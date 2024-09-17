# coding: utf-8
from enum import Enum
from qfluentwidgets import StyleSheetBase, Theme, qconfig
from importlib import resources

class StyleSheet(StyleSheetBase, Enum):
    """ Style sheet  """

    CONFIG_INTERFACE = "config_interface"
    BOT_INTERFACE = "bot_interface"
    SETTING_INTERFACE = "setting_interface"

    def path(self, theme=Theme.AUTO):
        theme = qconfig.theme if theme == Theme.AUTO else theme
        temp = str(resources.files('gui.resources.qss') / theme.value.lower() / f'{self.value}.qss')
        return temp
