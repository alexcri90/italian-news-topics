"""
News scraper module to extract articles from Italian news sources.
"""
import os
import json
import time
import logging
from datetime import datetime
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import newspaper
from newspaper import Article
from tqdm import tqdm

from scraper.sources import SOURCES, USER_AGENT, MIN_REQUEST_INTERVAL

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("news_scraper")

# Dictionary to keep track of last request time per domain
last_request_time = {}

class NewsScraper:
    def __init__(self, output_dir="_data"):
        """Initialize the scraper with output directory for collected data."""
        self.output_dir = output_dir
        self.headers = {"User-Agent": USER_AGENT}
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize article storage
        self.articles = []
    
    def _respect_rate_limits(self, url):
        """Ensure we respect rate limiting for ethical scraping."""
        domain = urlparse(url).netloc
        current_time = time.time()
        
        if domain in last_request_time:
            elapsed = current_time - last_request_time[domain]
            if elapsed < MIN_REQUEST_INTERVAL:
                wait_time = MIN_REQUEST_INTERVAL - elapsed
                logger.debug(f"Rate limiting: waiting {wait_time:.2f}s for {domain}")
                time.sleep(wait_time)
        
        last_request_time[domain] = time.time()
    
    def _fetch_rss_articles(self, source):
        """Fetch articles from an RSS feed."""
        articles = []
        try:
            self._respect_rate_limits(source["rss_feed"])
            response = requests.get(source["rss_feed"], headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "xml")
            items = soup.find_all("item")
            
            for item in items[:10]:  # Limit to 10 articles per source
                title = item.find("title").text
                link = item.find("link").text
                
                # Skip if no title or link
                if not title or not link:
                    continue
                
                articles.append({
                    "source": source["name"],
                    "title": title,
                    "url": link
                })
                
            logger.info(f"Fetched {len(articles)} articles from {source['name']} RSS feed")
        except Exception as e:
            logger.error(f"Error fetching RSS feed from {source['name']}: {str(e)}")
        
        return articles
    
    def _fetch_homepage_articles(self, source):
        """Scrape articles from a news source homepage."""
        articles = []
        try:
            self._respect_rate_limits(source["url"])
            response = requests.get(source["url"], headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            article_links = soup.select(source["article_selector"])
            
            # Extract up to 10 article URLs
            urls = []
            for link in article_links[:10]:
                href = link.get("href")
                if href:
                    # Handle relative URLs
                    if href.startswith("/"):
                        base_url = "{uri.scheme}://{uri.netloc}".format(uri=urlparse(source["url"]))
                        href = base_url + href
                    urls.append(href)
            
            # Get article titles
            for url in urls:
                try:
                    self._respect_rate_limits(url)
                    article = newspaper.Article(url)
                    article.download()
                    article.parse()
                    
                    articles.append({
                        "source": source["name"],
                        "title": article.title,
                        "url": url
                    })
                except Exception as e:
                    logger.warning(f"Could not parse article {url}: {str(e)}")
            
            logger.info(f"Fetched {len(articles)} articles from {source['name']} homepage")
        except Exception as e:
            logger.error(f"Error scraping homepage from {source['name']}: {str(e)}")
        
        return articles
    
    def _extract_article_content(self, article_info):
        """Extract the full content from an article URL."""
        try:
            url = article_info["url"]
            self._respect_rate_limits(url)
            
            article = Article(url)
            article.download()
            article.parse()
            
            # Update article with content
            article_info["content"] = article.text
            article_info["publish_date"] = article.publish_date.isoformat() if article.publish_date else None
            article_info["scraped_at"] = datetime.now().isoformat()
            
            return article_info
        except Exception as e:
            logger.warning(f"Could not extract content from {url}: {str(e)}")
            article_info["content"] = ""
            article_info["scraped_at"] = datetime.now().isoformat()
            return article_info
    
    def scrape_all_sources(self):
        """Scrape articles from all configured sources."""
        all_articles = []
        
        logger.info(f"Starting scraping of {len(SOURCES)} news sources")
        
        for source in SOURCES:
            logger.info(f"Scraping {source['name']}")
            
            # Choose scraping method based on configuration
            if source["should_use_rss"]:
                articles = self._fetch_rss_articles(source)
            else:
                articles = self._fetch_homepage_articles(source)
            
            all_articles.extend(articles)
        
        logger.info(f"Found {len(all_articles)} articles across all sources")
        self.articles = all_articles
        return all_articles
    
    def extract_article_contents(self):
        """Extract full content from all collected article URLs."""
        if not self.articles:
            logger.warning("No articles to extract content from. Run scrape_all_sources first.")
            return []
        
        logger.info(f"Extracting content from {len(self.articles)} articles")
        articles_with_content = []
        
        for article in tqdm(self.articles, desc="Extracting article content"):
            article_with_content = self._extract_article_content(article)
            # Only keep articles with actual content
            if article_with_content["content"]:
                articles_with_content.append(article_with_content)
        
        self.articles = articles_with_content
        logger.info(f"Successfully extracted content from {len(articles_with_content)} articles")
        return articles_with_content
    
    def save_articles(self):
        """Save collected articles to a JSON file with today's date."""
        if not self.articles:
            logger.warning("No articles to save.")
            return
        
        # Create filename with today's date
        today = datetime.now().strftime("%Y-%m-%d")
        filepath = os.path.join(self.output_dir, f"articles_{today}.json")
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.articles, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved {len(self.articles)} articles to {filepath}")
        return filepath

# Main execution function
def run_scraper():
    """Main function to run the scraper and save results."""
    scraper = NewsScraper()
    scraper.scrape_all_sources()
    scraper.extract_article_contents()
    output_file = scraper.save_articles()
    return output_file

if __name__ == "__main__":
    run_scraper()