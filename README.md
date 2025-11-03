# Partstown Trane Parts Scraper

This project scrapes Trane parts information and PDF manuals from the Partstown website.

## Features

- ✅ **Automatic popup handling** - Bypasses country selection, cookie consent, and notifications
- 📦 **Full pagination support** - Scrapes all 36,891+ Trane parts across multiple pages
- 📄 Extracts product information for each Trane part (List Price, Quantity Available, Manufacturer, etc.)
- 📕 Downloads all PDF manuals associated with each part
- 📁 Organizes data in a structured folder hierarchy
- 🤖 Smart JavaScript rendering with Selenium WebDriver

## Output Structure

```
trane_parts/
├── Part Name 1/
│   ├── product_info.txt
│   ├── manual_1.pdf
│   └── manual_2.pdf
├── Part Name 2/
│   ├── product_info.txt
│   └── manual_1.pdf
└── ...
```

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. For Selenium scraping (recommended for JavaScript-heavy sites):
   - Google Chrome browser must be installed on your system
   - ChromeDriver will be automatically installed by webdriver-manager
   - No manual installation needed!

## Usage

### Quick Start (Recommended)
Run the interactive menu:
```bash
python3 run_scraper.py
```

### Direct Usage

#### Basic Scraper (BeautifulSoup)
For sites that don't heavily rely on JavaScript:
```bash
python3 scraper.py
```

#### Advanced Scraper (Selenium)
For sites with dynamic content loaded by JavaScript:
```bash
python3 scraper_selenium.py
```

## Configuration

The target URL is hardcoded in the main function:
- `https://www.partstown.com/trane/parts`

To change it, edit the `main()` function in either scraper file.

## Notes

- The scraper includes respectful delays between requests
- Selenium scraper runs in headless mode (no browser window)
- Both scrapers handle missing or unavailable data gracefully
- PDFs are downloaded with proper error handling

## Testing

Before running the full scraper, you can test the connection:
```bash
python3 test_connection.py
```
This will open a browser window and save the page source for inspection.

## Troubleshooting

1. **ChromeDriver/Browser errors**: Make sure Google Chrome browser is installed. See `SETUP_BROWSER.md` for detailed instructions.
   - Install Chrome: `brew install --cask google-chrome`
   - ChromeDriver is automatically managed by webdriver-manager
2. **No parts found**: The page structure might have changed, or the site requires authentication
3. **PDF download fails**: Some PDFs might be behind authentication or have incorrect URLs
4. **403 Forbidden**: The website might be blocking automated access. Try using non-headless mode first

## Legal Notice

This scraper is for educational purposes. Make sure you comply with Partstown's Terms of Service and robots.txt when using this tool.

