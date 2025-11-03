# How to Run the Scraper

## ✅ Setup Complete!

You've successfully:
1. ✅ Installed Google Chrome
2. ✅ Updated code to prioritize Chrome
3. ✅ Tested the connection - it works!

## Next Steps

### Run the Scraper Now

**Option 1: Interactive Menu (Easiest)**
```bash
python3 run_scraper.py
```
Then choose option 2 (Selenium Scraper)

**Option 2: Direct Run**
```bash
python3 scraper_selenium.py
```

### What Will Happen

1. The browser will open (you'll see it working)
2. **Popups are handled automatically** - Country selection, cookies, notifications
3. It will scrape **all pages** of Trane parts (36,891+ parts!)
4. For each part, it will:
   - Extract product information (List Price, Manufacturer, etc.)
   - Download all PDF manuals
   - Save everything in organized folders

### ⚠️ IMPORTANT NOTE

There are **36,891 Trane parts** on the website! 
- Scraping ALL of them will take **many hours**
- Each product has ~1–2s delay (to respect the website)
- Estimated time: **12–24 hours** for the full scrape

Consider testing with a limited number of pages first by modifying the scraper.

### Output Structure

You'll get a folder structure like this:
```
trane_parts/
├── Drain Pan, Evaporator, Condensate/
│   ├── product_info.txt
│   └── manual_1.pdf
├── Capacitor XY123/
│   ├── product_info.txt
│   ├── manual_1.pdf
│   └── manual_2.pdf
└── ...
```

## Important Notes

- **Time**: Scraping all parts will take a while (there are 36,891 parts!)
- **Be Patient**: The scraper respects the website with delays between requests
- **Browser Window**: You'll see the Chrome browser working
- **Can Stop Anytime**: Press Ctrl+C to stop if needed

## Troubleshooting

If you see any errors, they'll be displayed in the terminal. The scraper will continue with other parts even if some fail.

## That's It!

You're ready to scrape! Run `python3 run_scraper.py` when you're ready.

