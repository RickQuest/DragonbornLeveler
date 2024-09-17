import pyautogui
import cv2
import pytesseract
import numpy as np
from PIL import Image
import logging
from tkinter.filedialog import asksaveasfilename
from tkinter import Tk
import time
from core.utils import Utils
from config.config import cfg
from pathlib import Path
from core.app_data_manager import app_data_manager
from importlib import resources
from pathlib import Path
import os

class ImageProcessing:
    logger = logging.getLogger('ImageProcessing')  # Static logger for the class
    assets_path = resources.files('core.assets')


    @staticmethod
    def screenshot(region=None):
        """
        Capture the health bar area of the screen.
        """
        try:
            Utils.focus_window(cfg.general_window_name.value)
            screenshot = pyautogui.screenshot(region=region)
            screenshot = np.array(screenshot)
            screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
            return screenshot

        except Exception as e:
            raise

    @staticmethod
    def crop_image(image, region):
        """
        Crop the image based on the specified region.

        :param image: The input image to be cropped (as a NumPy array).
        :param region: A tuple (x, y, width, height) specifying the region to crop.
        :return: The cropped image as a NumPy array.
        """
        x, y, w, h = region
        cropped_image = image[y:y+h, x:x+w]
        return cropped_image

    @staticmethod
    def display_and_save_image(image, window_name='Image', save_key='s'):
        """
        Display an image and open a file dialog to save it if the specified key is pressed.

        :param image: The image to display (as a NumPy array).
        :param window_name: The name of the window where the image is displayed.
        :param save_key: The key that, when pressed, will open a file dialog to save the image.
        """
        cv2.imshow(window_name, image)
        key = cv2.waitKey(0)

        if key == ord(save_key):
            Tk().withdraw()
            save_path = asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
            )
            if save_path:
                cv2.imwrite(save_path, image)
                print(f"Image saved as {save_path}")
            else:
                print("Save operation cancelled.")
        else:
            print("Image not saved.")

        cv2.destroyAllWindows()
        Utils.focus_window(cfg.general_window_name.value)
        time.sleep(1)

    @staticmethod
    def ocr_extract_text(image, config=None):
        """
        Extract text from an image using Tesseract OCR.
        :param image: The screenshot image to extract text from (as a PIL Image or NumPy array).
        :return: The extracted text as a string.
        """
        if isinstance(image, str):
            img = cv2.imread(image)
            if img is None:
                raise ValueError(f"Failed to load image at path: {image}")
        elif isinstance(image, np.ndarray):
            img = image
        elif isinstance(image, Image.Image):
            img = np.array(image)
        else:
            raise TypeError("screenshot must be a file path or an OpenCV image (numpy array)")

        if len(img.shape) == 3:
            gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray_image = img

        if config:
            text = pytesseract.image_to_string(gray_image, config=config)
        else:
            text = pytesseract.image_to_string(gray_image)

        if cfg.general_debug.value:
            ImageProcessing.logger.debug("Extracted Text: {}".format(text))

        return text

    @staticmethod
    def analyze_menu(img):
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh_img = cv2.threshold(gray_img, 150, 255, cv2.THRESH_BINARY_INV)
        thresh_img = cv2.resize(thresh_img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        extracted_text = ImageProcessing.ocr_extract_text(thresh_img)
        return extracted_text

    @staticmethod
    def analyze_health(img):
        if isinstance(img, str):
            img = cv2.imread(img)
            if img is None:
                raise ValueError(f"Failed to load image at path: {img}")
        elif isinstance(img, np.ndarray):
            img = img
        else:
            raise TypeError("screenshot must be a file path or an OpenCV image (numpy array)")

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_red = np.array([0, 70, 50])
        upper_red = np.array([10, 255, 255])
        mask1 = cv2.inRange(hsv, lower_red, upper_red)
        lower_red2 = np.array([170, 70, 50])
        upper_red2 = np.array([180, 255, 255])
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = mask1 | mask2

        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel)

        red_pixels = np.sum(mask == 255)
        total_pixels = mask.size
        health_percentage = (red_pixels / total_pixels) * 100

        if cfg.general_debug.value:
            debug_image_path = app_data_manager.get_file_path(str(Path('debug') / 'healtbar_redmask.png'))
            cv2.imwrite(debug_image_path, mask)

        return health_percentage

    @staticmethod
    def analyze_favorite_name(img):
        if isinstance(img, str):
            img = cv2.imread(img)
            if img is None:
                raise ValueError(f"Failed to load image at path: {img}")
        elif isinstance(img, np.ndarray):
            img = img
        else:
            raise TypeError("screenshot must be a file path or an OpenCV image (numpy array)")

        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh_img = cv2.threshold(gray_img, 150, 255, cv2.THRESH_BINARY_INV)
        thresh_img = cv2.resize(thresh_img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        extracted_text = ImageProcessing.ocr_extract_text(thresh_img)
        extracted_text = extracted_text.lower()
        translation_table = str.maketrans({
            "\n": "",
            "{": "(",
            "}": ")"
        })
        extracted_text = extracted_text.translate(translation_table)

        return extracted_text

    @staticmethod
    def analyze_favorite_equip(img):
        if isinstance(img, str):
            img = cv2.imread(img)
            if img is None:
                error_message = f"Failed to load image at path: {img}"
                ImageProcessing.logger.error(error_message)
                raise ValueError(error_message)
        elif not isinstance(img, np.ndarray):
            error_message = "screenshot must be a file path or an OpenCV image (numpy array)"
            ImageProcessing.logger.error(error_message)
            raise TypeError(error_message)

        ImageProcessing.logger.debug(f"Image resolution: {img.shape}")

        right_icon = cv2.imread(ImageProcessing.assets_path / 'fav_right_icon.png', cv2.IMREAD_GRAYSCALE)
        left_icon = cv2.imread(ImageProcessing.assets_path / 'fav_left_icon.png', cv2.IMREAD_GRAYSCALE)
        both_icon = cv2.imread(ImageProcessing.assets_path / 'fav_both_icon.png', cv2.IMREAD_GRAYSCALE)

        if right_icon is None or left_icon is None or both_icon is None:
            error_message = "Failed to load one or more favorite icon images."
            ImageProcessing.logger.error(error_message)
            raise ValueError(error_message)

        templates = [('r', right_icon), ('l', left_icon), ('lr', both_icon)]
        cropped_img1 = ImageProcessing.crop_image(img, cfg.general_region_favequip.value)
        result1 = ImageProcessing._match_templates(cropped_img1, templates)
        ImageProcessing.logger.debug(f"Confidence level of favorite equip state: {result1['confidence']}")

        if cfg.general_debug.value:
            debug_image_path = app_data_manager.get_file_path(str(Path('debug') / 'favequip_crop1.png'))
            cv2.imwrite(debug_image_path, cropped_img1)

        if result1['confidence'] >= 0.8:
            return result1['label']

        return ''

    @staticmethod
    def _match_templates(gray_img, templates):
        if len(gray_img.shape) == 3:
            gray_img = cv2.cvtColor(gray_img, cv2.COLOR_BGR2GRAY)

        best_match_label = None
        best_match_confidence = 0

        for label, template in templates:
            res = cv2.matchTemplate(gray_img, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

            if max_val > best_match_confidence:
                best_match_confidence = max_val
                best_match_label = label

        return {
            'label': best_match_label,
            'confidence': best_match_confidence
        }

