import pyautogui
import time
import ctypes
import pygetwindow as gw
from pywinauto import application
from pywinauto.findwindows import ElementNotFoundError, ElementAmbiguousError
import logging
from screeninfo import get_monitors
from core.exceptions import *
import keyboard

class Utils:
    logger = logging.getLogger('Utils')  # Static logger

    @staticmethod
    def relative_to_absolute_coords(x, y):
        """
        Convert coordinates relative to the active window to absolute coordinates in a multi-monitor setup.

        :param x: The x coordinate relative to the active window.
        :param y: The y coordinate relative to the active window.
        :return: The absolute x, y coordinates.
        """
        monitors = get_monitors()

        # Get the active window
        active_window = gw.getActiveWindow()

        if not active_window:
            raise Exception("No active window found.")

        # Determine which monitor the active window is on
        active_monitor = None
        for monitor in monitors:
            if (monitor.x <= active_window.left < monitor.x + monitor.width and
                monitor.y <= active_window.top < monitor.y + monitor.height):
                active_monitor = monitor
                break

        if not active_monitor:
            raise Exception("Active window is not on any known monitor.")

        # Calculate the absolute coordinates
        absolute_x = active_monitor.x + x
        absolute_y = active_monitor.y + y

        Utils.logger.debug(f"Absolute coordinates of system menu are x: {absolute_x}, y: {absolute_y}")

        return absolute_x, absolute_y

    @staticmethod
    def focus_window(window_title):
        """
        Brings a window with the given title to the foreground and focuses on it.
        """
        try:
            # Connect to the application with the specified window title
            app = application.Application().connect(title_re=window_title)
            window = app.window(title=window_title)
            app_dialog = app.top_window()

            if app_dialog.is_minimized():
                app_dialog.restore()

            app_dialog.set_focus()
            hwnd = app_dialog.handle
            ctypes.windll.user32.SetForegroundWindow(hwnd)
            Utils.logger.debug(f"Window '{window_title}' is now in focus.")
            return True

        except ElementNotFoundError:
            Utils.logger.error(f"No window found with the title: {window_title}")
            return False
        except ElementAmbiguousError:
            Utils.logger.error(f"Multiple windows found with the title: {window_title}")
            return False
        except Exception as e:
            Utils.logger.exception(f"An unexpected error occurred while focusing the window: {str(e)}")
            return False

    @staticmethod
    def press_key(key_code):
        """
        Press a key using the Windows API.
        :param key_code: The virtual-key code of the key to press.
        """
        ctypes.windll.user32.keybd_event(key_code, 0, 0, 0)  # Key down
        time.sleep(0.05)
        ctypes.windll.user32.keybd_event(key_code, 0, 2, 0)  # Key up

    @staticmethod
    def print_mouse_position():
        try:
            print("Press Ctrl+C to stop.")
            while True:
                # Get the current mouse position
                x, y = pyautogui.position()

                # Clear the previous output line and print the new position
                print(f"Mouse position: (X: {x}, Y: {y})", end='\r')

                # Sleep briefly to avoid overwhelming the console
                time.sleep(0.1)

        except KeyboardInterrupt:
            print("\nStopped.")

    @staticmethod
    def press_key_with_delay(key, delay=0.2):
        """
        Press a key using the keyboard module with a delay.
        """
        keyboard.press_and_release(key)
        time.sleep(delay)
