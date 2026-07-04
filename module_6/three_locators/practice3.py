import time
from playwright.sync_api import Page, expect


def test_example(page: Page) -> None:
    page.goto('https://demoqa.com/radio-button')
    page.is_enabled("#yesRadio")
    page.is_enabled("#impressiveRadio")
    page.is_disabled("#noRadio")

def test_example2(page: Page) -> None:
    page.goto('https://demoqa.com/checkbox')
    expect(page.get_by_text("Home")).to_be_visible()
    time.sleep(1)
    page.is_hidden(".rc-tree-title")
    time.sleep(1)
    page.locator(".rc-tree-switcher").click()
    time.sleep(1)
    expect(page.get_by_text("Desktop")).to_be_visible()

def test_example3(page: Page) -> None:
    page.goto('https://demoqa.com/dynamic-properties')
    page.is_hidden("#visibleAfter")
    page.wait_for_selector("#visibleAfter", state='visible', timeout=5500)
    time.sleep(1)