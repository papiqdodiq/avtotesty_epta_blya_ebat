from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context()
    page1 = context.new_page()  # Первая страница (вкладка)
    page2 = context.new_page()  # Вторая страница (вкладка)

    # ... (работаем с page1 и page2)

    context.close()
    browser.close()