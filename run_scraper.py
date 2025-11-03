#!/usr/bin/env python3
"""
Quick runner for the Partstown scraper
This script provides a simple interface to run the scraper
"""
import sys
import os


def print_header():
    """Print a nice header"""
    print("\n" + "=" * 70)
    print("PARTSTOWN TRANE PARTS SCRAPER")
    print("=" * 70 + "\n")


def print_menu():
    """Print the main menu"""
    print("Choose a scraper:")
    print("1. Test Connection (recommended first)")
    print("2. Selenium Scraper (for JavaScript-heavy sites)")
    print("3. Basic Scraper (BeautifulSoup - faster but may not work)")
    print("4. Quit")
    print()


def run_test_connection():
    """Run the test connection script"""
    print("\nRunning test connection...")
    print("-" * 70)
    os.system("python3 test_connection.py")


def run_selenium_scraper():
    """Run the Selenium scraper"""
    print("\nStarting Selenium scraper...")
    print("-" * 70)
    print("This will scrape all Trane parts and their PDFs.")
    print("The browser may open in a window so you can see progress.")
    print()
    response = input("Continue? (y/n): ").strip().lower()
    if response == 'y':
        # Ask for PDF extraction preference
        print("\n" + "-" * 70)
        print("PDF EXTRACTION OPTION")
        print("-" * 70)
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
            
            # Pass the option via environment variable or modify the script
            import subprocess
            import sys
            # Modify the call to pass the unique_pdfs option
            from scraper_selenium import PartstownScraperSelenium
            url = "https://www.partstown.com/trane/parts#id=mdptabparts"
            scraper = PartstownScraperSelenium(unique_pdfs=unique_pdfs)
            scraper.run(url)
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled.")
            return
        except Exception as e:
            print(f"\nError: {e}")
            return
    else:
        print("Cancelled.")


def run_basic_scraper():
    """Run the basic scraper"""
    print("\nStarting basic scraper...")
    print("-" * 70)
    print("Note: This may not work if the site uses heavy JavaScript.")
    print()
    response = input("Continue? (y/n): ").strip().lower()
    if response == 'y':
        os.system("python3 scraper.py")
    else:
        print("Cancelled.")


def main():
    """Main menu loop"""
    print_header()
    
    while True:
        print_menu()
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == '1':
            run_test_connection()
        elif choice == '2':
            run_selenium_scraper()
        elif choice == '3':
            run_basic_scraper()
        elif choice == '4':
            print("\nGoodbye!")
            sys.exit(0)
        else:
            print("\nInvalid choice. Please enter 1-4.")
        
        print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye!")
        sys.exit(0)

