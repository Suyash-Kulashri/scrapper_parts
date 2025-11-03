# Quick Start Guide

## 0. Prerequisites - Install Google Chrome First! ⚠️
The scraper needs Google Chrome browser to work:
```bash
brew install --cask google-chrome
```
Or download from: https://www.google.com/chrome/

**Important:** If you have Brave or another browser, Chrome is still required for best compatibility.

## 1. Install Dependencies
```bash
pip3 install -r requirements.txt
```

## 2. Test the Connection (Recommended First Step)
```bash
python3 test_connection.py
```
This will:
- Open a Chrome browser window
- Load the Partstown Trane parts page
- Save the HTML for inspection
- Show you if the page is accessible

## 3. Run the Scraper

### Option A: Interactive Menu (Easiest)
```bash
python3 run_scraper.py
```
Choose option 2 for Selenium scraper (recommended).

### Option B: Direct Selenium Scraper
```bash
python3 scraper_selenium.py
```

## 4. View Results
After scraping, check the `trane_parts/` folder:
```
trane_parts/
├── Part Name 1/
│   ├── product_info.txt  ← Product details
│   └── manual_1.pdf      ← PDF manuals
└── ...
```

## Common Issues

### "ChromeDriver not found"
- Google Chrome must be installed
- ChromeDriver is auto-installed by webdriver-manager
- If it fails, try: `brew install --cask google-chrome`

### "No parts found"
- The page structure might be different
- Try running `test_connection.py` to see what's on the page
- Check `test_page_source.html` for the actual HTML

### Browser Opens but Shows Error Page
- The website might block automated access
- The page structure might have changed
- Check if the site requires login

## Need Help?

Check the main README.md for detailed information.

