import cv2
from core.image_processing import ImageProcessing  # Import the static class
from config.config import cfg
from pathlib import Path
import pytest
import os

# def test_tesseract_env():
#     print("TESSDATA_PREFIX:", os.getenv('TESSDATA_PREFIX'))
#     assert os.getenv('TESSDATA_PREFIX') is not None

@pytest.fixture(scope="module")
def assets_path():
    """Define the base path to the assets directory."""
    base_path = Path(__file__).parent / 'assets'
    return base_path

@pytest.fixture(scope="module")
def img_paths(assets_path):
    """Define paths to the image files."""
    return {
        'healthbar_99': assets_path / 'healthbar_99.png',
        'healthbar_75': assets_path / 'healthbar_75.png',
        'healthbar_50': assets_path / 'healthbar_50.png',
        'healthbar_25': assets_path / 'healthbar_25.png',
        'menu_open': assets_path / 'menu_open.png',
        'fav1': assets_path / 'fav1.png',
        'fav2': assets_path / 'fav2.png',
        'fav3': assets_path / 'fav3.png',
        'fav4': assets_path / 'fav4.png',
        'fav5': assets_path / 'fav5.png',
        'fav_left': assets_path / 'fav_left.png',
        'fav_right': assets_path / 'fav_right.png',
        'fav_both': assets_path / 'fav_both.png'
    }

def load_image(img_path):
    """Utility function to load an image and ensure it exists."""
    image = cv2.imread(str(img_path))
    assert image is not None, f"Failed to load image {img_path}"
    return image

@pytest.mark.parametrize("img_key,expected_percentage", [
    ('healthbar_99', 99),
    ('healthbar_75', 75),
    ('healthbar_50', 50),
    ('healthbar_25', 25)
])
def test_analyze_health(img_paths, img_key, expected_percentage):
    health_image = ImageProcessing.crop_image(
        load_image(img_paths[img_key]), cfg.general_region_healtbar.value
    )
    health_percentage = ImageProcessing.analyze_health(health_image)
    assert round(health_percentage, 2) == pytest.approx(expected_percentage, abs=4.0)

def test_analyze_menu(img_paths):
    img = ImageProcessing.crop_image(
        load_image(img_paths['menu_open']), cfg.general_region_menu.value
    )
    extracted_text = ImageProcessing.analyze_menu(img).lower()
    assert "quests" in extracted_text

@pytest.mark.parametrize("img_key,expected_selection", [
    ('fav1', "elven bow of shocks"),
    ('fav2', "elven dagger (2)"),
    ('fav3', "healing"),
    ('fav4', "muffle"),
    ('fav5', "elven boots of eminent sneaking")
])
def test_analyze_favorite_name(img_paths, img_key, expected_selection):
    img = ImageProcessing.crop_image(
        load_image(img_paths[img_key]), cfg.general_region_favselect.value
    )
    favorite_selection = ImageProcessing.analyze_favorite_name(img)
    assert favorite_selection == expected_selection

@pytest.mark.parametrize("img_key,expected_selection", [
    ('fav_left', "l"),
    ('fav_right', "r"),
    ('fav_both', "lr")
])
def test_analyze_favorite_equip(img_paths, img_key, expected_selection):
    favorite_selection = ImageProcessing.analyze_favorite_equip(str(img_paths[img_key]))
    assert favorite_selection == expected_selection
