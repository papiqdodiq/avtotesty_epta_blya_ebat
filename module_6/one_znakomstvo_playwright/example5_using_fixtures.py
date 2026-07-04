import time


def test_example(page):  # page автоматически будет предоставлена фикстурой
    page.goto("https://www.example.com")

def test_google(page):  # page автоматически будет предоставлена фикстурой
    page.goto("https://www.google.com")

def test_some_entities(page):
    page.goto('https://demoqa.com')
    time.sleep(10)