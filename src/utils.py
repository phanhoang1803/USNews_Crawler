# src/utils.py
import argparse
import json
import os
import feedparser
from newsplease import NewsPlease
import requests

def discover_urls_from_feeds(conn, cursor, config, logger):
    for source, feeds in config['crawler']['feeds'].items():
        for feed_url in feeds:
            logger.info(f"Fetching feed: {feed_url}")
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                article_url = entry.link
                # Insert new URL into the database if not already present
                cursor.execute('INSERT OR IGNORE INTO urls (url) VALUES (?)', (article_url,))
    conn.commit()

def update_urls_from_json(conn, cursor, config, logger):
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

def crawl_news(conn, cursor, config, logger):
    # Fetch URLs that need to be crawled
    cursor.execute('SELECT url FROM urls WHERE crawled = 0 and url not like "%video%"')
    urls = cursor.fetchall()
    
    logger.info(f"Found {len(urls)} URLs to crawl")

    # Create a session to handle requests
    session = requests.Session()

    for i, (url,) in enumerate(urls):
        logger.info(f"{i + 1}. Starting crawl for: {url}")
        try:
            # Create a session for each URL to ensure fresh cookies handling
            with requests.Session() as session:
                # Make an initial request to handle any redirects and clear cookies
                response = session.get(url, allow_redirects=True, timeout=config['crawler']['timeout'])
                session.cookies.clear()  # Clear cookies after initial request

                # Use the final URL after handling redirects
                final_url = response.url
                
                # Fetch article using NewsPlease from the final URL
                article = NewsPlease.from_url(final_url, timeout=config['crawler']['timeout'])
                
                # Save the article data and mark the URL as crawled
                save_article(conn, cursor, article, url, logger)
                cursor.execute('UPDATE urls SET crawled = 1 WHERE url = ?', (url,))
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error crawling {url}: {e}")
        
        except Exception as e:
            logger.error(f"Unexpected error processing {url}: {e}")

    # Commit the database changes
    conn.commit()

def crawl_news_once(conn, cursor, config, logger, batch_size=100):
    # Fetch URLs that need to be crawled
    cursor.execute('SELECT url FROM urls WHERE crawled = 0 and url not like "%video%" and url not like "%www.cbsnews.com%"')
    urls = [url[0] for url in cursor.fetchall()]

    print(f"Found {len(urls)} URLs to crawl")
    logger.info(f"Found {len(urls)} URLs to crawl")

    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36"
    
    # Process in batches of 100 URLs
    for i in range(0, len(urls), batch_size):
        batch_urls = urls[i:i + batch_size]
        print(f"Processing batch {i//batch_size + 1}: {len(batch_urls)} URLs")
        logger.info(f"Processing batch {i//batch_size + 1}: {len(batch_urls)} URLs")

        try:
            # Fetch articles using NewsPlease from the batch of URLs
            articles = NewsPlease.from_urls(batch_urls, timeout=config['crawler']['timeout'], user_agent=user_agent)

            for url, article in articles.items():
                save_article(conn, cursor, article, url, logger)
                cursor.execute('UPDATE urls SET crawled = 1 WHERE url = ?', (url,))

        except requests.exceptions.RequestException as e:
            logger.error(f"Error during the crawling process: {e}")

        except Exception as e:
            logger.error(f"Unexpected error during the crawling process: {e}")

    # Commit the database changes
    conn.commit()

def save_article(conn, cursor, article, url, logger):
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
        logger.warning(f"Failed to save article to database: {url}")
        cursor.execute('UPDATE urls SET crawled = -1 WHERE url = ?', (url,))
        conn.commit()
        
        
def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default='config.yml', help='Path to the YAML configuration file')
    parser.add_argument('--db_path', type=str, default='../data/news_articles.db', help='Path to the SQLite database file')
    
    return parser.parse_args()