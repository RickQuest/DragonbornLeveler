import pyautogui
import time
import keyboard
import logging
from core.exceptions import *
from core.image_processing import ImageProcessing
from core.utils import Utils
from config.config import cfg, HandSelection


def add_attributes(**attrs):
    def decorator(func):
        for key, value in attrs.items():
            setattr(func, key, value)
        return func
    return decorator

class Logic:
    def __init__(self):
        # Configure the logging
        self.logger = logging.getLogger(self.__class__.__name__)  # Get a logger for this class
        # ImageProcessing = ImageProcessing()
        self.current_thread = None

    @add_attributes(sequence_name="Train Illusion")
    @add_attributes(sequence_summary="This bot will automatically select the \'Muffle\' spell from your favorites (make sure to add it beforehand), cast it with the chosen hand, and then sleep for 1 hour to regenerate Magicka. If the 'Bed' parameter is enabled, you'll need to aim at a bed before starting the bot, allowing it to interact with it and sleep.")
    def train_illusion(self):
        """
        Trains the Illusion skill by repeatedly casting a spell and sleeping for an hour in-game.

        :param repeat_times: The number of cycles to repeat.
        :param hand: The hand(s) to use for casting the spell. Options are HandSelection.LEFT, HandSelection.RIGHT, or HandSelection.BOTH.
        :param bed: Boolean indicating whether to use a bed for sleeping. Default is None.
        """
        repeat_times = cfg.illusion_repeat_time.value
        hand = cfg.illusion_hand.value
        bed = cfg.illusion_bed.value

        self.logger.info("Starting illusion training")

        if not Utils.focus_window(cfg.general_window_name.value):
            self.logger.error("Failed to focus window. Stopping illusion training.")
            return False  # Stop the bot sequence
        if not self.equip_favorite('muffle',hand):
            self.logger.error("Failed to equip favorite. Stopping illusion training.")
            return False  # Stop the bot sequence

        try:
            for i in range(repeat_times):
                if not self.current_thread._is_running:
                    self.logger.info("Stopping illusion training early.")
                    return False

                self.logger.info(f"Cycle {i+1} of {repeat_times}")

                # Cast the Illusion spell
                self.perform_action(hand=hand, delay=1)
                time.sleep(1)

                # Sleep for an hour in-game
                self.go_sleep_or_wait(bed=bed, check_menu=False)

                # Add a short delay between cycles to avoid potential issues
                time.sleep(1)

            self.logger.info("Illusion training completed.")
            return True  # Indicate that the training was successful

        except Exception as e:
            self.logger.exception("An unexpected error occurred while illusion training.")
            return False

    @add_attributes(sequence_name="Train Conjuration")
    @add_attributes(sequence_summary="This bot will automatically select the \'Soul Trap\' spell from your favorites (be sure to add it beforehand), cast it on a targeted corpse, and then sleep for 1 hour to regenerate Magicka. Before activating the bot, ensure you are aiming at the desired corpse."
)
    def train_conjuration(self):
        """
        Trains the Conjuration skill by repeatedly casting a spell and sleeping for an hour in-game.

        :param repeat_times: The number of cycles to repeat.
        :param hand: The hand(s) to use for casting the spell. Options are HandSelection.LEFT, HandSelection.RIGHT, or HandSelection.BOTH.
        :param bed: Boolean indicating whether to use a bed for sleeping. Default is None.
        """
        repeat_times = cfg.conjuration_repeat_time.value
        hand = cfg.conjuration_hand.value

        self.logger.info("Starting Conjuration training")

        if not Utils.focus_window(cfg.general_window_name.value):
            self.logger.error("Failed to focus window. Stopping Conjuration training.")
            return False  # Stop the bot sequence
        if not self.equip_favorite('soul trap',hand):
            self.logger.error("Failed to equip favorite. Stopping Conjuration training.")
            return False  # Stop the bot sequence

        try:
            for i in range(repeat_times):
                if not self.current_thread._is_running:
                    self.logger.info("Stopping Conjuration training early.")
                    return False

                self.logger.info(f"Cycle {i+1} of {repeat_times}")

                # Cast the Illusion spell
                self.perform_action(hand=hand, delay=1)
                time.sleep(1)

                # Sleep for an hour in-game
                self.go_sleep_or_wait(check_menu=False)

                # Add a short delay between cycles to avoid potential issues
                time.sleep(1)

            self.logger.info("Conjuration training completed.")
            return True  # Indicate that the training was successful

        except Exception as e:
            self.logger.exception("An unexpected error occurred while Conjuration training.")
            return False

    @add_attributes(sequence_name="Train Armor")
    @add_attributes(sequence_summary="This bot will automatically select the specified healing spell from your favorites (be sure to add it beforehand) and cast it to restore your health while you’re under attack. Before activating the bot, make sure you're engaged in combat to take damage, which will help increase your armor skill. Additionally, ensure you're equipped with either light or heavy armor, depending on which skill you want to level up."
)
    def train_armor(self):
        """
        Trains the Armor skill by repeatedly taking damage and healing when health is low.
        Stops the training and opens the menu if health is critically low (below 25%).
        Stops automatically when the training timer reaches the configured duration.
        """
        self.logger.info("Starting armor training")

        if not Utils.focus_window(cfg.general_window_name.value):
            self.logger.error("Failed to focus window. Stopping armor training.")
            return False  # Stop the bot sequence

        # Use the healing spell directly from the config, which is now of type HealingSpell
        healing_spell = cfg.armor_healing_skill.value.name.lower().replace('_', ' ')
        delay = cfg.armor_healing_skill.value.value  # Get the delay directly from the enum
        self.logger.debug(f"Searching healing spell: {healing_spell} in favorite")


        if not self.equip_favorite(healing_spell, cfg.armor_hand.value):
            self.logger.error(f"Failed to equip healing spell: {healing_spell}. Stopping armor training.")
            return False  # Stop the bot sequence

        start_time = time.time()
        training_duration = cfg.armor_train_time.value * 60  # Convert minutes to seconds

        try:
            while self.current_thread._is_running:
                elapsed_time = time.time() - start_time

                if elapsed_time >= training_duration:
                    self.logger.info(f"Training duration of {cfg.armor_train_time.value} minutes reached. Stopping armor training.")
                    break

                # Check the current health status
                health_percentage = self.check_health()

                self.logger.info(f"Current health: {health_percentage}%")

                if health_percentage < 75:
                    self.logger.info("Health is below 50%, starting to heal.")

                    # Keep healing until health is above 90%
                    while health_percentage < 90 and self.current_thread._is_running:
                        self.perform_action(hand=cfg.armor_hand.value, delay=delay)  # Use the delay from the enum
                        # time.sleep(delay)  # Wait for the healing to take effect

                        health_percentage = self.check_health()  # Recheck health after healing
                        self.logger.info(f"Health after healing: {health_percentage}%")
                        # Check if health is critically low
                        if health_percentage < 30:
                            self.logger.error("Health is critically low (below 25%). Stopping armor training.")
                            return False  # Stop the bot sequence

                # Add a short delay to simulate time passing and avoid spamming the check
                time.sleep(0.5)

            self.logger.info("Armor training completed.")
            return True  # Indicate that the training was successful

        except Exception as e:
            self.logger.exception("An unexpected error occurred while armor training.")
            return False

    def perform_action(self, hand: HandSelection = HandSelection.RIGHT, delay: float = 1.0):
        """
        Simulates casting a spell or attacking with the specified hand(s).

        :param hand: The hand(s) to use for the action. Options are HandSelection.LEFT, HandSelection.RIGHT, or HandSelection.BOTH.
        :param delay: The amount of time (in seconds) to hold down the mouse button for the action.
        """
        # self.logger.debug("Perform action with {} hand".format(hand))

        try:
            if hand == HandSelection.BOTH:
                self.logger.debug("Casting with both hands simultaneously.")
                # Simulate pressing both mouse buttons for dual casting
                pyautogui.mouseDown(button='left')
                pyautogui.mouseDown(button='right')
                time.sleep(delay)
                pyautogui.mouseUp(button='left')
                pyautogui.mouseUp(button='right')
            elif hand == HandSelection.LEFT:
                self.logger.debug("Casting with left hand.")
                pyautogui.mouseDown(button='left')
                time.sleep(delay)
                pyautogui.mouseUp(button='left')
            elif hand == HandSelection.RIGHT:
                self.logger.debug("Casting with right hand.")
                pyautogui.mouseDown(button='right')
                time.sleep(delay)
                pyautogui.mouseUp(button='right')
            else:
                self.logger.error(f"Invalid hand selection: {hand}")

        except Exception as e:
            self.logger.exception(f"An error occurred while performing the action: {e}")
            raise

    def go_sleep_or_wait(self, bed: bool = None, sleep_time: int = 1,check_menu: bool = True):
        """
        Simulates the process of going to sleep or waiting for a specified amount of time in Skyrim.

        :param bed: If True, interact with a bed using the 'e' key; if False, wait using the 't' key.
        :param sleep_time: The amount of time (in hours) to sleep or wait. Default is 1 hour.
        :param check_menu: If True, check if any menu is open and close it before proceeding.
        """

        if check_menu:
            # Close any open menu if the check_menu flag is True
            self.close_menu_if_open()

        if bed:
            # Interact with a bed (default key 'E')
            keyboard.press_and_release('e')
        else:
            # Open the wait menu (default key 'T')
            keyboard.press_and_release('t')

        # Wait for the menu to open
        time.sleep(1)

        # Set the sleep or wait time
        if sleep_time > 1:
            # Scroll down to increase the time if necessary (default key 'Down Arrow')
            for _ in range(sleep_time - 1):
                keyboard.press_and_release('d')  # 's' is often mapped to 'Down Arrow'
                time.sleep(0.2)  # Short delay between key presses

        # Press Enter to confirm sleeping or waiting for the specified time
        keyboard.press_and_release('enter')

        # Wait for the time to pass and the game to return to normal
        time.sleep(2)

    def quicksave_and_quit_game(self):
        """
        Simulates the process of quicksaving and quitting the game in Skyrim.
        """
        self.close_menu_if_open()

        self.quicksave()

        # Open the system menu (default key 'Esc')
        keyboard.press_and_release('esc')
        time.sleep(2)  # Wait for the menu to open

        # Click on the 'System' icon at coordinates (1357, 166)
        absolute_x, absolute_y = Utils.relative_to_absolute_coords(1357, 106)
        pyautogui.click(absolute_x, absolute_y)
        time.sleep(1)  # Short delay to ensure the click is registered

        # Navigate to 'Quit menu'
        for _ in range(3):
            keyboard.press_and_release('a')
            time.sleep(0.2)  # Short delay between key presses

        for _ in range(8):
            keyboard.press_and_release('s')
            time.sleep(0.2)  # Short delay between key presses

        # Press Enter
        keyboard.press_and_release('enter')
        time.sleep(0.5)  # Wait for the game to quit

        # Navigate to 'Quit Desktop' by pressing 'Down Arrow' 3 times
        for _ in range(3):
            keyboard.press_and_release('s')
            time.sleep(0.2)  # Short delay between key presses

        # Press Enter to select
        for _ in range(3):
            keyboard.press_and_release('enter')
            time.sleep(0.5)  # Short delay between key presses

    def quicksave(self):
        # Quicksave the game (default key 'F5')
        keyboard.press_and_release('f5')
        time.sleep(2)  # Wait for the quicksave to complete

    def check_health(self):
        """
        Check the current health percentage.
        """
        screenshot = ImageProcessing.screenshot(cfg.general_region_healtbar.value)
        health_percentage = ImageProcessing.analyze_health(screenshot)
        health_percentage = 100 if health_percentage == 0 else health_percentage
        print(health_percentage)
        return health_percentage

    def equip_favorite(self, favorite_name, hand: HandSelection = HandSelection.RIGHT):
        favorite_name = favorite_name.lower().replace('_', ' ')
        self.logger.info(f"Attempting to equip '{favorite_name}' in {hand.name} hand.")
        try:
            # Close any open menus before starting
            self.close_menu_if_open()

            # Open the favorites menu
            Utils.press_key_with_delay('q', 1)

            # Initialize variables
            favorite_found = False
            previous_text = ""
            steps_up = 0  # To track how many times we've moved up
            reached_top = False
            max_steps = 20  # Max steps to prevent infinite loops

            # Analyze menu while moving up
            while steps_up < max_steps:
                # Take a screenshot and analyze the text
                screenshot = ImageProcessing.screenshot(region=cfg.general_region_favselect.value)
                current_text = ImageProcessing.analyze_favorite_name(screenshot)

                if not current_text:
                    raise FavoriteTextNotFoundException('No text was found in the favorites menu.')

                self.logger.debug(f"Detected favorite text: {current_text.strip()}")

                # If the favorite is found, break out of the loop
                if favorite_name in current_text.lower():
                    favorite_found = True
                    break

                # Check if the text is the same as the last iteration (indicates we're at the top)
                if current_text == previous_text:
                    if not reached_top:
                        self.logger.info("Reached the top of the favorites menu. Going back to initial position.")
                        reached_top = True
                        for _ in range(steps_up):  # Go back to the initial position
                            Utils.press_key_with_delay('s', 0.2)
                    else:
                        self.logger.info("Reached the bottom of the favorites menu.")
                        raise FavoriteNotFoundException(favorite_name)
                else:
                    # Update previous text and move up
                    previous_text = current_text
                    if reached_top:
                        Utils.press_key_with_delay('s', 0.2)
                    else:
                        Utils.press_key_with_delay('w', 0.2)
                    steps_up += 1

            if not favorite_found:
                raise FavoriteNotFoundException(favorite_name)

            time.sleep(1)
            # Proceed with equipping the favorite based on hand selection if the favorite was found
            hand_state = self.detect_favorite_equipped()
            self.logger.debug(f"Current hand state: {hand_state.name}")

            # Equip the favorite based on the hand selection
            if hand == HandSelection.RIGHT:
                if hand_state in [HandSelection.RIGHT, HandSelection.BOTH]:
                    self.logger.info(f"{favorite_name} is already equipped in RIGHT hand, skipping re-equipping.")
                else:
                    self.logger.info(f"Equipping {favorite_name} in RIGHT hand.")
                    pyautogui.mouseDown(button='right')
                    time.sleep(0.1)
                    pyautogui.mouseUp(button='right')
                    time.sleep(1)

            elif hand == HandSelection.LEFT:
                if hand_state in [HandSelection.LEFT, HandSelection.BOTH]:
                    self.logger.info(f"{favorite_name} is already equipped in LEFT hand, skipping re-equipping.")
                else:
                    self.logger.info(f"Equipping {favorite_name} in LEFT hand.")
                    pyautogui.mouseDown(button='left')
                    time.sleep(0.1)
                    pyautogui.mouseUp(button='left')
                    time.sleep(1)

            elif hand == HandSelection.BOTH:
                if hand_state == HandSelection.BOTH:
                    self.logger.info(f"{favorite_name} is already equipped in BOTH hands, skipping re-equipping.")
                else:
                    if hand_state == HandSelection.LEFT:
                        self.logger.info(f"Right hand is free, equipping {favorite_name} in RIGHT hand.")
                        pyautogui.mouseDown(button='right')
                        time.sleep(0.1)
                        pyautogui.mouseUp(button='right')
                    elif hand_state == HandSelection.RIGHT:
                        self.logger.info(f"Left hand is free, equipping {favorite_name} in LEFT hand.")
                        pyautogui.mouseDown(button='left')
                        time.sleep(0.1)
                        pyautogui.mouseUp(button='left')
                    elif hand_state == HandSelection.NONE:
                        self.logger.info(f"Equipping {favorite_name} in BOTH hands.")
                        pyautogui.mouseDown(button='left')
                        pyautogui.mouseDown(button='right')
                        time.sleep(0.1)
                        pyautogui.mouseUp(button='left')
                        pyautogui.mouseUp(button='right')
                    time.sleep(1)

            return True

        except FavoriteNotFoundException as e:
            self.logger.exception(e)
            return False
        except FavoriteTextNotFoundException as e:
            self.logger.exception(e)
            return False
        except Exception as e:
            self.logger.exception("An unexpected error occurred while trying to equip the favorite.")
            return False
        finally:
            # Close the favorites menu
            Utils.press_key_with_delay('q', 1)

    def is_menu_open(self):
        """
        Detect if the menu is open.
        """
        # Capture a screenshot of the menu region
        screenshot = ImageProcessing.screenshot(region=cfg.general_region_menu.value)

        # Use OCR to extract text from the grayscale screenshot
        extracted_text = ImageProcessing.analyze_menu(screenshot)

        # Check if the word 'Quest' is in the extracted text
        if "quest" in extracted_text.lower():
            self.logger.info("Menu is open")
            return True
        else:
            self.logger.info("Menu is not open")
            return False

    def detect_favorite_equipped(self):
        """
        Detect which hand(s) the favorite is equipped in.
        :return: Enum value indicating 'l', 'r', 'lr', or 'none'.
        """
        try:
            # Capture the screenshot of the favorite equipment region
            screenshot = ImageProcessing.screenshot()

            # Analyze the screenshot to extract the relevant text
            equipped_state = ImageProcessing.analyze_favorite_equip(screenshot)
            self.logger.debug(f"Detected current favorite hand state text: {equipped_state}")
        except Exception as e:
            raise

        # Determine the hand state based on the extracted text
        if equipped_state == "l":
            return HandSelection.LEFT
        elif equipped_state == "r":
            return HandSelection.RIGHT
        elif equipped_state == "lr":
            return HandSelection.BOTH
        else:
            return HandSelection.NONE

    def open_menu(self):
        keyboard.press_and_release('esc')
        time.sleep(1)

    def close_menu_if_open(self):
        keyboard.press_and_release('esc')
        time.sleep(1)
        if self.is_menu_open():
            keyboard.press_and_release('esc')
            time.sleep(1)
