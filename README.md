# Supermarket Price Tracking System

A comprehensive system for tracking and comparing prices across major Israeli supermarket chains.

## Features

- **Multi-Chain Support**: Tracks prices from major Israeli supermarkets:
  - רמי לוי (Rami Levy)
  - שופרסל (Shufersal)
  - יוחננוף (Yochananof)
  - טיב טעם (Tiv Taam)
  - ויקטורי (Victory)

- **Smart Product Matching**: Uses advanced algorithms to match similar products across different chains:
  - Levenshtein distance for name similarity
  - Unit conversion for size comparison
  - Configurable matching thresholds

- **Real-time Price Collection**: Automatically collects prices at configurable intervals
  - Configurable collection frequency
  - Error handling and retry logic
  - Comprehensive logging

- **Interactive Dashboard**: Web-based interface for price comparison and analysis:
  - Current price comparisons
  - Historical price trends
  - Interactive graphs and filters

## System Architecture

### Core Components

1. **Scrapers** (`src/scrapers/`)
   - Base scraper class with common functionality
   - Chain-specific implementations
   - Error handling and retry logic

2. **Database Models** (`src/database/`)
   - Product information
   - Supermarket details
   - Price history
   - Product matches

3. **Product Matcher** (`src/matchers/`)
   - Similarity calculation
   - Unit conversion
   - Match management

4. **Web Dashboard** (`src/dashboard/`)
   - Price comparison views
   - Trend analysis
   - Interactive filtering

### Data Flow

1. **Price Collection**
   ```mermaid
   graph LR
   A[Scrapers] --> B[Price Data]
   B --> C[Database]
   ```

2. **Product Matching**
   ```mermaid
   graph LR
   A[Products] --> B[Matcher]
   B --> C[Matches]
   C --> D[Database]
   ```

3. **Dashboard Display**
   ```mermaid
   graph LR
   A[Database] --> B[Dashboard]
   B --> C[User Interface]
   ```

## Setup and Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/supermarket-prices.git
   cd supermarket-prices
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   - Copy `.env.example` to `.env`
   - Update configuration values as needed

5. **Initialize Database**
   ```bash
   python scripts/init_db.py
   ```

## Usage

1. **Start Price Collection Service**
   ```bash
   python src/main.py
   ```

2. **Launch Dashboard**
   ```bash
   python src/dashboard/app.py
   ```

3. **Access Dashboard**
   - Open browser to `http://localhost:8050`
   - Select products to compare
   - View price trends and comparisons

## Configuration

Key configuration options in `.env`:

```ini
# Database
DATABASE_URL=sqlite:///data/supermarket_prices.db

# Scraping
SCRAPING_INTERVAL=3600  # 1 hour

# Dashboard
DASHBOARD_HOST=localhost
DASHBOARD_PORT=8050
DASHBOARD_DEBUG=false

# Logging
LOG_LEVEL=INFO
```

## Adding New Supermarkets

1. Create a new scraper class in `src/scrapers/`:
   ```python
   from src.scrapers.base_scraper import BaseScraper

   class NewSupermarketScraper(BaseScraper):
       def parse_price_list(self, html):
           # Implement parsing logic
           pass

       def normalize_product_name(self, name):
           # Implement normalization
           pass

       def extract_product_size(self, name):
           # Implement size extraction
           pass
   ```

2. Add supermarket configuration in `config/settings.py`:
   ```python
   SUPERMARKET_CHAINS = {
       'new_supermarket': {
           'name': 'New Supermarket',
           'price_list_url': 'https://example.com/prices',
           'headers': {...}
       }
   }
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to all contributors
- Inspired by the need for transparent price comparison
- Built with Python, SQLAlchemy, and Dash 