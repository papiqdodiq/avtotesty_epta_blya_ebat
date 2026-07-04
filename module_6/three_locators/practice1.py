import time
from playwright.sync_api import Page, expect


def test_example(page: Page) -> None:
    page.goto('https://demoqa.com/webtables')
    page.get_by_role("button", name="Add").click()
    expect(page.locator("div").filter(has_text="Registration Form").nth(3)).to_be_visible()
    page.get_by_placeholder("First Name").fill("хуй")
    page.get_by_placeholder("Last Name").fill("хуй2")
    page.get_by_placeholder("name@example.com").fill("name3333@example.com")
    page.get_by_placeholder("Age").fill("22")
    page.get_by_placeholder("Salary").fill("13377")
    page.get_by_placeholder("Department").fill("хуйня")
    time.sleep(3)
    page.get_by_role("button", name="Submit").click()
    expect(page.get_by_role("cell", name="хуй", exact=True)).to_be_visible()
    time.sleep(3)