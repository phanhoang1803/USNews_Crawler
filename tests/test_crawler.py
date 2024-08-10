# tests/test_crawler.py
import unittest
from src.crawler import crawl_news

class TestCrawler(unittest.TestCase):

    def test_crawl_news(self):
        self.assertIsNone(crawl_news())

if __name__ == "__main__":
    unittest.main()
