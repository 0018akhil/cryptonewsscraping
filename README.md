# Crypto News Scraper

This Python-based scraper is designed to gather news articles related to cryptocurrency from various sources. It utilizes Scrapy to scrape articles and subsequently converts them into multiple languages, storing the information in a MongoDB database.

## Features

- **Scraping:** Uses Scrapy to extract cryptocurrency-related news articles from diverse sources.
- **Multilingual Conversion:** Translates scraped articles into seven languages for wider accessibility.
- **MongoDB Integration:** Stores the converted articles in a MongoDB database for easy retrieval and analysis.

## Requirements

- Python 3.x
- Scrapy
- MongoDB

## Installation

1. Clone the repository: `https://github.com/0018akhil/cryptonewsscraping.git`

## Usage

1. Set up MongoDB with the necessary configurations (connection URL, database, collection, etc.).
2. Configure the scraper settings such as target languages, scraping sources, etc., in the appropriate files
3. Run the scraper: `scrapy runspider <crypto_news>.py`
4. Monitor the console for scraping progress and check the MongoDB database for stored articles.

## Configuration

- **Scrapy Settings:** Adjust code in `<crypto_news>.py` to modify scraping behavior.
- **Language Conversion:** Update language preferences or APIs in language conversion modules/files.

## Contributing

Contributions are welcome! Feel free to fork the repository, make changes, and create a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

- Mention any libraries, APIs, or resources used.
- Credit any inspirations or references that helped shape this project.

