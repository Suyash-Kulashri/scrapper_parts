# Browser Setup Instructions

## ❌ Current Issue: Browser Not Found

You have Brave Browser installed, but `webdriver-manager` is having trouble detecting the correct ChromeDriver version (Brave 141 needs ChromeDriver 141, but it downloaded 114).

## ✅ Recommended Solution: Install Google Chrome

**On macOS:**
```bash
brew install --cask google-chrome
```

**Or download manually:**
Visit: https://www.google.com/chrome/
- Download and install Chrome
- Then rerun: `python3 run_scraper.py`

## Why Chrome?
- webdriver-manager works perfectly with Chrome
- Better compatibility with Selenium
- More stable for web scraping

## Alternative: Manual ChromeDriver (Advanced)
If you want to stick with Brave:
1. Download ChromeDriver 141 manually from: https://chromedriver.chromium.org/
2. Extract it to your PATH
3. Update the scraper to use the local path

But honestly, installing Chrome is much easier!

