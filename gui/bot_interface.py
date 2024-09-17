from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QListWidgetItem, QFrame, 
)
from PyQt5.QtCore import Qt, pyqtSignal, QThreadPool, pyqtSlot
from qfluentwidgets import (
    ListWidget, TogglePushButton, ExpandLayout, SettingCardGroup, TextEdit, isDarkTheme, setTheme, Theme
)
from qfluentwidgets import FluentIcon as FIF
import logging
import keyboard
from config.config import cfg
from gui.components.custom_qfluentwidgets import CustomTitleLabel
from gui.components.logging_component import TextEditLogger
from core.logic import Logic
from core.training_runnable import TrainingRunnable 
from gui.components.gui_utils import GuiUtils
from gui.components.custom_qwidgets import BotListItemWidget, DarkOverlay
from importlib import resources

class BotInterface(QWidget):
    finished_signal = pyqtSignal()  # Declare the signal here
    
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("BotInterface")

        keyboard.add_hotkey(cfg.general_bot_hotkey.value, self.toggle_hotkey_action)  # Setup a global hotkey (e.g., F9) to start/stop the bot
        self.logic = Logic()  # Assuming Logic class is defined elsewhere
        self.current_runnable = None  # To hold the QRunnable instance
        self.thread_pool = QThreadPool()
        self.logger = logging.getLogger(self.__class__.__name__)  # Get a logger for this class

        self.init_widgets()
        self.init_layout()
        # StyleSheet.BOT_INTERFACE.apply(self)
        self.connect_signals()
        self.apply_styles()
        # self._setup_logger_widget()

    def init_widgets(self):
        # Create a container widget for all content
        self.container_widget = QWidget(self)
        self.container_widget.setObjectName("container_widget")
        
        # Bot selection section
        self.bot_selection_label = CustomTitleLabel('Bot selection', self.container_widget)
        self.bot_list_widget = ListWidget(self.container_widget)
        self._setup_bot_list_widget()
        self.bot_list_widget.setObjectName("list")
        self.play_button_widget = TogglePushButton(FIF.PLAY, 'Start', self.container_widget)
        
        # Bot settings widgets
        self.scroll_widget = QWidget(self.container_widget)
        self.scroll_widget.setObjectName("scroll")
        self.expand_layout = ExpandLayout(self.scroll_widget)  

        self.personal_group = SettingCardGroup(self.tr('Bot settings'), self.scroll_widget)
        self.expand_layout.addWidget(self.personal_group)

        # Log widget
        self.log_text_edit = TextEdit(self.container_widget)
        self.log_text_edit.setObjectName("textedit")
        self.log_text_edit.setReadOnly(True)
        self.log_text_edit.setPlaceholderText("Log output will appear here...")

        # Setup logger
        self.text_edit_logger = TextEditLogger(self.log_text_edit)
        logging.getLogger().addHandler(self.text_edit_logger)

        self.overlay = DarkOverlay(self)
        self.overlay.hide()  # Initially hidden

        # Populate bot list
        self._populate_bot_list()

    def init_layout(self):
        """Set up the layout and organize widgets."""
        
        # Main layout for the BotInterface
        self.main_layout = QVBoxLayout(self)  # QVBoxLayout instead of QGridLayout for simplicity
        self.main_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        self.main_layout.setSpacing(0)  # No spacing between widgets

        # Add container_widget to main_layout
        self.main_layout.addWidget(self.container_widget)

        # Create a layout for the container_widget to hold its contents
        container_layout = QGridLayout(self.container_widget)
        container_layout.setContentsMargins(20, 10, 20, 10)
        
        # Layout for bot selection
        self.bot_selection_layout = QVBoxLayout()
        self.bot_selection_layout.setAlignment(Qt.AlignTop)
        self.bot_selection_layout.setSpacing(0)
        self.bot_selection_layout.addSpacing(10)
        self.bot_selection_layout.addWidget(self.bot_selection_label)
        self.bot_selection_layout.addSpacing(12)
        self.bot_selection_layout.addWidget(self.bot_list_widget)
        self.bot_selection_layout.addWidget(self.play_button_widget)

        # Layout for bot settings and log output
        self.vertical_layout = QVBoxLayout()
        self.vertical_layout.addWidget(self.scroll_widget, stretch=1)

        # Add bot selection and bot settings layouts to the container layout
        container_layout.addLayout(self.bot_selection_layout, 0, 0)
        container_layout.addLayout(self.vertical_layout, 0, 1)
        container_layout.addWidget(self.log_text_edit, 1, 0, 1, 2)

        # Set stretch factors for better control of layout size
        container_layout.setRowStretch(0, 7)
        container_layout.setRowStretch(1, 2)
        container_layout.setColumnStretch(0, 1)
        container_layout.setColumnStretch(1, 3)
        
        # Set layout for container_widget
        self.container_widget.setLayout(container_layout)

    def connect_signals(self):
        self.bot_list_widget.itemClicked.connect(self.select_bot_sequence)
        self.play_button_widget.toggled.connect(self.toggle_action)
        self.finished_signal.connect(self.on_training_finished)  # Connect the signal
        cfg.themeChanged.connect(self.__onThemeChanged)

    def apply_styles(self):
        """ set style sheet """
        theme = 'dark' if isDarkTheme() else 'light'
        qss_path = str(resources.files('gui.resources.qss') / theme / 'bot_interface.qss')
        with open(qss_path, encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def _setup_bot_list_widget(self):
        self.bot_list_widget.setFrameStyle(QFrame.Box | QFrame.Plain)
        self.bot_list_widget.setLineWidth(2)
        self.bot_list_widget.setStyleSheet("""
            QListWidget {
                border: 1px solid rgba(255, 255, 255, 13);
                border-radius: 5px;
                background-color: transparent;
            }
        """)

    def _populate_bot_list(self):
        # Find all functions with the 'sequence_name' attribute
        for name, method in Logic.__dict__.items():
            if callable(method) and hasattr(method, 'sequence_name'):
                sequence_name = getattr(method, 'sequence_name')
                sequence_summary = getattr(method, 'sequence_summary')
                sequence_video = str(resources.files('gui.resources.clips') / f'{sequence_name.replace(" ", "_").lower()}.mp4')
                item = QListWidgetItem(sequence_name)
                item.setText(sequence_name)
                bot_widget  = BotListItemWidget(sequence_name, sequence_summary, sequence_video,interface=self)
                
                item.setSizeHint(bot_widget.sizeHint())
                self.bot_list_widget.addItem(item)
                self.bot_list_widget.setItemWidget(item, bot_widget)

        # Select the first item in the bot_list_widget by default
        if self.bot_list_widget.count() > 0:
            self.bot_list_widget.setCurrentRow(0)
            # Manually trigger the itemClicked signal for the first item
            self.select_bot_sequence(self.bot_list_widget.item(0))

    def select_bot_sequence(self, item):
        """Handle the selection of a bot sequence."""
        sequence_name = item.text().replace(" ", "_").lower()  # Make sure this matches the actual function name format

        self.currently_active_function = getattr(self.logic, sequence_name, None)
        if self.currently_active_function is None:
            self.logger.error(f"No function found for {sequence_name}")
        else:
            self.logger.info(f"{sequence_name} selected and ready.")

        # Clear existing settings by removing widgets from personal_group layout
        self._clear_SettingCards(self.personal_group)

        GuiUtils.generate_Card_from_config(sequence_name, self.personal_group)

        for widget in self.personal_group.cardLayout._ExpandLayout__widgets:
            widget.setVisible(True)

        # self.video_player.video_path = str(importlib_resources.files('gui.resources.clips').joinpath(f'{sequence_name}.mp4'))

        # Refresh the layout to ensure it renders correctly
        self.personal_group.adjustSize()  # Adjust the size if the layout's appearance changes

    def _clear_SettingCards(self, settingCardGroup: SettingCardGroup):
        """Clear all setting cards from the group by directly accessing ExpandLayout's private list."""
        self.logger.debug("Number of items in personal_group layout before deleting: {}".format(len(self.personal_group.cardLayout._ExpandLayout__widgets)))

        widgets_list = settingCardGroup.cardLayout._ExpandLayout__widgets
        while widgets_list:
            widget = widgets_list.pop(0)
            if widget:
                widget.deleteLater()

        self.logger.debug("Number of items in personal_group layout after deleting: {}".format(len(self.personal_group.cardLayout._ExpandLayout__widgets)))

    def toggle_action(self, checked):
        if checked:
            self.play_button_widget.setText('Stop')

            current_item = self.bot_list_widget.currentItem()
            if current_item:
                sequence_name = current_item.text().replace(" ", "_").lower()
                self.logger.info(f"Starting training sequence: {sequence_name}")

                # Create the runnable and start it
                self.current_runnable = TrainingRunnable(self.logic, getattr(self.logic, sequence_name), self.finished_signal)
                self.current_runnable.logger.addHandler(self.text_edit_logger)
                self.thread_pool.start(self.current_runnable)
            else:
                self.logger.error("No bot sequence selected.")
                self.play_button_widget.setChecked(False)
                self.play_button_widget.setText('Start')
        else:
            self.play_button_widget.setText('Start')
            self.logger.info("Stopping the training sequence...")
            if self.current_runnable:
                self.current_runnable.stop()
                self.thread_pool.waitForDone()

    @pyqtSlot()
    def on_training_finished(self):
        self.play_button_widget.setChecked(False)
        self.play_button_widget.setText('Start')
        self.logger.info("Training sequence finished.")
        self.current_runnable = None

    def toggle_hotkey_action(self):
        """Simulate the press of the start/stop button when the hotkey is pressed."""
        self.play_button_widget.setChecked(not self.play_button_widget.isChecked())

    def closeEvent(self, event):
        keyboard.unhook_all_hotkeys()
        event.accept()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        
        # Dynamically re-adjust layout to maintain correct proportions
        self.main_layout.invalidate()
        self.vertical_layout.invalidate()

        # Adjust the stretch factors for the main layout
        self.main_layout.setStretch(0, 4)  # Use setStretch for QVBoxLayout
        self.main_layout.setStretch(1, 1)

        # Adjust the stretch factors for vertical layout (optional)
        self.vertical_layout.setStretch(0, 1)
        self.vertical_layout.setStretch(1, 1)

        # Ensure the overlay resizes correctly
        self.overlay.resizeEvent(event) 

    def show_overlay(self):
        """Show the dark overlay over the active window."""
        self.overlay.show_overlay()
        
    def hide_overlay(self):
        """Hide the dark overlay when the FlyoutWidget is closed."""
        self.overlay.hide()

    def __onThemeChanged(self, theme: Theme):
            """ theme changed slot """
            # change the theme of qfluentwidgets
            setTheme(theme)

            # chang the theme of setting interface
            self.apply_styles()
