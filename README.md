# Supermarket Price Tracker

A comprehensive system for tracking and analyzing prices across major Israeli supermarket chains.

## Features

- Automated price collection from major Israeli supermarket chains
- Smart product matching across different chains
- Historical price tracking and analysis
- Dynamic web dashboard for price comparison
- Export capabilities to Excel
- Modular architecture for easy extension

## Supported Supermarkets

- Rami Levy
- Shufersal
- Yochananof
- Tiv Taam
- Victory

## Project Structure

```
supemarket_prices/
├── src/
│   ├── scrapers/           # Price scraping modules for each chain
│   ├── matchers/           # Product matching logic
│   ├── database/           # Database models and operations
│   ├── api/                # FastAPI backend
│   ├── dashboard/          # Dash web dashboard
│   └── utils/              # Utility functions
├── config/                 # Configuration files
├── data/                   # Data storage
│   ├── shopping_lists/     # Shopping list definitions
│   └── raw/               # Raw scraped data
├── tests/                  # Test suite
└── scripts/               # Utility scripts
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Initialize the database:
```bash
python scripts/init_db.py
```

## Usage

1. Start the price collection service:
```bash
python src/main.py
```

2. Launch the web dashboard:
```bash
python src/dashboard/app.py
```

## Configuration

- Edit `config/settings.py` for general settings
- Add shopping lists in `data/shopping_lists/`
- Configure scraping schedules in `config/schedules.py`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License 