# tests/test_update.py
import unittest
from src.update import update_data

class TestUpdate(unittest.TestCase):

    def test_update_data(self):
        self.assertIsNone(update_data())

if __name__ == "__main__":
    unittest.main()
