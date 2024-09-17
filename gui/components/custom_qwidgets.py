import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QSizePolicy, QLabel, QGraphicsScene, QGraphicsView,
                             QGraphicsOpacityEffect, QFrame, QHBoxLayout,QDialog, QApplication)
from PyQt5.QtCore import QUrl, Qt, QPropertyAnimation, QRectF, QSizeF, QEvent
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QGraphicsVideoItem
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtSvg import QSvgRenderer 
from importlib import resources
from qfluentwidgets import (TransparentToolButton, TitleLabel,
                            BodyLabel, isDarkTheme)
from qfluentwidgets import FluentIcon as FIF

class VideoIconWidget(QWidget):
    def __init__(self, play_icon_path: str, pause_icon_path: str, parent: QWidget = None, scale: float = 0.1):
        super().__init__(parent)
        self.scale = scale  # Scale factor as a ratio of the parent's width

        # Load the play and pause icons using QSvgRenderer
        self.play_icon_renderer = QSvgRenderer(str(play_icon_path))
        self.pause_icon_renderer = QSvgRenderer(str(pause_icon_path))

        # Start with the play icon
        self.current_icon_renderer = self.play_icon_renderer

        # Set the widget's attributes to make it transparent
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_OpaquePaintEvent, False)
        self.setStyleSheet("background-color: transparent;")  # Ensure no background is drawn
        

    def toggle_icon(self, is_playing: bool):
        """Toggle between the play and pause icons based on the is_playing state."""
        if is_playing:
            self.current_icon_renderer = self.pause_icon_renderer
        else:
            self.current_icon_renderer = self.play_icon_renderer

        # Trigger a repaint to display the new icon
        self.update()

    def paintEvent(self, event):
        """This method is called when the widget needs to be repainted."""
        with QPainter(self) as painter:
            if self.current_icon_renderer.isValid():
                # Draw the icon without any background
                self.current_icon_renderer.render(painter, QRectF(0, 0, self.width(), self.height()))


    def resizeEvent(self, event):
        """Resize the icon based on the parent widget's size."""
        if self.parent():
            parent_width = self.parent().width()
            scaled_width = int(parent_width * self.scale)  # Cast to int
            scaled_height = int(scaled_width * (self.current_icon_renderer.defaultSize().height() /
                                                self.current_icon_renderer.defaultSize().width()))  # Cast to int
            self.setFixedSize(scaled_width, scaled_height)

class VideoPlayerWidget(QFrame):
    def __init__(self, video_path:str=None, autoplay: bool = False, autoreplay: bool = True):
        super().__init__()
        self.video_valid = False
        self.autoplay = autoplay
        self.autoreplay = autoreplay  # Add an autoreplay flag
        # Use importlib_resources to get paths to icons and video
        self.play_icon_path = str(resources.files('gui.resources.icons') / 'Play_white.svg')
        self.pause_icon_path = str(resources.files('gui.resources.icons') / 'Pause_white.svg')

        self.setStyleSheet("""
            QFrame {
                border-radius: 20px;  /* Rounded corners */
                background-color: black;  /* Background color behind video */
            }
        """)
        # Create label to display error messages
        self.error_label = QLabel(self)
        self.error_label.setStyleSheet("color: white; font-size: 20px;")
        # self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setVisible(False)  # Initially hidden


        # Create QGraphicsScene and QGraphicsView for video and icon layering
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)
        self.view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Ensure view expands
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setAlignment(Qt.AlignCenter)  # Automatically center content
        self.view.setTransformationAnchor(QGraphicsView.AnchorViewCenter)

        # Set up media player and QGraphicsVideoItem for video rendering
        self.media_player = QMediaPlayer(None)
        self.video_item = QGraphicsVideoItem()
        self.video_item.setAspectRatioMode(Qt.KeepAspectRatio) 
        self.scene.addItem(self.video_item)
        self.media_player.setVideoOutput(self.video_item)

        # Create the IconWidget to display play/pause icons
        self.icon_widget = VideoIconWidget(self.play_icon_path, self.pause_icon_path, parent=self, scale=0.1)

        # Set layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.view)
        self.setLayout(layout)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Connect media player signals to update play/pause icon
        self.media_player.stateChanged.connect(self.handle_media_state)
        # Connect the media status signal to a custom slot
        self.media_player.mediaStatusChanged.connect(self.check_for_autoreplay)

        # # Animation for fading the icon in and out
        self.icon_effect = QGraphicsOpacityEffect()
        self.icon_widget.setGraphicsEffect(self.icon_effect)
        self.fade_animation = QPropertyAnimation(self.icon_effect, b"opacity")
        self.fade_animation.setDuration(2000)
        self.fade_animation.setStartValue(1)
        self.fade_animation.setEndValue(0)

        # Initially hide the icon
        self.icon_widget.setVisible(False)

        # Enable mouse tracking to receive enterEvent and leaveEvent
        self.setMouseTracking(True)
        self.view.setMouseTracking(True)

        self._video_path = None
        self.video_path = video_path

    def setVideoPath(self,video_path):
        self._video_path = video_path


    def handle_media_state(self, state):
        """Update the play/pause icon, but don't control visibility here."""
        if state == QMediaPlayer.PlayingState:
            self.icon_widget.toggle_icon(True)  # Show pause icon when playing
        else:
            self.icon_widget.toggle_icon(False)  # Show play icon when paused

    def check_for_autoreplay(self, status):
        """Check if the video has ended and replay if autoreplay is enabled."""
        if status == QMediaPlayer.EndOfMedia and self.autoreplay:
            self.media_player.setPosition(0)  # Reset to the beginning
            self.media_player.play()  # Start playing again

    def mousePressEvent(self, event):
        """Handle mouse clicks on the video widget to toggle play/pause."""
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

    def show_icon(self):
        """Fade in the play/pause icon."""
        self.fade_animation.stop()  # Stop any ongoing animation
        self.icon_widget.setVisible(True)
        self.icon_effect.setOpacity(1.0)
        self.icon_widget.raise_()  # Ensure it's on top of the video widget

    def hide_icon(self):
        """Fade out the play/pause icon slowly by becoming transparent."""
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.fade_animation.stop()  # Stop any ongoing animation
            self.fade_animation.start()
            self.fade_animation.finished.connect(lambda: self.icon_widget.setVisible(False))

    def resizeEvent(self, event):
        self.error_label.adjustSize()
        # Center the label manually in the view
        self.error_label.move(
            (self.width() - self.error_label.width()) // 2,
            (self.height() - self.error_label.height()) // 2
        )
        self.error_label.raise_()
        # Manually position the icon in the center of the video
        self.icon_widget.move(
            (self.width() - self.icon_widget.width()) // 2,
            (self.height() - self.icon_widget.height()) // 2
        )
        self.icon_widget.resizeEvent(event)  # Ensure the icon is resized appropriately
        if self.video_item:
            self.video_item.setSize(QSizeF(self.view.size()))  # Resize video to fit view
        super().resizeEvent(event)

    def enterEvent(self, event):
        """Show the icon only if the video is valid."""
        if self.video_valid:  # Only show icon if video is valid
            self.show_icon()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Hide the icon when the mouse leaves the VideoPlayerWidget."""
        if self.video_valid:  # Only hide if the icon was shown
            self.hide_icon()
        super().leaveEvent(event)

    # Getter for 'video_path'
    @property
    def video_path(self):
        return self._video_path

    # Setter for 'video_path'
    @video_path.setter
    def video_path(self, value):
        if value is None or isinstance(value, str):  # Allow None or strings
            self._video_path = value

            if not value:  # If video_path is None or empty
                self.error_label.setText("Video file path not defined")
                # self.error_label.adjustSize()
                self.error_label.setVisible(True)
                self.icon_widget.setVisible(False)  # Hide play/pause icon
                self.video_valid = False  # Set flag to false
                self.media_player.setMedia(QMediaContent())  # Pass an empty QMediaContent
            elif not os.path.exists(value):  # If video file doesn't exist
                self.error_label.setText("Video file not found")
                # self.error_label.adjustSize()
                self.error_label.setVisible(True)
                self.icon_widget.setVisible(False)  # Hide play/pause icon
                self.video_valid = False  # Set flag to false
                self.media_player.setMedia(QMediaContent())  # Pass an empty QMediaContent
            else:
                self.error_label.setVisible(False)  # Hide error label
                self.icon_widget.setVisible(True)  # Show play/pause icon
                self.video_valid = True  # Set flag to true
                self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(value)))
                if self.autoplay:  # Check if autoplay is True
                    self.media_player.play()  # Start playing video automatically
        else:
            raise ValueError("video_path must be a string.")

class BotListItemWidget(QWidget):
    def __init__(self, bot_name, bot_summary="",bot_video_path = "", parent=None, interface=None):
        super().__init__(parent)
        self.bot_name=bot_name
        self.bot_summary=bot_summary
        self.bot_video_path=bot_video_path
        self.interface = interface
        # self.flyout = CustomFlyoutBotSummary(parent, self.bot_name, self.bot_summary, self.bot_video_path)

        self.overlay = DarkOverlay(self)
        self.overlay.hide()

        # Create a layout for the custom list item widget
        layout = QHBoxLayout(self)

        # Add a spacer to push the button to the right
        layout.addStretch()

        # "About" button
        self.about_button = TransparentToolButton(FIF.INFO, self)
        layout.addWidget(self.about_button)

        # Connect the button click to show the bot summary
        self.about_button.clicked.connect(lambda: self.show_summary())

        self.setLayout(layout)

    def show_summary(self):
        """Display a summary for the bot."""
        # flyout = CustomFlyoutBotSummary(parent=self, bot_name=self.bot_name, bot_summary=self.bot_summary, bot_video_path=self.bot_video_path)
        # Flyout.make(flyout, self.about_button, self, aniType=FlyoutAnimationType.DROP_DOWN)
        if self.interface:
            self.interface.show_overlay()
        
        self.flyout = FlyoutWidget(parent=self.interface, bot_name=self.bot_name, bot_summary=self.bot_summary, bot_video_path=self.bot_video_path)
        # Position the flyout relative to the main window
        self.flyout.centerInParent()
        self.flyout.show()
        self.flyout.finished.connect(self.interface.hide_overlay)
    
class FlyoutWidget(QDialog):
    def __init__(self, parent=None,bot_name="",bot_summary="", bot_video_path=""):
        super(FlyoutWidget, self).__init__(parent)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog | Qt.WindowStaysOnTopHint)
        # self.setWindowModality(Qt.NonModal)  # Allows interaction with the main window

        self.setFixedSize(800, 500)

        # Dynamically set the background and border colors
        background_color = self.backgroundColor().name()
        
        self.setStyleSheet(f"""
            background-color: {background_color};
        """)

        layout = QVBoxLayout()

        # Add widgets to the flyout
        bot_name = TitleLabel(bot_name)
        
        bot_summary = BodyLabel(bot_summary)
        bot_summary.setWordWrap(True)
        bot_summary.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        bot_summary.adjustSize()

        video_player = VideoPlayerWidget(bot_video_path,autoplay=True)
        layout.addWidget(bot_name)
        layout.addWidget(bot_summary)
        layout.addWidget(video_player)
        self.setLayout(layout)
        self.installEventFilter(self)

    def backgroundColor(self):
        return QColor(40, 40, 40) if isDarkTheme() else QColor(248, 248, 248)

    def borderColor(self):
        return QColor(0, 0, 0, 45) if isDarkTheme() else QColor(0, 0, 0, 17)
    
    # Event filter to detect when the flyout loses focus or when a click happens outside
    def eventFilter(self, obj, event):
        if event.type() == QEvent.WindowDeactivate or event.type() == QEvent.FocusOut:
            self.close()  # Close the flyout when it loses focus
        return super(FlyoutWidget, self).eventFilter(obj, event)
    
    
    def centerInParent(self):
        if self.parent() is not None:
            # Get the parent widget's geometry
            parent_geometry = self.parent().frameGeometry()

            # Calculate the center position relative to the parent widget
            parent_center = self.parent().mapToGlobal(parent_geometry.center())

            # Calculate the top-left position for the flyout to be centered in the parent
            new_x = parent_center.x() - (self.width() // 2)
            new_y = parent_center.y() - (self.height() // 2)

            # Move the flyout to the calculated position
            self.move(new_x, new_y)

        else:
            # If there is no parent, default to centering in the screen
            screen_center = QApplication.activeWindow().geometry().center()
            self.move(screen_center.x() - (self.width() // 2), screen_center.y() - (self.height() // 2))

class DarkOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_NoMousePropagation, True)

        # Make the overlay dark and semi-transparent
        self.setStyleSheet("background-color: transparent;")  # Dark with 60% opacity
        self.hide()  # Initially hidden

    def show_overlay(self):
        """Show the overlay and adjust its size to cover the entire parent window."""
        if self.parent():
            # Use the parent's geometry and map it globally to cover the correct area
            parent_geo = self.parent().frameGeometry()
            global_pos = self.parent().mapToGlobal(parent_geo.topLeft())
            self.setGeometry(global_pos.x(), global_pos.y(), parent_geo.width(), parent_geo.height())
            self.raise_()  # Ensure it's brought to the front
            self.show()

    def hide_overlay(self):
        """Hide the overlay."""
        self.hide()

    def resizeEvent(self, event):
        """Ensure the overlay covers the entire parent window when resized."""
        if self.parent():
            parent_geo = self.parent().frameGeometry()
            global_pos = self.parent().mapToGlobal(parent_geo.topLeft())
            self.setGeometry(global_pos.x(), global_pos.y(), parent_geo.width(), parent_geo.height())
        super().resizeEvent(event)

    def paintEvent(self, event):
        """Manually draw the semi-transparent background."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(0, 0, 0, 150))  # Set the semi-transparent color (60% opacity)
        painter.setPen(Qt.NoPen)  # No border
        painter.drawRect(self.rect())  # Draw a filled rectangle covering the whole widget

