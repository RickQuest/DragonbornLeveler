from config.config import cfg
from qfluentwidgets import (
    SettingCardGroup, SwitchSettingCard, OptionsSettingCard, ScrollArea,
    ExpandLayout, Theme, InfoBar, CustomColorSettingCard, setTheme, setThemeColor, isDarkTheme
)
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QLabel
from gui.components.gui_utils import GuiUtils
from importlib import resources

micaEnableChanged = pyqtSignal(bool)

class SettingInterface(ScrollArea):
    """ Settings page """

    checkUpdateSig = pyqtSignal()
    acrylicEnableChanged = pyqtSignal(bool)
    minimizeToTrayChanged = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("SettingsPage")

        self.init_widgets()
        self.init_layout()
        self.apply_styles()
        self.connect_signals()

    def init_widgets(self):
        """Initialize all widgets."""
        self.scroll_widget = QWidget()  # Scrollable container for the settings content
        self.expand_layout = ExpandLayout(self.scroll_widget)  # Main layout inside scrollWidget

        # Setting label
        self.setting_label = QLabel(self.tr("Settings"), self)

        # Gui panel section
        self.gui_group = SettingCardGroup(self.tr('Gui'), self.scroll_widget)

        card = cfg.gui_enableAcrylicBackground
        self.enableacrylic_card = SwitchSettingCard(card.icon, card.name, content=card.content, configItem=card, parent=self.gui_group)

        card = cfg.gui_micaEnabled
        self.micaEnabled_card = SwitchSettingCard(card.icon, card.name, content=card.content, configItem=card, parent=self.gui_group)

        self.theme_card = OptionsSettingCard(
            cfg.themeMode,
            FIF.BRUSH,
            self.tr('Application theme'),
            self.tr("Change the appearance of your application"),
            texts=[self.tr('Light'), self.tr('Dark'), self.tr('Use system setting')],
            parent=self.gui_group
        )

        self.themecolor_card = CustomColorSettingCard(
            cfg.themeColor,
            FIF.PALETTE,
            self.tr('Theme color'),
            self.tr('Change the theme color of your application'),
            parent=self.gui_group
        )

        card = cfg.gui_dpiScale
        options = [opt.name for opt in card.validator.options]
        self.zoom_card = OptionsSettingCard(card, card.icon, card.name, card.content, texts=options, parent=self.gui_group)


        # App panel section
        self.mainpanel_group = SettingCardGroup(self.tr('App'), self.scroll_widget)
        card = cfg.gui_minimizeToTray
        self.minimizetotray_card = SwitchSettingCard(card.icon, card.name, content=card.content, configItem=card, parent=self.mainpanel_group)

        # Bot panel section
        self.logic_group = SettingCardGroup(self.tr('Logic'), self.scroll_widget)
        GuiUtils.generate_Card_from_config("General", self.logic_group)

    def init_layout(self):
        """Set up the layout and organize widgets."""
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 120, 0, 20)
        self.setWidget(self.scroll_widget)
        self.setWidgetResizable(True)

        # Set layout for the main label
        self.setting_label.move(60, 63)

        # Add cards to the Personalization group
        self.gui_group.addSettingCard(self.enableacrylic_card)
        self.gui_group.addSettingCard(self.micaEnabled_card)
        self.gui_group.addSettingCard(self.theme_card)
        self.gui_group.addSettingCard(self.themecolor_card)
        self.gui_group.addSettingCard(self.zoom_card)

        # Add cards to the Main panel group
        self.mainpanel_group.addSettingCard(self.minimizetotray_card)

        # Configure the layout for the ExpandLayout in scrollWidget
        self.expand_layout.setSpacing(28)
        self.expand_layout.setContentsMargins(60, 10, 60, 0)
        self.expand_layout.addWidget(self.gui_group)
        self.expand_layout.addWidget(self.mainpanel_group)
        self.expand_layout.addWidget(self.logic_group)


    def apply_styles(self):
        """Apply the QSS stylesheet."""
        self.scroll_widget.setObjectName('scrollWidget')
        self.setting_label.setObjectName('settingLabel')

        theme = 'dark' if isDarkTheme() else 'light'
        qss_path = str(resources.files('gui.resources.qss') / theme / 'setting_interface.qss')

        with open(qss_path, encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def connect_signals(self):
        """Connect signals to corresponding slots."""
        cfg.appRestartSig.connect(self.__showRestartTooltip)
        cfg.themeChanged.connect(self.__onThemeChanged)

        # Personalization section signals
        self.enableacrylic_card.checkedChanged.connect(self.acrylicEnableChanged)
        self.themecolor_card.colorChanged.connect(setThemeColor)

        # Main panel section signals
        self.minimizetotray_card.checkedChanged.connect(self.minimizeToTrayChanged)

    def __showRestartTooltip(self):
        """Show restart tooltip when a configuration change is made."""
        InfoBar.warning(
            '',
            self.tr('Configuration takes effect after restart'),
            parent=self.window()
        )

    def __onThemeChanged(self, theme: Theme):
        """Handle theme changes and reapply QSS."""
        setTheme(theme)
        self.apply_styles()
