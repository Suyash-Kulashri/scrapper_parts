"""Test connection to Partstown website"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def test_connection():
    """Test if we can connect to the Partstown website"""
    print("Initializing Chrome driver...")
    
    chrome_options = Options()
    # Don't run headless initially so we can see what's happening
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--window-size=1920,1080')
    
    # Try to find Chrome or Brave browser
    import os
    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    brave_path = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
    
    if os.path.exists(chrome_path):
        print("Found Google Chrome, using it")
        chrome_options.binary_location = chrome_path
    elif os.path.exists(brave_path):
        print("Found Brave Browser, using it instead of Chrome")
        chrome_options.binary_location = brave_path
    
    try:
        # Use the version argument to get a compatible chromedriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Hide webdriver property
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
        })
        
        print("Loading page...")
        url = "https://www.partstown.com/trane/parts"  # Remove the #id fragment
        driver.get(url)
        
        # Wait a bit for page to load
        import time
        time.sleep(3)
        
        # Handle popups
        print("Handling popups...")
        try:
            # Handle Country & Currency popup
            start_shopping_buttons = driver.find_elements(By.XPATH, 
                "//button[contains(text(), 'START SHOPPING')] | //a[contains(text(), 'START SHOPPING')]")
            for button in start_shopping_buttons:
                if button.is_displayed():
                    print("  Clicking through country selection...")
                    button.click()
                    time.sleep(2)
                    break
        except:
            pass
        
        try:
            # Handle cookie consent
            cookie_buttons = driver.find_elements(By.XPATH,
                "//button[contains(text(), 'Accept All') or contains(text(), 'Accept')]")
            for button in cookie_buttons:
                if button.is_displayed():
                    print("  Accepting cookies...")
                    button.click()
                    time.sleep(1)
                    break
        except:
            pass
        
        print(f"Page title: {driver.title}")
        print(f"Page length: {len(driver.page_source)} characters")
        
        # Save page source for inspection
        with open('test_page_source.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("Page source saved to test_page_source.html")
        
        # Check for common elements
        print("\nChecking for elements...")
        try:
            links = driver.find_elements('tag name', 'a')
            print(f"Found {len(links)} links on the page")
            
            trane_links = [l for l in links if '/trane/parts/' in l.get_attribute('href') or '']
            print(f"Found {len(trane_links)} Trane-specific links")
            
            if trane_links:
                print("\nFirst few Trane links:")
                for link in trane_links[:5]:
                    href = link.get_attribute('href')
                    text = link.text.strip()[:50]
                    print(f"  - {text} -> {href}")
        
        except Exception as e:
            print(f"Error checking elements: {e}")
        
        try:
            input("\nPress Enter to close the browser...")
        except EOFError:
            pass
        driver.quit()
        print("Browser closed")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_connection()

