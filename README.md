# News Crawler Project

## Overview
This project is designed to crawl news data in real-time using the `news-please` library in Python. It collects, processes, and updates news articles automatically.

## Structure
- `config/`: Configuration files.
- `data/`: Raw, processed, and archived data.
- `notebooks/`: Jupyter notebooks for data exploration.
- `src/`: Core scripts for crawling, processing, and updating.
- `tests/`: Unit tests.
- `logs/`: Log files.

## Usage
1. Set up the environment: `pip install -r requirements.txt`
2. Run the crawler: `python src/crawler.py`
3. Process data: `python src/process_data.py`
4. Schedule updates: `python src/scheduler.py`

## Configuration
Edit `config/config.yaml` to change settings like URLs and crawl intervals.

## References
- [TopNews](https://github.com/notnews/top_news.git)

## Notes:
- Some cnn page have been set to -1 because of timeout error, should be process later with longer timeout.
- abcnews news have been removed because lots of unavaiable pages.