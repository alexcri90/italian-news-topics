"""
Configuration file for Italian news sources.
Each source defines:
- name: Display name of the news source
- url: Homepage URL
- rss_feed: RSS feed URL if available (preferred method)
- article_selector: CSS selector to find article links on homepage
- should_use_rss: Whether to use RSS feed (True) or scrape homepage (False)
"""

SOURCES = [
    {
        "name": "La Repubblica",
        "url": "https://www.repubblica.it/",
        "rss_feed": "https://www.repubblica.it/rss/homepage/rss2.0.xml",
        "article_selector": "a.headline-link",
        "should_use_rss": True
    },
    {
        "name": "Corriere della Sera",
        "url": "https://www.corriere.it/",
        "rss_feed": "https://www.corriere.it/rss/homepage.xml",
        "article_selector": "a.title-art",
        "should_use_rss": True
    },
    {
        "name": "Il Sole 24 Ore",
        "url": "https://www.ilsole24ore.com/",
        "rss_feed": "https://www.ilsole24ore.com/rss/italia.xml",
        "article_selector": "a.apicella",
        "should_use_rss": True
    },
    {
        "name": "La Stampa",
        "url": "https://www.lastampa.it/",
        "rss_feed": "https://www.lastampa.it/rss/home.xml",
        "article_selector": "a.entry__title",
        "should_use_rss": True
    },
    {
        "name": "Il Fatto Quotidiano",
        "url": "https://www.ilfattoquotidiano.it/",
        "rss_feed": "https://www.ilfattoquotidiano.it/feed/",
        "article_selector": "h2.entry-title a",
        "should_use_rss": True
    }
]

# User agent for ethical scraping
USER_AGENT = "NewsTopicAnalyzer/1.0 (Educational Project; +https://github.com/yourusername/italian-news-topics)"

# Rate limiting settings (in seconds)
MIN_REQUEST_INTERVAL = 3  # Wait at least 3 seconds between requests to the same domain