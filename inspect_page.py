"""
Quick utility to inspect the Partstown page structure
This helps determine which scraper approach to use
"""
import requests
from bs4 import BeautifulSoup


def inspect_page(url):
    """Inspect the page structure"""
    print(f"Inspecting: {url}\n")
    print("=" * 80)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}\n")
        
        if response.status_code != 200:
            print(f"Error: Could not fetch page")
            return
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check for JavaScript-heavy content
        scripts = soup.find_all('script')
        print(f"Found {len(scripts)} script tags")
        
        # Look for product-related elements
        print("\n--- Looking for product links ---")
        product_links = soup.find_all('a', href=lambda x: x and '/trane/parts/' in x)
        print(f"Found {len(product_links)} links containing '/trane/parts/'")
        if product_links:
            print("\nFirst few links:")
            for link in product_links[:5]:
                print(f"  - {link.get_text(strip=True)[:50]} -> {link.get('href')}")
        
        # Check for data attributes
        print("\n--- Checking for data attributes ---")
        data_attrs = soup.find_all(attrs={'data-product': True})
        print(f"Found {len(data_attrs)} elements with data-product attribute")
        
        # Check for specific classes
        print("\n--- Common product-related classes ---")
        common_classes = ['product', 'item', 'card', 'listing']
        for class_name in common_classes:
            elements = soup.find_all(class_=lambda x: x and class_name in str(x).lower())
            print(f"Found {len(elements)} elements with '{class_name}' in class")
        
        # Save full HTML for manual inspection
        with open('page_source.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("\nFull page HTML saved to: page_source.html")
        
        print("\n" + "=" * 80)
        print("RECOMMENDATION:")
        if len(product_links) > 10:
            print("✓ Good! Found product links. Basic scraper should work.")
        else:
            print("✗ Few product links found. May need Selenium scraper.")
        
    except Exception as e:
        print(f"Error inspecting page: {e}")


if __name__ == "__main__":
    url = "https://www.partstown.com/trane/parts#id=mdptabparts"
    inspect_page(url)

