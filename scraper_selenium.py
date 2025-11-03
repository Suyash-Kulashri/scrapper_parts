from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import requests
import os
import re
import time
from urllib.parse import urljoin
import json


class PartstownScraperSelenium:
    def __init__(self, base_url="https://www.partstown.com", unique_pdfs=True):
        self.base_url = base_url
        self.output_dir = "trane_parts"
        self.driver = None
        self.session = requests.Session()
        self.unique_pdfs = unique_pdfs  # True for unique PDFs only, False for all PDFs
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def init_driver(self):
        """Initialize Selenium WebDriver"""
        chrome_options = Options()
        # Comment out headless for debugging - we can enable it after testing
        # chrome_options.add_argument('--headless')  # Run in background
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Try to find Chrome or Brave browser
        import os
        
        # Try Chrome first (preferred)
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        brave_path = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
        
        if os.path.exists(chrome_path):
            print("Found Google Chrome, using it")
            chrome_options.binary_location = chrome_path
        elif os.path.exists(brave_path):
            print("Found Brave Browser, using it instead of Chrome")
            chrome_options.binary_location = brave_path
        
        try:
            # Use webdriver-manager to automatically download and manage chromedriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            # Execute script to hide webdriver property
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
            })
            print("Selenium WebDriver initialized successfully")
        except Exception as e:
            print(f"Error initializing Chrome driver: {e}")
            print("\nBrowser installation required!")
            print("Install Chrome: brew install --cask google-chrome")
            print("Or download: https://www.google.com/chrome/")
            print("\nSee SETUP_BROWSER.md for more options")
            raise
    
    def sanitize_filename(self, filename):
        """Remove invalid characters from filename"""
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        filename = filename.strip()
        return filename[:100]
    
    def handle_popups(self):
        """Handle country selection, cookie consent, and other popups"""
        try:
            print("Handling popups and modals...")
            
            # Wait a bit for popups to appear
            time.sleep(2)
            
            # Handle Country & Currency popup
            try:
                # Look for the country selection button
                start_shopping_buttons = self.driver.find_elements(By.XPATH, 
                    "//button[contains(text(), 'START SHOPPING') or contains(text(), 'Start Shopping')]")
                if not start_shopping_buttons:
                    # Try finding button by different methods
                    start_shopping_buttons = self.driver.find_elements(By.XPATH,
                        "//a[contains(text(), 'START SHOPPING')]")
                
                for button in start_shopping_buttons:
                    if button.is_displayed():
                        print("  Found country selection popup, clicking through...")
                        button.click()
                        time.sleep(2)
                        break
            except Exception as e:
                print(f"  Country popup handling: {e}")
            
            # Handle cookie consent
            try:
                # Look for cookie consent buttons
                cookie_buttons = self.driver.find_elements(By.XPATH,
                    "//button[contains(text(), 'Accept') or contains(text(), 'Accept All') or contains(text(), 'Ok')]")
                
                for button in cookie_buttons:
                    if button.is_displayed():
                        print("  Found cookie consent, accepting...")
                        button.click()
                        time.sleep(1)
                        break
            except Exception as e:
                print(f"  Cookie popup handling: {e}")
            
            # Close any notifications if they appear
            try:
                # Look for notification close buttons
                close_buttons = self.driver.find_elements(By.XPATH,
                    "//button[@aria-label='Close' or contains(@class, 'close') or contains(@class, 'notification-close')]")
                
                for button in close_buttons:
                    if button.is_displayed():
                        print("  Closing notification...")
                        button.click()
                        time.sleep(0.5)
            except Exception:
                pass
                
            print("Popup handling complete")
            
        except Exception as e:
            print(f"Error handling popups: {e}")
    
    def get_page_selenium(self, url, wait_time=10):
        """Load a page with Selenium and wait for content"""
        try:
            self.driver.get(url)
            time.sleep(3)  # Give time for JavaScript to load
            self.handle_popups()  # Handle any popups that appear
            return True
        except Exception as e:
            print(f"Error loading page {url}: {e}")
            return False
    
    def extract_trane_parts(self, url, max_pages=None):
        """Extract all Trane parts from the main parts page with pagination"""
        print(f"Fetching Trane parts from: {url}")
        
        if not self.get_page_selenium(url):
            return []
        
        parts = []
        page_num = 0
        
        while True:
            print(f"Extracting products from page {page_num + 1}...")
            
            # Wait for products to load
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "li.js-product-item, .product-item"))
                )
            except TimeoutException:
                print("  No more products found")
                break
            
            # Find all product items on current page
            product_elements = self.driver.find_elements(By.CSS_SELECTOR, 'li.js-product-item, .product-item')
            
            page_parts_count = 0
            for element in product_elements:
                try:
                    product_name = element.get_attribute('data-name')
                    link = element.find_element(By.TAG_NAME, 'a')
                    product_url = link.get_attribute('href')
                    
                    if not product_name:
                        product_name = link.text.strip()
                    
                    if product_url and product_name:
                        parts.append({
                            'name': product_name,
                            'url': product_url
                        })
                        page_parts_count += 1
                except:
                    continue
            
            print(f"  Found {page_parts_count} products on page {page_num + 1}")
            
            # Try to find and click "Load More" or pagination button
            try:
                # Look for "Load More" button or Next page button
                next_button = None
                
                # Try multiple selectors for next page
                try:
                    next_button = self.driver.find_element(By.XPATH, 
                        "//button[contains(@class, 'js-link-paging')] | //a[contains(@class, 'next')]")
                except:
                    pass
                
                # If no button found, try "Load More"
                if not next_button:
                    try:
                        next_button = self.driver.find_element(By.XPATH,
                            "//button[contains(text(), 'Load More') or contains(text(), 'Next')]")
                    except:
                        pass
                
                if next_button and next_button.is_displayed():
                    try:
                        next_button.click()
                        time.sleep(3)  # Wait for new products to load
                        page_num += 1
                        
                        if max_pages and page_num >= max_pages:
                            print(f"Reached max pages limit: {max_pages}")
                            break
                        continue
                    except:
                        break
                else:
                    print("  No more pages found")
                    break
                    
            except Exception as e:
                print(f"Error checking for next page: {e}")
                break
        
        # Remove duplicates
        seen_urls = set()
        unique_parts = []
        for part in parts:
            if part['url'] not in seen_urls and part['name']:
                seen_urls.add(part['url'])
                unique_parts.append(part)
        
        print(f"\nTotal: Found {len(unique_parts)} unique parts across {page_num + 1} page(s)")
        return unique_parts
    
    def get_part_details(self, part_url):
        """Fetch detailed information about a specific part using Selenium"""
        print(f"Fetching details from: {part_url}")
        
        if not self.get_page_selenium(part_url, wait_time=15):
            return None, [], part_url
        
        details = {}
        pdf_urls = []
        product_page_url = part_url
        
        # Wait for product info section to load
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".product-info, .product-block"))
            )
        except TimeoutException:
            print("  Warning: Product info section not found")
        
        # Extract product information using correct selectors
        details_fields = {
            'List Price': None,
            'Quantity Available': None,
            'Manufacturer': None,
            'Manufacturer #': None,
            'Parts Town #': None,
            'Units': None,
            'Fits Models': None,
            'California Residents': None
        }
        
        # Method 1: Use product__row structure (primary method)
        try:
            rows = self.driver.find_elements(By.CSS_SELECTOR, ".product-info .product__row")
            for row in rows:
                try:
                    label_elem = row.find_element(By.CSS_SELECTOR, ".product__label")
                    val_elem = row.find_element(By.CSS_SELECTOR, ".product__val")
                    label = label_elem.text.strip().rstrip(':')
                    value = val_elem.text.strip()
                    
                    if label and value:
                        # Map labels to our fields
                        if 'Quantity' in label or ('Available' in label and 'Quantity' in label):
                            details_fields['Quantity Available'] = value
                        elif 'Manufacturer' in label and '#' not in label:
                            details_fields['Manufacturer'] = value
                        elif 'Manufacturer #' in label or ('Mfr' in label and '#' in label):
                            details_fields['Manufacturer #'] = value
                        elif 'Parts Town #' in label or 'PT #' in label:
                            details_fields['Parts Town #'] = value
                        elif 'Units' in label:
                            details_fields['Units'] = value
                        elif 'Fits Models' in label:
                            # If value is "View Models List" or similar, try to get actual list
                            if 'View' in value or 'List' in value:
                                # Try to find the actual models text nearby
                                try:
                                    models_link = row.find_element(By.XPATH, ".//a[contains(@href, '#') or contains(text(), 'View')]")
                                    models_text = models_link.get_attribute('title') or models_link.text.strip()
                                    if models_text and models_text != value:
                                        details_fields['Fits Models'] = models_text
                                    else:
                                        details_fields['Fits Models'] = value
                                except:
                                    details_fields['Fits Models'] = value
                            else:
                                details_fields['Fits Models'] = value
                except:
                    continue
        except Exception as e:
            print(f"  Error extracting from product__row: {e}")
        
        # Get List Price (special handling)
        try:
            # Try data attribute first - most reliable
            price_elem = self.driver.find_element(By.CSS_SELECTOR, "[data-listprice]")
            data_price = price_elem.get_attribute('data-listprice')
            if data_price:
                # Format as currency
                try:
                    price_val = float(data_price)
                    details_fields['List Price'] = f"$ {price_val:.2f}"
                except:
                    details_fields['List Price'] = f"$ {data_price}"
            else:
                # Fallback to text content (filter out "My Price")
                price_text = price_elem.text.strip()
                if price_text and '$' in price_text and 'My Price' not in price_text:
                    details_fields['List Price'] = price_text
        except:
            try:
                # Alternative: Look for price element with "List Price" label
                price_row = self.driver.find_element(By.XPATH,
                    "//div[contains(@class, 'product__row')]//div[contains(@class, 'product__label') and contains(text(), 'List Price')]/following-sibling::div[@class='product__cell product__val']")
                price_text = price_row.text.strip()
                if price_text:
                    details_fields['List Price'] = price_text
            except:
                try:
                    # Last resort: Look for any price element
                    price_elem = self.driver.find_element(By.CSS_SELECTOR, ".js-product-listPrice, .price-vat")
                    price_text = price_elem.text.strip()
                    # Only use if it doesn't say "My Price"
                    if price_text and '$' in price_text and 'My Price' not in price_text:
                        details_fields['List Price'] = price_text
                except:
                    pass
        
        # Get California Residents warning
        try:
            cal_elem = self.driver.find_element(By.XPATH, 
                "//*[contains(text(), 'California Residents') or contains(text(), 'Prop 65')]")
            if cal_elem:
                parent = cal_elem.find_element(By.XPATH, "./..")
                cal_text = parent.text.strip()
                # Clean up - remove just "California Residents:" label if that's all it is
                if cal_text and cal_text != "California Residents:":
                    # Remove the label if it's just a label
                    cal_text = cal_text.replace("California Residents:", "").strip()
                    if cal_text:
                        details_fields['California Residents'] = cal_text
                    else:
                        details_fields['California Residents'] = "See product page for Prop 65 warning details"
                elif not cal_text or cal_text == "California Residents:":
                    details_fields['California Residents'] = "See product page for Prop 65 warning details"
        except:
            # If no California Residents warning found, that's okay
            details_fields['California Residents'] = "N/A"
        
        details = details_fields
        
        # Find PDF links - COMPREHENSIVE SEARCH (ensuring we always find available PDFs)
        # Use a helper function to normalize and add URLs
        def add_pdf_url(url):
            """Helper to normalize and add PDF URL"""
            if not url or '.pdf' not in url.lower():
                return
            # Normalize URL
            if url.startswith('/'):
                url = f"https://www.partstown.com{url}"
            elif not url.startswith('http'):
                url = f"https://www.partstown.com/modelManual/{url}"
            # Add if not already present
            if url not in pdf_urls:
                pdf_urls.append(url)
        
        try:
            # Step 1: Extract PDFs from data attributes FIRST (most reliable, works even without clicking)
            try:
                pdf_data_elems = self.driver.find_elements(By.XPATH, "//*[@data-manual-name]")
                for elem in pdf_data_elems:
                    try:
                        # First try to get href (most reliable)
                        href = elem.get_attribute('href')
                        if href:
                            add_pdf_url(href)
                        
                        # Also check data-manual-name attribute
                        manual_name = elem.get_attribute('data-manual-name')
                        if manual_name and '.pdf' in manual_name.lower():
                            # If href wasn't found, construct from manual name
                            if not href:
                                add_pdf_url(manual_name)
                    except:
                        continue
            except Exception as e:
                print(f"  Error checking data attributes: {e}")
            
            # Step 2: Find PDFs on main page (direct links)
            try:
                pdf_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
                for link in pdf_links:
                    try:
                        href = link.get_attribute('href')
                        if href:
                            add_pdf_url(href)
                    except:
                        continue
            except Exception as e:
                print(f"  Error finding direct PDF links: {e}")
            
            # Step 3: Click "MANUALS & DIAGRAMS" tab to reveal more PDFs
            try:
                manual_tab = self.driver.find_element(By.XPATH,
                    "//a[@href='#manualsDiagrams'] | //a[contains(@href, '#manualsDiagrams')] | " +
                    "//li[@role='tab']//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'manuals') and contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'diagrams')]")
                
                if manual_tab and manual_tab.is_displayed():
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", manual_tab)
                    time.sleep(0.5)
                    manual_tab.click()
                    time.sleep(4)  # Wait for content to load
                    
                    # Find all PDFs after clicking tab
                    tab_pdfs = self.driver.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
                    for link in tab_pdfs:
                        try:
                            href = link.get_attribute('href')
                            if href:
                                add_pdf_url(href)
                        except:
                            continue
                    
                    # Also extract from data attributes again after tab click (in case new content loaded)
                    try:
                        pdf_data_elems_after = self.driver.find_elements(By.XPATH, "//*[@data-manual-name]")
                        for elem in pdf_data_elems_after:
                            try:
                                href = elem.get_attribute('href')
                                if href:
                                    add_pdf_url(href)
                                manual_name = elem.get_attribute('data-manual-name')
                                if manual_name and '.pdf' in manual_name.lower() and not href:
                                    add_pdf_url(manual_name)
                            except:
                                continue
                    except:
                        pass
                    
                    # Scroll within the tab section to trigger lazy loading
                    try:
                        section = self.driver.find_element(By.XPATH,
                            "//div[@id='manualsDiagrams'] | //div[contains(@class, 'manuals')] | //section[@id='manualsDiagrams']")
                        if section:
                            for i in range(3):
                                self.driver.execute_script("arguments[0].scrollTop += 300;", section)
                                time.sleep(1)
                                
                                # Check for new PDFs after scroll
                                scroll_pdfs = section.find_elements(By.XPATH, ".//a[contains(@href, '.pdf')]")
                                for link in scroll_pdfs:
                                    try:
                                        href = link.get_attribute('href')
                                        if href:
                                            add_pdf_url(href)
                                    except:
                                        continue
                    except:
                        pass
            except:
                pass  # Tab might not exist, that's okay
            
            # Step 4: Check popup menus (model-specific manuals)
            try:
                popup_items = self.driver.find_elements(By.XPATH,
                    "//ul[contains(@class, 'data-sheet__popup__list')]//a | " +
                    "//div[contains(@class, 'popup')]//a[contains(@href, '.pdf')] | " +
                    "//div[contains(@class, 'data-sheet__popup')]//a")
                
                for item in popup_items:
                    try:
                        href = item.get_attribute('href')
                        if href:
                            add_pdf_url(href)
                        
                        # Also check data attributes
                        manual_name = item.get_attribute('data-manual-name')
                        if manual_name and '.pdf' in manual_name.lower():
                            add_pdf_url(manual_name)
                    except:
                        continue
            except:
                pass
            
            # Step 5: Scroll entire page to catch any lazy-loaded PDFs
            for i in range(3):
                self.driver.execute_script("window.scrollBy(0, 500);")
                time.sleep(1)
                
                scroll_pdfs = self.driver.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
                for link in scroll_pdfs:
                    try:
                        href = link.get_attribute('href')
                        if href:
                            add_pdf_url(href)
                    except:
                        continue
        except Exception as e:
            print(f"  Error finding PDF links: {e}")
        
        # Remove duplicates if unique_pdfs is True, otherwise keep all
        if self.unique_pdfs:
            from urllib.parse import urlparse
            seen_bases = set()
            unique_pdfs = []
            for pdf_url in pdf_urls:
                parsed = urlparse(pdf_url)
                base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                if base_url not in seen_bases:
                    seen_bases.add(base_url)
                    unique_pdfs.append(pdf_url)
            
            pdf_urls = unique_pdfs
        
        # Product page URL (already set to part_url)
        # No need to do anything else
        
        # Debug output
        if pdf_urls:
            print(f"  Found {len(pdf_urls)} PDF(s)")
        else:
            print(f"  No PDFs found for this product")
        
        return details, pdf_urls, product_page_url
    
    def download_pdf(self, pdf_url, filepath):
        """Download a PDF file"""
        try:
            response = self.session.get(pdf_url, timeout=60, stream=True)
            response.raise_for_status()
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Downloaded: {os.path.basename(filepath)}")
            return True
        except Exception as e:
            print(f"Failed to download PDF {pdf_url}: {e}")
            return False
    
    def save_part_info(self, details, pdf_urls, product_page_url, filepath):
        """Save part information to a text file with product page link and PDF links"""
        content = []
        
        # First section: Product Page Link
        content.append("=" * 60)
        content.append("PRODUCT PAGE - WEB LINK")
        content.append("=" * 60)
        content.append(f"Product Page: {product_page_url}")
        
        # Add separator
        content.append("")
        content.append("=" * 60)
        content.append("PRODUCT DETAILS")
        content.append("=" * 60)
        
        # Second section: Product Details
        for key, value in details.items():
            value_str = str(value) if value else "N/A"
            content.append(f"{key}: {value_str}")
        
        # Add separator
        content.append("")
        content.append("=" * 60)
        # Update heading based on unique_pdfs setting
        if self.unique_pdfs:
            content.append("PDF MANUALS - WEB LINKS (UNIQUE)")
        else:
            content.append("PDF MANUALS - WEB LINKS (ALL)")
        content.append("=" * 60)
        
        # Third section: PDF Links
        if pdf_urls:
            for idx, pdf_url in enumerate(pdf_urls, 1):
                content.append(f"PDF {idx}: {pdf_url}")
        else:
            content.append("No PDF manuals available for this product")
        
        # Create directory if needed (only if filepath has a directory)
        dir_path = os.path.dirname(filepath)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
        print(f"Saved info: {os.path.basename(filepath)}")
    
    def scrape_part(self, part):
        """Scrape a single part"""
        part_name = self.sanitize_filename(part['name'])
        part_folder = os.path.join(self.output_dir, part_name)
        
        # Get part details
        details, pdf_urls, product_page_url = self.get_part_details(part['url'])
        
        if details:
            # Save product information with product page link and PDF links
            info_file = os.path.join(part_folder, 'product_info.txt')
            self.save_part_info(details, pdf_urls, product_page_url, info_file)
        
        # Download PDFs
        pdf_count = 0
        for idx, pdf_url in enumerate(pdf_urls):
            pdf_filename = f"manual_{idx + 1}.pdf"
            pdf_path = os.path.join(part_folder, pdf_filename)
            if self.download_pdf(pdf_url, pdf_path):
                pdf_count += 1
        
        print(f"Scraped: {part_name} ({pdf_count} PDFs downloaded)")
        time.sleep(2)  # Be respectful
    
    def run(self, url):
        """Main scraping function"""
        print("Starting Partstown Trane Parts Scraper (Selenium)")
        print("=" * 50)
        
        try:
            # Initialize driver
            self.init_driver()
            
            # Create output directory
            os.makedirs(self.output_dir, exist_ok=True)
            
            # Get all parts
            parts = self.extract_trane_parts(url)
            
            if not parts:
                print("No parts found. The page might need authentication or has a different structure.")
                return
            
            # Scrape each part
            total = len(parts)
            for idx, part in enumerate(parts, 1):
                print(f"\nProcessing part {idx}/{total}")
                self.scrape_part(part)
            
            print("\n" + "=" * 50)
            print(f"Scraping complete! {total} parts processed.")
            
        finally:
            if self.driver:
                self.driver.quit()
                print("Browser closed")


def main():
    url = "https://www.partstown.com/trane/parts"  # Removed fragment for better compatibility
    
    # Ask user for PDF extraction preference
    print("\n" + "=" * 60)
    print("PDF EXTRACTION OPTION")
    print("=" * 60)
    print("Choose how to extract PDFs:")
    print("1. Unique PDFs only (remove duplicates)")
    print("2. All PDFs (including duplicates)")
    
    try:
        pdf_choice = input("\nEnter your choice (1 or 2, default: 1): ").strip()
        unique_pdfs = pdf_choice != '2'
        if unique_pdfs:
            print("Selected: Unique PDFs only")
        else:
            print("Selected: All PDFs (including duplicates)")
    except (EOFError, KeyboardInterrupt):
        # If running non-interactively, default to unique
        unique_pdfs = True
        print("\nNon-interactive mode: Using unique PDFs (default)")
    
    scraper = PartstownScraperSelenium(unique_pdfs=unique_pdfs)
    scraper.run(url)


if __name__ == "__main__":
    main()

