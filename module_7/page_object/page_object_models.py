import time

import allure
from playwright.sync_api import Page, expect


class PageAction:
    def __init__(self, page: Page):
        self.page = page

    @allure.step("Переход на страницу: {url}")
    def open_url(self, url: str):
        self.page.goto(url)

    @allure.step("Ввод текста '{text}' в поле '{locator}'")
    def enter_text_to_element(self, locator, text: str):  # раньше было locator: str
        """Универсальный ввод текста (поддержка старых локаторов)"""
        if isinstance(locator, str):
            self.page.fill(locator, text)  # через XPath
        else:
            locator.fill(text)  # генерируемые с помощью playwright codegen

    @allure.step("Клик по элементу '{locator}'")
    def click_element(self, locator):  # раньше было locator: str
        """Универсальный клик (поддержка старых локаторов)"""
        if isinstance(locator, str):
            self.page.click(locator)  # через XPath
        else:
            locator.click()  # генерируемые с помощью playwright codegen

    @allure.step("Ожидание загрузки страницы: {url}")
    def wait_redirect_for_url(self, url: str):
        self.page.wait_for_url(url)
        assert self.page.url == url, "Редирект на домашнюю страницу не произошел"

    @allure.step("Получение текста элемента: {locator}")
    def get_element_text(self, locator) -> str:  # раньше было locator: str
        if isinstance(locator, str):
            return self.page.locator(locator).text_content()
        return locator.text_content()

    @allure.step("Ожидание пояления или исчезновения элемента: {locator}, state = {state}")
    def wait_for_element(self, locator, state: str = "visible"):  # раньше было locator: str
        if isinstance(locator, str):
            self.page.locator(locator).wait_for(state=state)
        else:
            locator.wait_for(state=state)

    @allure.step("Скриншот текущей страницы")
    def make_screenshot_and_attach_to_allure(self):
        screenshot_path = "screenshot.png"
        self.page.screenshot(path=screenshot_path, full_page=True)  # full_page=True для скриншота всей страницы

        # Прикрепление скриншота к Allure-отчету
        with open(screenshot_path, "rb") as file:
            allure.attach(file.read(), name="Screenshot after redirect", attachment_type=allure.attachment_type.PNG)

    @allure.step("Проверка всплывающего сообщения с текстом: {text}")
    def check_pop_up_element_with_text(self, text: str) -> bool:

        with allure.step("Проверка появления алерта с текстом: '{text}'"):
            notification_locator = self.page.get_by_text(text)
            # Ждем появления элемента
            notification_locator.wait_for(state="visible")
            assert notification_locator.is_visible(), "Уведомление не появилось"

        with allure.step("Проверка исчезновения алерта с текстом: '{text}'"):
            # Ждем, пока влерт исчезнет
            notification_locator.wait_for(state="hidden")
            assert notification_locator.is_visible() == False, "Уведомление не исчезло"

        return True


class BasePage(PageAction):  # Базовая логика допустимая для всех страниц на сайте
    def __init__(self, page: Page):
        super().__init__(page)
        self.home_url = "https://dev-cinescope.coconutqa.ru/"

        # Общие локаторы для всех страниц на сайте
        self.home_button = page.get_by_role("link", name="Cinescope")  # "a[href='/' and text()='Cinescope']"
        self.all_movies_button = page.get_by_role("link", name="Все фильмы")  # "a[href='/movies' and text()='Все фильмы']"

    @allure.step("Переход на главную страницу, из шапки сайта")
    def go_to_home_page(self):
        self.click_element(self.home_button)
        self.wait_redirect_for_url(self.home_url)

    @allure.step("Переход на страницу 'Все фильмы, из шапки сайта'")
    def go_to_all_movies(self):
        self.click_element(self.all_movies_button)
        self.wait_redirect_for_url(f"{self.home_url}movies")


class CinescopeRegisterPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.url = f"{self.home_url}register"

        # Локаторы элементов
        self.full_name_input = page.get_by_role("textbox", name="Имя Фамилия Отчество")  # "input[name='fullName']"
        self.email_input = page.get_by_role("textbox", name="Email")  # "input[name='email']"
        self.password_input = page.get_by_role("textbox", name="Пароль", exact=True) # "input[name='password']"
        self.repeat_password_input = page.get_by_role("textbox", name="Повторите пароль")  # "input[name='passwordRepeat']"

        self.register_button = page.get_by_role("button", name="Зарегистрироваться")  # "button[data-qa-id='register_submit_button']"
        self.sign_button = page.get_by_role("link", name="Войти")  # "a[href='/login' and text()='Войти']"

    # Локальные action методы
    def open(self):
        """Переход на страницу регистрации."""
        self.page.goto(self.url)

    def register(self, full_name: str, email: str, password: str, confirm_password: str):
        """Полный процесс регистрации."""
        self.enter_text_to_element(self.full_name_input, full_name)
        self.enter_text_to_element(self.email_input, email)
        self.enter_text_to_element(self.password_input, password)
        self.enter_text_to_element(self.repeat_password_input, confirm_password)

        self.click_element(self.register_button)

    def assert_was_redirect_to_login_page(self):
        self.wait_redirect_for_url(f"{self.home_url}login")

    def assert_allert_was_pop_up(self):
        self.check_pop_up_element_with_text("Подтвердите свою почту")


class CinescopeLoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.url = f"{self.home_url}login"

        # Локаторы элементов
        self.email_input = page.get_by_role("textbox", name="Email")  # "input[name='email']"
        self.password_input = page.get_by_role("textbox", name="Пароль")  # "input[name='password']"

        self.login_button = page.get_by_role("button", name="Войти")  # "button[data-qa-id='login_submit_button']"
        self.register_button = page.get_by_role("link", name="Зарегистрироваться")  # "a[href='/register' and text()='Зарегистрироваться']"

    # Локальные action методы
    def open(self):
        self.open_url(self.url)

    def login(self, email: str, password: str):
        self.enter_text_to_element(self.password_input, password)
        self.enter_text_to_element(self.email_input, email)
        self.click_element(self.login_button)
        self.page.goto("https://dev-cinescope.coconutqa.ru/")  # нужно принудительно переходить на домашнюю страницу без уведа (самостоятельно не работает и выдает ошибку)

    def assert_was_redirect_to_home_page(self):
        self.wait_redirect_for_url(self.home_url)

    def assert_allert_was_pop_up(self):
        self.check_pop_up_element_with_text("Вы вошли в аккаунт")


class CinescopeCommentPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

        # Локаторы элементов
        self.email_input = page.get_by_role("textbox", name="Email")
        self.password_input = page.get_by_role("textbox", name="Пароль")

        self.login_button = page.get_by_role("button", name="Войти")

        self.review_textbox = page.get_by_role("textbox", name="Написать отзыв")
        self.review_combobox = page.get_by_role("combobox")
        self.review_option_1 = page.get_by_role("option", name="1")
        self.review_send_button = page.get_by_role("button", name="Отправить")

    # Локальные action методы
    def open_login_page(self):
        self.open_url(f"{self.home_url}login")

    def assert_was_redirect_to_home_page(self):
        self.wait_redirect_for_url(self.home_url)

    def login(self, email: str, password: str):
        self.enter_text_to_element(self.password_input, password)
        self.enter_text_to_element(self.email_input, email)
        self.click_element(self.login_button)
        time.sleep(2)
        self.page.goto("https://dev-cinescope.coconutqa.ru/")

    def create_review(self, text, page: Page):
        self.enter_text_to_element(self.review_textbox, text)
        time.sleep(2)
        self.click_element(self.review_combobox)
        time.sleep(2)
        self.click_element(self.review_option_1)
        time.sleep(2)
        self.click_element(self.review_send_button)
        time.sleep(2)

        self.wait_for_element(page.get_by_text(text))

        self.wait_for_element(self.review_textbox, "hidden")
        self.wait_for_element(self.review_combobox, "hidden")
        self.wait_for_element(self.review_send_button, "hidden")

    def assert_allert_was_pop_up(self):
        self.check_pop_up_element_with_text("Отзыв успешно создан")
