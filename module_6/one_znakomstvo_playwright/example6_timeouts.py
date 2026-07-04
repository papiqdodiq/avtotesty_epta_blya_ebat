import pytest


def test_search_product(page):
    page.goto('https://www.example.com')  # Глобальный таймаут (из фикстуры context)

    page.fill('input#search', 'Playwright', timeout=5000)  # Локальный таймаут для заполнения поля

    page.click('button#search-button')  # Глобальный таймаут

    page.wait_for_selector('.results', state='visible', timeout=10000)  # Локальный таймаут для ожидания результатов поиска

    assert page.locator('.results').count() > 0

@pytest.mark.timeout(120000)  # Устанавливаем таймаут для всего теста 2 минуты
def test_long_process(page):
    # ... код теста, выполняющийся длительное время
    pass