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

links = [
    'https://img.buzzfeed.com/buzzfeed-static/static/2022-03/5/0/asset/6201713e5c7e/sub-buzz-1009-1646440684-8.jpg',
    'https://hungrybynature.com/wp-content/uploads/2017/09/pinch-of-yum/workshop-19.jpg',
    'https://img.hellofresh.com/f_auto,fl_lossy,q_auto,w_1200/hellofresh_s3/image/tex-mex-turkey-rice-tacos-ac3c8368.jpg'
]

detected_foods = [
    ['rice', 'chicken', 'meat', 'fried rice'],
    ['berry', 'pancake', 'honey', 'blueberry'],
    ['meat', 'chicken', 'tacos', 'tomato', 'corn', 'salsa', 'beef']
]

def test_food_detection_with_valid_image():
    """
    Test food detection with a valid image containing food.
    """
    for i in range(3):
        detector = FoodDetector()
        result = detector.detect_food(links[i])
        assert result[0] == 'Success'  # This is the list of detected foods
        print(result[1])
        expected_food = detected_foods[i]
        print(expected_food)
        assert sorted(result[1]) == sorted(expected_food)
