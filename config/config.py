# coding:utf-8
import sys
import os
from enum import Enum
from qfluentwidgets import (qconfig, QConfig, ConfigItem, OptionsConfigItem, BoolValidator,
                            OptionsValidator, RangeConfigItem, RangeValidator,
                            EnumSerializer, __version__)
from qfluentwidgets import FluentIcon as FIF
from gui.components.custom_fluenticon import CustomFluentIcon
from gui.components.custom_qfluentwidgets import StringValidator, RegionValidator
from core.app_data_manager import app_data_manager

class CustomConfigItemBase:
    def __init__(self, content="", icon=None):
        self.content = content  # Add the content attribute
        self.icon = icon


class CustomConfigItem(ConfigItem, CustomConfigItemBase):
    def __init__(self, group, name, default, validator=None, serializer=None, restart=False, content="", icon=None):
        super().__init__(group, name, default, validator, serializer, restart)
        CustomConfigItemBase.__init__(self, content, icon)  # Initialize content from CustomConfigItemBase

class CustomRangeConfigItem(RangeConfigItem, CustomConfigItemBase):
    def __init__(self, group, name, default, validator=None, serializer=None, restart=False, content="",icon=None):
        super().__init__(group, name, default, validator, serializer, restart)
        CustomConfigItemBase.__init__(self, content,icon)  # Initialize content from CustomConfigItemBase


class CustomOptionsConfigItem(OptionsConfigItem, CustomConfigItemBase):
    def __init__(self, group, name, default, validator=None, serializer=None, restart=False, content="",icon=None):
        super().__init__(group, name, default, validator, serializer, restart)
        CustomConfigItemBase.__init__(self, content,icon)  # Initialize content from CustomConfigItemBase


class HandSelection(Enum):
        NONE = "none"
        LEFT = "l"
        RIGHT = "r"
        BOTH = "lr"

class LogLevel(Enum):
        DEBUG = "DEBUG"
        INFO = "INFO"
        WARNING = "WARNING"
        ERROR = "ERROR"
        CRITICAL = "CRITICAL"

class HealingSpell(Enum):
    FAST_HEAL = 0.5
    HEALING = 4
    HEALING_HANDS = 1.2
    GRAND_HEAL = 2.0

class DpiScale(Enum):
    _100 = 1
    _125 = 1.25
    _150 = 1.5
    _175 = 1.75
    _200 = 2
    AUTO = 'Auto'



def isWin11():
    return sys.platform == 'win32' and sys.getwindowsversion().build >= 22000

class Config(QConfig):
    # region General settings
    general_log_level = CustomOptionsConfigItem("General",
                                            "debug_level",
                                            LogLevel.INFO,
                                            OptionsValidator(list(LogLevel)),
                                            EnumSerializer(LogLevel),
                                            content="Choose the logging level",
                                            icon=CustomFluentIcon.SPARKLE,
                                            restart=True
                                            )

    general_debug = CustomConfigItem("General",
                               "debug_flag",
                               False,
                               BoolValidator(),
                               content="Add debug action to bot sequence",
                               icon=CustomFluentIcon.SPARKLE
                               )

    general_window_name = CustomConfigItem("General",
                                     "window_name",
                                     'Skyrim Special Edition',
                                     StringValidator(),
                                     content= "Name of the Skyrim window",
                                     icon=CustomFluentIcon.SPARKLE)

    general_bot_hotkey = CustomConfigItem("General",
                                     "bot_hotkey",
                                     'pause',
                                     StringValidator(),
                                     content= "The hotkey input to start and stop bot.",
                                     icon=CustomFluentIcon.SPARKLE)

    general_region_healtbar = CustomConfigItem("General",
                                     "region_healtbar",
                                     [774, 1006, 375, 19],
                                     RegionValidator(),
                                     content= "Region containing the health bar.",
                                     icon=CustomFluentIcon.SPARKLE)

    general_region_favselect = CustomConfigItem("General",
                                     "region_favselect",
                                     [7, 791, 395, 43],
                                     RegionValidator(),
                                     content= "Region containing the name of the active favorite.",
                                     icon=CustomFluentIcon.SPARKLE)

    general_region_menu = CustomConfigItem("General",
                                     "region_menu",
                                     [517, 82, 96, 43],
                                     RegionValidator(),
                                     content= "Region containing the menu text.",
                                     icon=CustomFluentIcon.SPARKLE)

    general_region_favequip = CustomConfigItem("General",
                                     "region_favequip",
                                     [402, 798, 29, 35],
                                     RegionValidator(),
                                     content= "Region containing favorite hand selection symbol.",
                                     icon=CustomFluentIcon.SPARKLE)

    # endregion

    # region GUI settings
    gui_enableAcrylicBackground = CustomConfigItem("Gui",
                           "Use Acrylic effect",
                           False,
                           BoolValidator(),
                           content="Acrylic effect has better visual experience, but it may cause the window to become stuck",
                           icon=FIF.TRANSPARENT
                           )
    gui_dpiScale = CustomOptionsConfigItem("Gui",
                                            "Interface zoom",
                                            DpiScale.AUTO,
                                            OptionsValidator(list(DpiScale)),
                                            EnumSerializer(DpiScale),
                                            content="Change the size of widgets and fonts",
                                            icon=FIF.ZOOM,
                                            restart=True
                                            )
    gui_micaEnabled = CustomConfigItem("Gui",
                           "Mica effect",
                           False,
                           BoolValidator(),
                           content="Apply semi transparent to windows and surfaces",
                           icon=FIF.TRANSPARENT
                           )
    # endregion

    # region App settings

    gui_minimizeToTray = CustomConfigItem("App",
                           "Minimize to tray after closing",
                           False,
                           BoolValidator(),
                           content="The application will continue to run in the background",
                           icon=FIF.MINIMIZE
                           )
    # endregion

    # region Train Illusion settings
    illusion_repeat_time = CustomRangeConfigItem("train_illusion",
                                                 "RepeatTimes",
                                                 5,
                                                 RangeValidator(1, 9999),
                                                 content="Number of times the Muffle spell is cast.",
                                                 icon=CustomFluentIcon.REPEAT
                                                 )
    illusion_hand = CustomOptionsConfigItem("train_illusion",
                                            "Hand",
                                            HandSelection.RIGHT,
                                            OptionsValidator(list(HandSelection)),
                                            EnumSerializer(HandSelection),
                                            content="Choose the hand to cast the spell. Choose \"Both\" for dual cast.",
                                            icon=CustomFluentIcon.HAND
                                            )
    illusion_bed = CustomConfigItem("train_illusion",
                                    "Bed",
                                    False,
                                    BoolValidator(),
                                    content="Sleep in bed and gain \"Well Rested\" bonus while leveling. You need to target a bed.",
                                    icon=CustomFluentIcon.BED
                                    )
    # endregion

    # region Train Conjuration settings
    conjuration_repeat_time = CustomRangeConfigItem("train_conjuration",
                                                 "RepeatTimes",
                                                 5,
                                                 RangeValidator(1, 9999),
                                                 content="Number of times the spell Soul Trap spell is cast.",
                                                 icon=CustomFluentIcon.REPEAT
                                                 )
    conjuration_hand = CustomOptionsConfigItem("train_conjuration",
                                            "Hand",
                                            HandSelection.RIGHT,
                                            OptionsValidator(list(HandSelection)),
                                            EnumSerializer(HandSelection),
                                            content="Choose the hand to cast the spell. Choose \"Both\" for dual cast.",
                                            icon=CustomFluentIcon.HAND
                                            )
    # endregion

    # region Train armor settings
    armor_train_time = CustomRangeConfigItem("train_armor",
                                                 "Train time",
                                                 1,
                                                 RangeValidator(1, 1000),
                                                 content="The training time in minutes.",
                                                 icon=CustomFluentIcon.TIMER
                                                 )
    armor_healing_skill = CustomOptionsConfigItem("train_armor",
                                            "Healing skill",
                                            HealingSpell.HEALING,
                                            OptionsValidator(list(HealingSpell)),
                                            EnumSerializer(HealingSpell),
                                            content="Choose the healing skill to train.",
                                            icon=FIF.HEART
                                            )
    armor_hand = CustomOptionsConfigItem("train_armor",
                                            "Hand",
                                            HandSelection.RIGHT,
                                            OptionsValidator(list(HandSelection)),
                                            EnumSerializer(HandSelection),
                                            content="Choose the hand to cast the spell. Choose \"Both\" for dual cast.",
                                            icon=CustomFluentIcon.HAND
                                            )
    # endregion


AUTHOR = "Eric Surprenant"
VERSION = __version__

# Create the config object
cfg = Config()

# Use AppDataManager to get the path for the config file
config_path = app_data_manager.get_file_path('config.json')

# Load the configuration from the custom path
qconfig.load(config_path, cfg)
