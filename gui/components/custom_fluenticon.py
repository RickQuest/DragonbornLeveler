from qfluentwidgets import FluentIconBase, getIconColor, Theme
from enum import Enum
from importlib import resources

class CustomFluentIcon(FluentIconBase, Enum):
    HAND = "Hand"
    BED = "Bed"
    REPEAT = "Repeat"
    SPARKLE = "Sparkle"
    TIMER = "Timer"
    EYETRACKING = "EyeTracking"
    
    def path(self, theme=Theme.AUTO):
        if self.name in ['HAND', 'BED', 'REPEAT', 'SPARKLE', 'TIMER', 'EYETRACKING']:
            icon_path = resources.files('gui.resources.icons') / f'{self.value}_{getIconColor(theme)}.svg'
            return str(icon_path)
        else:
            return super().path(theme)
