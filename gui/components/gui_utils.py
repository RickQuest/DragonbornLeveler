import os
from PyQt5.QtGui import QIcon
from qfluentwidgets import (SettingCardGroup, SwitchSettingCard,
    RangeSettingCard, ComboBoxSettingCard, BoolValidator, RangeValidator, OptionsValidator
)
import logging
from config.config import cfg, CustomConfigItemBase
from gui.components.custom_qfluentwidgets import StringValidator, LineEditSettingCard, RegionValidator, RegionSettingCard

class GuiUtils:
    def load_icon(icon_path):
        """Load an icon from the specified path, checking if it exists."""
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        else:
            logging.error(f"Icon not found: {icon_path}")
            # Optionally, return a default or fallback icon
            return QIcon()  # or return a specific default icon path if you have one
        
    def generate_Card_from_config(group_name, settingCardGroup:SettingCardGroup):
        """Generate UI elements dynamically based on the group name."""
        for attr_name in dir(cfg):
            config_item = getattr(cfg, attr_name)
            if isinstance(config_item, CustomConfigItemBase) and config_item.group == group_name:
                if isinstance(config_item.validator, BoolValidator):
                    setting_card = SwitchSettingCard(
                        config_item.icon, config_item.name, content=config_item.content, configItem=config_item, parent=settingCardGroup
                    )
                elif isinstance(config_item.validator, RangeValidator):
                    setting_card = RangeSettingCard(
                        config_item, config_item.icon, config_item.name, config_item.content, parent=settingCardGroup
                    )
                elif isinstance(config_item.validator, OptionsValidator):
                    options = [opt.name for opt in config_item.validator.options]
                    setting_card = ComboBoxSettingCard(
                        config_item, config_item.icon, config_item.name, config_item.content, texts=options, parent=settingCardGroup
                    )
                elif isinstance(config_item.validator, StringValidator):
                    setting_card = LineEditSettingCard(
                        config_item.icon, config_item.name, content=config_item.content, configItem=config_item, parent=settingCardGroup
                    )
                elif isinstance(config_item.validator, RegionValidator):
                    setting_card = RegionSettingCard(
                        config_item.icon, config_item.name, content=config_item.content, configItem=config_item, parent=settingCardGroup
                    )
                else:
                    continue

                settingCardGroup.addSettingCard(setting_card)