from playwright.sync_api import sync_playwright
import time

# Создаем экземпляр Playwright и запускаем его
playwright = sync_playwright().start()

# Далее, используя объект playwright, можно запускать браузер и работать с ним
browser = playwright.chromium.launch(headless=False, slow_mo=50)
# На первых порах передавать параметр slow_mo=50, чтобы была небольшая задержка между всеми действиями,
# чтобы можно было разглядеть более детально что происходит
page = browser.new_page()
page.goto('https://demoqa.com/')
time.sleep(10) # Сделаем sleep иначе браузер сразу закроется перейдя к следующим строкам

# После выполнения необходимых действий, следует явно закрыть браузер
browser.close()

# И остановить Playwright, чтобы освободить ресурсы
playwright.stop()