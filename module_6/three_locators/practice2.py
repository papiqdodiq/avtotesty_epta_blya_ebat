from datetime import datetime
from playwright.sync_api import Page, expect


def test_example(page: Page) -> None:
    page.goto("https://demoqa.com/automation-practice-form")
    page.get_by_role("textbox", name="First Name").fill("яйца")
    page.get_by_role("textbox", name="Last Name").fill("блянах")
    page.get_by_role("textbox", name="name@example.com").fill("huy@mail.ru")
    page.get_by_role("radio", name="Male", exact=True).check()
    page.get_by_role("textbox", name="Mobile Number").fill("8957583740")

    # Проверка на совпадение с текущей датой
    date = page.get_attribute("#dateOfBirthInput", "value")
    today = datetime.now().strftime("%d %b %Y")
    assert date == today, f"Дата не совпадает: {date} != {today}"

    # Ищем элемент, берем из него значение и сравниваем с тем, что нужно
    text = page.locator("#root footer span").text_content()
    assert text == "© 2013-2026 TOOLSQA.COM | ALL RIGHTS RESERVED."

    page.locator("#dateOfBirthInput").click()
    page.get_by_role("gridcell", name="Choose Tuesday, June 23rd,").click()
    page.locator("#subjectsInput").fill("хуйня + хуйня")
    page.get_by_role("checkbox", name="Sports").check()
    page.get_by_role("textbox", name="Current Address").fill("колотушкино")
    page.locator("#state svg").click()
    page.get_by_role("option", name="NCR").click()
    page.get_by_role("button", name="Submit").click()