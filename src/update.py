import logging
import yaml
import sqlite3
import json
import os
from utils import *

def prepare_database(db_path):
    # Load configuration
    with open('../config/config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    with open('../config/logging_config.yaml', 'r') as file:
        logging_config = yaml.safe_load(file)
        
    logging.config.dictConfig(logging_config)
    logger = logging.getLogger('updater')

    # Connect to SQLite database (or create it if it doesn't exist)
    conn = connect_db(db_path, logger)
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
    
    return conn, cursor, config, logger

if __name__ == "__main__":
    args = parse_arguments()
    conn, cursor, config, logger = prepare_database(args.db_path)
    
    try:
        # discover_urls_from_feeds(conn, cursor, config, logger)
        # update_urls_from_json(conn, cursor, config, logger)
        # crawl_news(conn, cursor, config, logger)
        crawl_news_once(conn, cursor, config, logger)
        
        logger.info("URL update from JSON files completed.")
    finally:
        conn.close()
