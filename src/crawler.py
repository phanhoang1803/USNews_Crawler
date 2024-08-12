import logging
import yaml
import sqlite3
from time import sleep
from utils import *

def prepare_database(db_path):
    # Load configuration
    with open('../config/config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    with open('../config/logging_config.yaml', 'r') as file:
        logging_config = yaml.safe_load(file)
        
    logging.config.dictConfig(logging_config)
    logger = logging.getLogger('crawler')

    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables for storing articles and URLs if they don't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            authors TEXT,
            published_date TEXT,
            description TEXT,
            text TEXT,
            url TEXT UNIQUE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            crawled INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    
    return conn, cursor, config, logger

if __name__ == "__main__":
    args = parse_arguments()
    conn, cursor, config, logger = prepare_database(args.db_path)
    try:
        while True:
            # Discover URLs from RSS feeds
            discover_urls_from_feeds(conn, cursor, config, logger)
            
            # Crawl discovered URLs
            crawl_news_once(conn, cursor, config, logger)
            
            logger.info(f"Sleeping for {config['crawler']['crawl_interval']} seconds")
            sleep(config['crawler']['crawl_interval'])
    finally:
        conn.close()
