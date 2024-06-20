from main import add_margin, polycut, load_locations
import unittest
from PIL import Image
import os
import json

class TestImageProcessing(unittest.TestCase):

    def setUp(self):
        """Setup a mock image for testing."""
        self.image = Image.new("RGBA", (100, 100), (255, 0, 0, 0))

        # Create a temporary locations.json file for testing
        self.test_locations = {
            "TestLocation": "123 Test St, Test City",
            "TestCoordinates": [10.0, 20.0]
        }
        with open('test_locations.json', 'w') as f:
            json.dump(self.test_locations, f)

        # Ensure the output directory exists
        self.output_dir = 'output'
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def test_add_margin(self):
        """Test the add_margin function."""
        result = add_margin(self.image, 10, 10, 10, 10, (255, 255, 255))
        self.assertEqual(result.size, (120, 120))

    def test_polycut(self):
        """Test the polycut function."""
        # Create a mock image and save it to test polycut function
        self.image.save(os.path.join(self.output_dir, "test.png"))
        polycut("test", self.output_dir)
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "test_hex.png")))
        os.remove(os.path.join(self.output_dir, "test_hex.png"))

    def test_load_locations(self):
        """Test the load_locations function."""
        locations = load_locations('test_locations.json')
        expected_locations = {
            "TestLocation": "123 Test St, Test City",
            "TestCoordinates": (10.0, 20.0)
        }
        self.assertEqual(locations, expected_locations)

    def tearDown(self):
        """Clean up after tests."""
        if os.path.exists(os.path.join(self.output_dir, "test.png")):
            os.remove(os.path.join(self.output_dir, "test.png"))
        if os.path.exists('test_locations.json'):
            os.remove('test_locations.json')

if __name__ == '__main__':
    unittest.main()
