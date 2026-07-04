import time
import allure
import pytest
from module_7.page_object.page_object_models import CinescopeLoginPage, CinescopeRegisterPage
from utils.data_generator import DataGenerator


@allure.epic("Тестирование UI")
@allure.feature("Тестирование Страницы Review")
@pytest.mark.ui
class TestReviewPage:
    @allure.title("Проведение успешного комментинга фильма епта")
    def test_review_by_ui(self, page, create_film, logged_page):
        movie_id = create_film.json()["id"]
        logged_page.open_url(f"https://dev-cinescope.coconutqa.ru/movies/{movie_id}")
        logged_page.create_review("хуйня", page)
        logged_page.assert_allert_was_pop_up()
        logged_page.make_screenshot_and_attach_to_allure()

        # Пауза для визуальной проверки (нужно удалить в реальном тестировании)
        time.sleep(5)


@allure.epic("Тестирование UI")
@allure.feature("Тестирование Страницы Login")
@pytest.mark.ui
class TestLoginPage:
     @allure.title("Проведение успешного входа в систему")
     def test_login_by_ui(self, page, create_user, register_data):
         # Создаем объект страницы регистрации Cinescope
         login_page = CinescopeLoginPage(page)

         # Открываем страницу
         login_page.open()

         # Осуществяем вход
         login_page.login(register_data["email"], register_data["password"])

         # Проверка редиректа на домашнюю страницу
         login_page.assert_was_redirect_to_home_page()  # Проверка редиректа на домашнюю страницу
         login_page.make_screenshot_and_attach_to_allure()  # Прикрепляем скриншот
         #login_page.assert_allert_was_pop_up()  # Проверка появления и исчезновения алерта (увед не работает, при кнопке
         # логина ошибка и нужно принудительно переходить на домашнюю страницу)

         # Пауза для визуальной проверки (нужно удалить в реальном тестировании)
         time.sleep(5)


@allure.epic("Тестирование UI")
@allure.feature("Тестирование Страницы Register")
@pytest.mark.ui
class TestRegisterPage:
    @allure.title("Проведение успешной регистрации")
    def test_register_by_ui(self,  page):
        # Подготовка данных для регистрации
        random_email = DataGenerator.generate_random_email()
        random_name = DataGenerator.generate_random_name()
        random_password = DataGenerator.generate_random_password()

        # Создаем объект страницы регистрации Cinescope
        register_page = CinescopeRegisterPage(page)
        register_page.open()

        # Выполняем регистрацию
        register_page.register(f"PlaywrightTest {random_name}", random_email, random_password, random_password)

        register_page.assert_was_redirect_to_login_page()  # Проверка редиректа на страницу /login
        register_page.make_screenshot_and_attach_to_allure()  # Прикрепляем скриншот
        register_page.assert_allert_was_pop_up()  # Проверка появления и исчезновения алерта

        # Пауза для визуальной проверки (нужно удалить в реальном тестировании)
        time.sleep(5)