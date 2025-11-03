import requests
from bs4 import BeautifulSoup
import os
import re
import time
from urllib.parse import urljoin, urlparse
import json


class PartstownScraper:
    def __init__(self, base_url="https://www.partstown.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.output_dir = "trane_parts"
        
    def sanitize_filename(self, filename):
        """Remove invalid characters from filename"""
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        filename = filename.strip()
        return filename[:100]  # Limit length
    
    def get_page(self, url, retries=3):
        """Fetch a page with retry logic"""
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                print(f"Failed to fetch {url}: {e}")
                return None
    
    def extract_trane_parts(self, url):
        """Extract all Trane parts from the main parts page"""
        print(f"Fetching Trane parts from: {url}")
        response = self.get_page(url)
        if not response:
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        parts = []
        
        # Look for product cards/links - this may need adjustment based on actual HTML structure
        product_links = soup.find_all('a', href=re.compile(r'/trane/parts/'))
        
        for link in product_links:
            product_url = urljoin(self.base_url, link.get('href', ''))
            product_name = link.get_text(strip=True)
            
            if product_url and product_name:
                parts.append({
                    'name': product_name,
                    'url': product_url
                })
        
        # If the above doesn't work, try to find JSON data in the page
        if not parts:
            scripts = soup.find_all('script', type='application/json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    # Process JSON data structure
                    if isinstance(data, dict):
                        parts.extend(self._parse_json_data(data))
                except:
                    pass
        
        # Alternative: Look for data attributes or specific class patterns
        if not parts:
            product_cards = soup.find_all(['div', 'article'], class_=re.compile(r'product|item', re.I))
            for card in product_cards:
                link = card.find('a', href=True)
                if link:
                    product_url = urljoin(self.base_url, link['href'])
                    product_name = link.get_text(strip=True) or card.get_text(strip=True)
                    if product_url and product_name:
                        parts.append({
                            'name': product_name,
                            'url': product_url
                        })
        
        print(f"Found {len(parts)} parts")
        return parts
    
    def _parse_json_data(self, data):
        """Parse JSON data to extract parts"""
        parts = []
        # This is a placeholder - actual implementation depends on JSON structure
        return parts
    
    def get_part_details(self, part_url):
        """Fetch detailed information about a specific part"""
        print(f"Fetching details from: {part_url}")
        response = self.get_page(part_url)
        if not response:
            return None, []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        details = {}
        pdf_urls = []
        
        # Extract product information
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
        
        # Find product specifications - adjust selectors based on actual HTML
        spec_section = soup.find(['div', 'section'], class_=re.compile(r'spec|detail|product-info', re.I))
        if spec_section:
            rows = spec_section.find_all(['tr', 'div'], class_=re.compile(r'row|item', re.I))
            for row in rows:
                label_elem = row.find(['td', 'dt', 'span'], class_=re.compile(r'label|name', re.I))
                value_elem = row.find(['td', 'dd', 'span'], class_=re.compile(r'value|data', re.I))
                
                if label_elem and value_elem:
                    label = label_elem.get_text(strip=True)
                    value = value_elem.get_text(strip=True)
                    
                    # Map to our fields
                    for key in details_fields.keys():
                        if key.lower() in label.lower():
                            details_fields[key] = value
        
        details = details_fields
        
        # Find PDF links
        pdf_links = soup.find_all('a', href=re.compile(r'\.pdf$', re.I))
        for link in pdf_links:
            pdf_url = urljoin(self.base_url, link['href'])
            pdf_urls.append(pdf_url)
        
        # Also check for download buttons or manual sections
        download_links = soup.find_all(['a', 'button'], string=re.compile(r'manual|pdf|download', re.I))
        for link in download_links:
            href = link.get('href', '')
            if '.pdf' in href.lower():
                pdf_url = urljoin(self.base_url, href)
                if pdf_url not in pdf_urls:
                    pdf_urls.append(pdf_url)
        
        return details, pdf_urls
    
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
    
    def save_part_info(self, details, filepath):
        """Save part information to a text file"""
        content = []
        for key, value in details.items():
            value_str = str(value) if value else "N/A"
            content.append(f"{key}: {value_str}")
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
        print(f"Saved info: {os.path.basename(filepath)}")
    
    def scrape_part(self, part):
        """Scrape a single part"""
        part_name = self.sanitize_filename(part['name'])
        part_folder = os.path.join(self.output_dir, part_name)
        
        # Get part details
        details, pdf_urls = self.get_part_details(part['url'])
        
        if details:
            # Save product information
            info_file = os.path.join(part_folder, 'product_info.txt')
            self.save_part_info(details, info_file)
        
        # Download PDFs
        pdf_count = 0
        for idx, pdf_url in enumerate(pdf_urls):
            pdf_filename = f"manual_{idx + 1}.pdf"
            pdf_path = os.path.join(part_folder, pdf_filename)
            if self.download_pdf(pdf_url, pdf_path):
                pdf_count += 1
        
        print(f"Scraped: {part_name} ({pdf_count} PDFs downloaded)")
        time.sleep(1)  # Be respectful
    
    def run(self, url):
        """Main scraping function"""
        print("Starting Partstown Trane Parts Scraper")
        print("=" * 50)
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Get all parts
        parts = self.extract_trane_parts(url)
        
        if not parts:
            print("No parts found. This might be due to:")
            print("1. The page uses JavaScript to load content (need Selenium)")
            print("2. The page structure is different than expected")
            print("3. The URL needs authentication or special handling")
            return
        
        # Scrape each part
        total = len(parts)
        for idx, part in enumerate(parts, 1):
            print(f"\nProcessing part {idx}/{total}")
            self.scrape_part(part)
        
        print("\n" + "=" * 50)
        print(f"Scraping complete! {total} parts processed.")


def main():
    url = "https://www.partstown.com/trane/parts#id=mdptabparts"
    scraper = PartstownScraper()
    scraper.run(url)


if __name__ == "__main__":
    main()

