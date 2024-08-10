import logging
import yaml
import sqlite3
import json
import os
from crawler import crawl_news

# Load configuration
with open('../config/config.yaml', 'r') as file:
    config = yaml.safe_load(file)

with open('../config/logging_config.yaml', 'r') as file:
    logging_config = yaml.safe_load(file)
    
logging.config.dictConfig(logging_config)
logger = logging.getLogger('updater')

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('../data/news_articles.db')
cursor = conn.cursor()

# Ensure the URLs table exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS urls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE,
        crawled INTEGER DEFAULT 0
    )
''')
conn.commit()

def update_urls_from_json():
    json_dir = config['json_updater']['json_dir']
    for filename in os.listdir(json_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(json_dir, filename)
            logger.info(f"Processing JSON file: {filepath}")
            with open(filepath, 'r') as file:
                urls = json.load(file)
                for url in urls:
                    cursor.execute('INSERT OR IGNORE INTO urls (url) VALUES (?)', (url,))
            logger.info(f"Completed processing of {filepath}")
            # Optionally, move the processed JSON file to a backup directory
            # os.rename(filepath, os.path.join(json_dir, 'processed', filename))
    conn.commit()

if __name__ == "__main__":
    try:
        update_urls_from_json()
        crawl_news(logger=logger)
        logger.info("URL update from JSON files completed.")
    finally:
        conn.close()
