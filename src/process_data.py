import logging
import logging.config
import yaml
import sqlite3

# Load configuration
with open('../config/config.yaml', 'r') as file:
    config = yaml.safe_load(file)

with open('../config/logging_config.yaml', 'r') as file:
    logging_config = yaml.safe_load(file)

# Apply logging configuration
logging.config.dictConfig(logging_config)

# Get a specific logger for the process_data script
logger = logging.getLogger('process_data')

def connect_db(db_path):
    logger.info(f"Connecting to database at {db_path}...")
    try:
        conn = sqlite3.connect(db_path)
        logger.info("Database connection successful.")
        return conn
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        raise

def remove_video_urls(conn):
    cursor = conn.cursor()
    logger.info("Removing rows with URLs containing 'video'...")

    try:
        # Identify rows to delete
        cursor.execute("SELECT id, url FROM articles WHERE url LIKE '%video%'")
        rows_to_delete = cursor.fetchall()

        if not rows_to_delete:
            logger.info("No rows with 'video' in URL found.")
            return

        # Delete rows with URLs containing 'video'
        cursor.executemany("DELETE FROM articles WHERE id = ?", [(row[0],) for row in rows_to_delete])
        conn.commit()

        logger.info(f"Removed {len(rows_to_delete)} rows with URLs containing 'video'.")
    except Exception as e:
        logger.error(f"Error during row removal: {e}")
        conn.rollback()
        raise

def main():
    db_path = '../data/news_articles.db'  # Update this path as needed

    try:
        conn = connect_db(db_path)
        remove_video_urls(conn)
    except Exception as e:
        logger.error(f"Process failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
