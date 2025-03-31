"""
Topic analyzer module to extract common topics from news articles.
"""
import os
import json
import logging
from datetime import datetime
from collections import Counter
import spacy
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("analyzer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("topic_analyzer")

class TopicAnalyzer:
    def __init__(self, input_dir="_data", output_dir="_data"):
        """Initialize the topic analyzer with input and output directories."""
        self.input_dir = input_dir
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Load Italian language model
        try:
            self.nlp = spacy.load("it_core_news_sm")
            logger.info("Loaded Italian language model")
        except OSError:
            logger.error("Italian language model not found. Make sure to run: python -m spacy download it_core_news_sm")
            raise
    
    def _get_latest_articles_file(self):
        """Get the most recent articles JSON file."""
        json_files = [f for f in os.listdir(self.input_dir) if f.startswith("articles_") and f.endswith(".json")]
        
        if not json_files:
            logger.error("No article files found in input directory")
            return None
        
        # Sort by date in filename
        latest_file = sorted(json_files, reverse=True)[0]
        return os.path.join(self.input_dir, latest_file)
    
    def _load_articles(self, filepath=None):
        """Load articles from JSON file."""
        if filepath is None:
            filepath = self._get_latest_articles_file()
            if filepath is None:
                return []
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                articles = json.load(f)
            
            logger.info(f"Loaded {len(articles)} articles from {filepath}")
            return articles
        except Exception as e:
            logger.error(f"Error loading articles from {filepath}: {str(e)}")
            return []
    
    def _extract_named_entities(self, articles):
        """Extract named entities from article content."""
        entity_counter = Counter()
        source_entity_counter = {}
        
        logger.info("Extracting named entities from articles")
        
        for article in tqdm(articles, desc="Processing articles"):
            source = article["source"]
            content = article["content"]
            
            # Skip articles with empty content
            if not content:
                continue
            
            # Process text with spaCy
            doc = self.nlp(content)
            
            # Extract named entities (people, organizations, locations)
            entities = []
            for ent in doc.ents:
                if ent.label_ in ["PER", "ORG", "LOC", "GPE"]:
                    # Clean and normalize entity text
                    entity_text = ent.text.strip().title()
                    
                    # Skip very short entities and numbers
                    if len(entity_text) <= 2 or entity_text.isdigit():
                        continue
                    
                    entities.append((entity_text, ent.label_))
            
            # Update global counter
            entity_counter.update(entity_text for entity_text, _ in entities)
            
            # Update source-specific counter
            if source not in source_entity_counter:
                source_entity_counter[source] = Counter()
            source_entity_counter[source].update(entity_text for entity_text, _ in entities)
        
        return entity_counter, source_entity_counter
    
    def _extract_keywords(self, articles):
        """Extract important keywords from article content."""
        keyword_counter = Counter()
        
        logger.info("Extracting keywords from articles")
        
        for article in tqdm(articles, desc="Analyzing keywords"):
            content = article["content"]
            
            # Skip articles with empty content
            if not content:
                continue
            
            # Process text with spaCy
            doc = self.nlp(content)
            
            # Extract nouns and adjectives as keywords
            keywords = []
            for token in doc:
                if token.pos_ in ["NOUN", "PROPN", "ADJ"] and not token.is_stop and len(token.text) > 3:
                    keywords.append(token.lemma_.lower())
            
            # Update counter
            keyword_counter.update(keywords)
        
        return keyword_counter
    
    def analyze_topics(self):
        """Analyze the latest articles to extract common topics."""
        # Load the latest articles
        articles = self._load_articles()
        if not articles:
            logger.error("No articles found to analyze")
            return None
        
        # Extract named entities and keywords
        entity_counter, source_entity_counter = self._extract_named_entities(articles)
        keyword_counter = self._extract_keywords(articles)
        
        # Get the most common entities and keywords
        top_entities = entity_counter.most_common(50)
        top_keywords = keyword_counter.most_common(100)
        
        # Get top entities by source
        top_entities_by_source = {}
        for source, counter in source_entity_counter.items():
            top_entities_by_source[source] = counter.most_common(20)
        
        # Prepare topic data
        topic_data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "total_articles": len(articles),
            "sources": list(set(article["source"] for article in articles)),
            "top_entities": [{"text": entity, "count": count} for entity, count in top_entities],
            "top_keywords": [{"text": keyword, "count": count} for keyword, count in top_keywords],
            "top_entities_by_source": {
                source: [{"text": entity, "count": count} for entity, count in entities]
                for source, entities in top_entities_by_source.items()
            }
        }
        
        return topic_data
    
    def save_topic_data(self, topic_data):
        """Save topic data to JSON file."""
        if topic_data is None:
            logger.error("No topic data to save")
            return None
        
        # Save to date-specific file
        date = topic_data["date"]
        date_filepath = os.path.join(self.output_dir, f"topics_{date}.json")
        
        with open(date_filepath, "w", encoding="utf-8") as f:
            json.dump(topic_data, f, ensure_ascii=False, indent=2)
        
        # Also save to topics.json for the website
        topics_filepath = os.path.join(self.output_dir, "topics.json")
        
        with open(topics_filepath, "w", encoding="utf-8") as f:
            json.dump(topic_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved topic data to {date_filepath} and {topics_filepath}")
        return topics_filepath

# Main execution function
def run_analyzer():
    """Main function to run the topic analyzer."""
    analyzer = TopicAnalyzer()
    topic_data = analyzer.analyze_topics()
    output_file = analyzer.save_topic_data(topic_data)
    return output_file

if __name__ == "__main__":
    run_analyzer()