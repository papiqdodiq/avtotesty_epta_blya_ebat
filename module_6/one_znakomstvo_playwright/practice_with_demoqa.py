from playwright.sync_api import Page, expect
import time

def test_text_box(page: Page):
    page.goto('https://demoqa.com/text-box')

    # вариант №1
    username_locator = '#userName'
    page.fill(username_locator, 'testQa')

    # вариант №2
    # page.locator('#userName').fill('testQa')

    # вариант №3
    # page.fill(selector='#userName', value='testQa')

    page.fill(selector='#userEmail', value='aboba@mail.ru')

    page.fill(selector='#currentAddress', value='Обводный пр-т 40')

    page.fill(selector='#permanentAddress', value='Обводный пр-т 40')

    time.sleep(3)

    page.click('button#submit')

    time.sleep(3)

    expect(page.locator('#output #name')).to_have_text('Name:testQa')
    expect(page.locator('#output #email')).to_have_text('Email:aboba@mail.ru')
    expect(page.locator('#output #currentAddress')).to_have_text('Current Address :Обводный пр-т 40')
    expect(page.locator('#output #permanentAddress')).to_have_text('Permananet Address :Обводный пр-т 40')

    time.sleep(3)

def test_text_box2(page):
    page.goto("https://demoqa.com/elements")
    page.get_by_role("link", name="Check Box").click()
    page.get_by_role("link", name="Radio Button").click()
    page.get_by_role("link", name="Web Tables").click()
    page.get_by_role("cell", name="Cierra", exact=True).click()
    page.get_by_role("cell", name="Alden", exact=True).click()
    page.get_by_role("cell", name="Kierra", exact=True).click()
    expect(page.locator("tbody")).to_contain_text("Alden")
    page.get_by_role("cell", name="Cantrell").click()
    expect(page.locator("tbody")).to_contain_text("Cantrell")