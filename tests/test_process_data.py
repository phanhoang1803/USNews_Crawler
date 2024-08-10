# tests/test_process_data.py
import unittest
from src.process_data import process_article

class TestProcessData(unittest.TestCase):

    def test_process_article(self):
        article = {'title': 'Sample Title', 'text': 'Sample Text'}
        processed_article = process_article(article)
        self.assertEqual(processed_article['title'], 'sample title')
        self.assertEqual(processed_article['text'], 'sample text')

if __name__ == "__main__":
    unittest.main()
