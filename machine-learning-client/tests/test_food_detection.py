"""
Test module for food detector functionality.
This module contains unit tests for the FoodDetector class.
"""

from food_detection import FoodDetector


def test_food_detector_initialization():
    """
    Test if FoodDetector can be properly initialized.
    """
    detector = FoodDetector()
    assert detector is not None


def test_food_detection_with_valid_image():
     """
     Test emotion detection with a valid image containing a face.
     """
     detector = FoodDetector()