import logging
import yaml
import sqlite3
import feedparser
from time import sleep
from newsplease import NewsPlease

# Load configuration
with open('../config/config.yaml', 'r') as file:
    config = yaml.safe_load(file)

with open('../config/logging_config.yaml', 'r') as file:
    logging_config = yaml.safe_load(file)
    
logging.config.dictConfig(logging_config)
logger = logging.getLogger('crawler')

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('../data/news_articles.db')
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

def discover_urls_from_feeds():
    for source, feeds in config['crawler']['feeds'].items():
        for feed_url in feeds:
            logger.info(f"Fetching feed: {feed_url}")
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                article_url = entry.link
                # Insert new URL into the database if not already present
                cursor.execute('INSERT OR IGNORE INTO urls (url) VALUES (?)', (article_url,))
    conn.commit()

def crawl_news(logger=logger):
    cursor.execute('SELECT url FROM urls WHERE crawled = 0')
    urls = cursor.fetchall()
    
    logger.info(f"Found {len(urls)} URLs to crawl")
    for i, (url,) in enumerate(urls):
        logger.info(f"{i + 1}. Starting crawl for: {url}")

        article = NewsPlease.from_url(url, timeout=config['crawler']['timeout'])
        save_article(article, url, logger)
        
        # Mark URL as crawled
        # cursor.execute('UPDATE urls SET crawled = 1 WHERE url = ?', (url,))
    conn.commit()

def save_article(article, url, logger=logger):
    if article:
        cursor.execute('''
            INSERT OR IGNORE INTO articles (title, authors, published_date, description, text, url)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            article.title,
            ', '.join(article.authors) if article.authors else None,
            article.date_publish,
            article.description,
            article.maintext,
            article.url
        ))
        cursor.execute('UPDATE urls SET crawled = 1 WHERE url = ?', (url,))
        conn.commit()
        logger.info(f"Saved article to database: {article.title}")
    else:
        logger.warning(f"Failed to save article to database: {article}")
        cursor.execute('UPDATE urls SET crawled = -1 WHERE url = ?', (url,))
        conn.commit()

if __name__ == "__main__":
    try:
        while True:
            # Discover URLs from RSS feeds
            discover_urls_from_feeds()
            
            # Crawl discovered URLs
            crawl_news()
            
            logger.info(f"Sleeping for {config['crawler']['crawl_interval']} seconds")
            sleep(config['crawler']['crawl_interval'])
    finally:
        conn.close()
