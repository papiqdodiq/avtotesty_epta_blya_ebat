from playwright.sync_api import expect
import time


def test_run(page):
    page.goto("https://demoqa.com/text-box")
    page.get_by_role("textbox", name="Full Name").click()
    page.get_by_role("textbox", name="Full Name").fill("Абобий абобович")
    page.get_by_role("textbox", name="name@example.com").click()
    page.get_by_role("textbox", name="name@example.com").fill("kaka@mail.ru")
    page.get_by_role("textbox", name="Current Address").click()
    page.get_by_role("textbox", name="Current Address").fill("абобияново")
    page.locator("#permanentAddress").click()
    page.locator("#permanentAddress").fill("абобияново")
    page.get_by_role("button", name="Submit").click()
    # page.pause()  # включает плейврайтовский девтулс
    expect(page.locator("#name")).to_contain_text("Name:Абобий абобович")
    expect(page.locator("#email")).to_contain_text("Email:kaka@mail.ru")
    expect(page.locator("#output")).to_contain_text("Current Address :абобияново")
    expect(page.locator("#output")).to_contain_text("Permananet Address :абобияново")

    time.sleep(3)


'''
Данный способ создания тестов не рекомендую. Да, возможно быстрые решения для критичных моментов и можно использовать 
или для исследования локаторов. Но есть поговорка - нет ничего более постоянного, чем временное. 
Лучше сразу держать тесты в порядке!

Первое время можно использовать для определения локаторов, особенно ARIA локаторов.
'''