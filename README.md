# Italian News Topics Tracker

A static website that analyzes and displays the most common topics appearing in Italian online newspapers daily. The analysis uses Natural Language Processing (NLP) to extract trending entities and keywords from news articles.

## 📊 Features

- Daily automatic scraping of major Italian news websites
- Text analysis with NLP to identify trending topics, entities, and keywords
- Interactive visualizations with Chart.js
- Fully automated pipeline using GitHub Actions
- Zero-cost hosting with GitHub Pages

## 🛠️ Technologies Used

- **Data Collection**: Python, BeautifulSoup, Newspaper3k
- **Text Analysis**: spaCy with Italian language model
- **Static Site Generation**: 11ty (Eleventy)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Visualization**: Chart.js
- **Automation**: GitHub Actions
- **Hosting**: GitHub Pages

## 🚀 Project Structure

```
italian-news-topics/
├── .github/workflows/     # GitHub Actions workflows
├── scraper/               # News scraping module
├── analysis/              # Topic analysis module
├── _data/                 # JSON data (generated)
├── _includes/             # Template partials
├── assets/                # Static assets (CSS, JS)
└── _site/                 # Generated site (not committed)
```

## 📝 How It Works

1. **Data Collection**: Daily scheduled GitHub Action scrapes Italian news sites
2. **Text Analysis**: NLP extracts entities and keywords from articles
3. **Static Site Generation**: 11ty builds static HTML/CSS/JS
4. **Deployment**: Automatically published to GitHub Pages

## 🔧 Local Development

### Prerequisites

- Python 3.8+
- Node.js 14+
- Git

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/italian-news-topics.git
cd italian-news-topics

# Python environment
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python -m spacy download it_core_news_sm

# Node.js dependencies
npm install

# Run scraper and analyzer for initial data
python -c "from scraper.scraper import run_scraper; run_scraper()"
python -c "from analysis.topic_analyzer import run_analyzer; run_analyzer()"

# Serve site locally
npm run serve
```

The site will be available at http://localhost:8080

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

- Alexandre Crivellari

## 📚 Acknowledgments

- Data sourced from major Italian news outlets
- Built with ethical web scraping principles