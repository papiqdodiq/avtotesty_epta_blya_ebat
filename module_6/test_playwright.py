from playwright.sync_api import sync_playwright

def test_browser():
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False)  # headless=True - без окна браузера
        page = browser.new_page()
        page.goto("https://example.com")
        print(f"✅ Страница загружена, заголовок: {page.title()}")
        browser.close()

if __name__ == "__main__":
    test_browser()