from playwright.sync_api import sync_playwright
import time

def time_multiple_browsers():
    with sync_playwright() as p:
        chromium_browser = p.chromium.launch(headless=False)
        firefox_browser = p.firefox.launch(headless=False)

        chromium_page = chromium_browser.new_page()
        firefox_page = firefox_browser.new_page()

        chromium_page.goto("https://www.example.com")
        firefox_page.goto("https://www.google.com")

        time.sleep(10)

        chromium_browser.close()
        firefox_browser.close()