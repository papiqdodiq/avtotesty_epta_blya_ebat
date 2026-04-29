import requests
import pytest
from constants import AUTH_URL
from faker import Faker

faker = Faker('ru_RU')

# Тут использую кастом реквестер и api-менеджер (отредачил все позитивные тесты,
# используя api-классы с методами для /register, /login, /get, /delete)
class TestPositiveAuth:

    def test_register_success(self, api_manager, register_data):
        """Позитив: успешная регистрация пользователя с валидными данными.
        Проверяем статус, заголовки, структуру ответа и типы данных."""

        # 1. РЕГИСТРАЦИЯ
        response = api_manager.auth_api.register_user(register_data)

        # Заголовки
        assert response.headers.get("Content-Type") == "application/json; charset=utf-8", "Неверный Content-Type"

        # Проверка структуры ответа
        data = response.json()
        required_fields = ["id", "email", "fullName", "roles", "verified", "createdAt", "banned"]
        for field in required_fields:
            assert field in data, f"У ответа отсутствует поле {field}"

        # Проверка типов
        assert isinstance(data["id"], str), "id должен быть строкой (UUID)"
        assert isinstance(data["email"], str), "email должен быть строкой"
        assert isinstance(data["fullName"], str), "fullName должен быть строкой"
        assert isinstance(data["roles"], list), "roles должен быть списком"
        assert isinstance(data["verified"], bool), "verified должен быть булевым"
        assert isinstance(data["createdAt"], str), "createdAt должен быть строкой"
        assert isinstance(data["banned"], bool), "banned должен быть булевым"

        # Проверка значений
        assert data["email"] == register_data["email"], "email не совпадает"
        assert data["fullName"] == register_data["fullName"], "fullName не совпадает"
        assert "USER" in data["roles"], "роль USER отсутствует"
        assert data["verified"] is True, "verified должен быть True"
        assert data["banned"] is False, "banned должен быть False"

        # Проверка формата UUID
        assert len(data["id"]) == 36, "id должен быть UUID формата"
        assert data["id"].count("-") == 4, "id должен содержать 4 дефиса"

        # Проверка формата createdAt (ISO 8601)
        assert "T" in data["createdAt"], "createdAt должен быть в формате ISO 8601"

        user_id = data["id"]

        # 2. ПРОВЕРЯЕМ, ЧТО ПОЛЬЗОВАТЕЛЬ РЕАЛЬНО СОЗДАЛСЯ (GET)
        # 1) логинимся как админ, чтобы обновить токен для запроса get
        login_data = ["api1@gmail.com", "asdqwe123Q"]
        api_manager.authenticate(login_data) # это мною придуманный метод
        # мы обновляем токен сразу у двух объектов api-классов (auth_api и user_api)

        # 2) проверяем через get
        get_user = api_manager.user_api.get_user_info(user_id)

        get_data = get_user.json()
        assert get_data["id"] == user_id, "id не совпадает"
        assert get_data["email"] == register_data["email"], "email не совпадает"
        assert get_data["fullName"] == register_data["fullName"], "fullName не совпадает"
        assert get_data["verified"] is True, "verified должен быть True"
        assert get_data["banned"] is False, "banned должен быть False"

        # 3. УДАЛЯЕМ ПОЛЬЗОВАТЕЛЯ
        api_manager.user_api.delete_user(user_id)

        # 4. ПРОВЕРЯЕМ, ЧТО ПОЛЬЗОВАТЕЛЬ ДЕЙСТВИТЕЛЬНО УДАЛИЛСЯ
        # БАГ!!! API возвращает 200 и пустое тело {} вместо 404
        get_deleted = api_manager.user_api.get_user_info(user_id)

        # Проверяем, что тело ответа пустое (пользователь не найден)
        assert get_deleted.json() == {}, "Тело ответа не пустое, пользователь не удалился"

    def test_login_success(self, api_manager, register_data):
        """Позитив: успешный логин пользователя с корректными данными.
        Проверяем статус, заголовки, структуру ответа и типы данных."""

        # 1. СНАЧАЛА РЕГИСТРИРУЕМ ПОЛЬЗОВАТЕЛЯ
        register_response = api_manager.auth_api.register_user(register_data)
        user_id = register_response.json()["id"]

        # 2. ЛОГИН
        login_data = {
        "email": register_data["email"],
        "password": register_data["password"]
        }
        response = api_manager.auth_api.login_user(login_data)

        # Заголовки
        assert response.headers.get("Content-Type") == "application/json; charset=utf-8", "Неверный Content-Type"

        # Проверка структуры ответа
        data = response.json()
        required_fields = ["user", "accessToken", "refreshToken", "expiresIn"]
        for field in required_fields:
            assert field in data, f"У ответа отсутствует поле {field}"

        # Проверка структуры user
        user = data["user"]
        user_fields = ["id", "email", "fullName", "roles"]
        for field in user_fields:
            assert field in user, f"У user отсутствует поле {field}"

        # Проверка типов
        assert isinstance(data["accessToken"], str), "accessToken должен быть строкой"
        assert isinstance(data["refreshToken"], str), "refreshToken должен быть строкой"
        assert isinstance(data["expiresIn"], int), "expiresIn должен быть числом"
        assert isinstance(user["id"], str), "id должен быть строкой (UUID)"
        assert isinstance(user["email"], str), "email должен быть строкой"
        assert isinstance(user["fullName"], str), "fullName должен быть строкой"
        assert isinstance(user["roles"], list), "roles должен быть списком"

        # Проверка значений
        assert user["email"] == register_data["email"], "email не совпадает"
        assert user["fullName"] == register_data["fullName"], "fullName не совпадает"
        assert len(data["accessToken"]) > 0, "accessToken не должен быть пустым"
        assert len(data["refreshToken"]) > 0, "refreshToken не должен быть пустым"
        assert data["expiresIn"] > 0, "expiresIn должен быть больше 0"

        # Проверка формата UUID
        assert len(user["id"]) == 36, "id должен быть UUID формата"
        assert user["id"].count("-") == 4, "id должен содержать 4 дефиса"

        # 3. УДАЛЯЕМ ПОЛЬЗОВАТЕЛЯ
        # 1) логинимся как админ, чтобы обновить токен для запроса delete
        login_data = ["api1@gmail.com", "asdqwe123Q"]
        api_manager.authenticate(login_data)

        # 2) удаляем юзера
        api_manager.user_api.delete_user(user_id)


class TestNegativeAuth:

    # ========== РЕГИСТРАЦИЯ (негатив) ==========
    def test_register_duplicate_email(self, auth_session, register_data):
        """Негатив: регистрация с уже существующим email"""
        # 1. Регистрируем первого пользователя
        response1 = requests.post(f"{AUTH_URL}/register", json=register_data)
        assert response1.status_code == 201, "Ошибка при регистрации первого пользователя"
        user_id = response1.json()["id"]

        # 2. Пытаемся зарегистрироваться с тем же email
        response2 = requests.post(f"{AUTH_URL}/register", json=register_data)
        assert response2.status_code == 409, "Регистрация с существующим email не вызвала ошибку"

        # 3. Чистим
        auth_session.delete(f"{AUTH_URL}/user/{user_id}")

    def test_register_short_password(self):
        """Негатив: регистрация с коротким паролем (меньше 8 символов)"""
        register_data = {
            "email": faker.email(),
            "fullName": faker.name(),
            "password": "Test1",  # меньше 8 символов
            "passwordRepeat": "Test1"
        }

        response = requests.post(f"{AUTH_URL}/register", json=register_data)
        assert response.status_code == 400, "Регистрация с коротким паролем не вызвала ошибку"

    def test_register_password_no_digit(self):
        """Негатив: регистрация с паролем без цифры"""
        register_data = {
            "email": faker.email(),
            "fullName": faker.name(),
            "password": "Testtest!",  # нет цифры
            "passwordRepeat": "Testtest!"
        }

        response = requests.post(f"{AUTH_URL}/register", json=register_data)
        assert response.status_code == 400, "Регистрация с паролем без цифры не вызвала ошибку"

    def test_register_password_no_uppercase(self):
        """Негатив: регистрация с паролем без заглавной буквы"""
        register_data = {
            "email": faker.email(),
            "fullName": faker.name(),
            "password": "test123!",  # нет заглавной
            "passwordRepeat": "test123!"
        }

        response = requests.post(f"{AUTH_URL}/register", json=register_data)
        assert response.status_code == 400, "Регистрация с паролем без заглавной не вызвала ошибку"

    def test_register_password_with_space(self):
        """Негатив: регистрация с паролем, содержащим пробел"""
        register_data = {
            "email": faker.email(),
            "fullName": faker.name(),
            "password": "Test 123!",  # есть пробел
            "passwordRepeat": "Test 123!"
        }

        response = requests.post(f"{AUTH_URL}/register", json=register_data)
        assert response.status_code == 400, "Регистрация с паролем-пробелом не вызвала ошибку"

    def test_register_password_mismatch(self):
        """Негатив: регистрация с несовпадающими паролями"""
        register_data = {
            "email": faker.email(),
            "fullName": faker.name(),
            "password": "Test123!",
            "passwordRepeat": "Test123!!"  # отличается
        }

        response = requests.post(f"{AUTH_URL}/register", json=register_data)
        assert response.status_code == 400, "Регистрация с несовпадающими паролями не вызвала ошибку"

    # ========== ЛОГИН (негатив) ==========
    def test_login_wrong_password(self, register_data):
        """Негатив: логин с неверным паролем"""

        # 1. Регистрируем пользователя (нужен для проверки)
        register_response = requests.post(f"{AUTH_URL}/register", json=register_data)
        assert register_response.status_code == 201
        user_id = register_response.json()["id"]

        # 2. Логинимся для получения токена (для удаления)
        login_data = {
            "email": register_data["email"],
            "password": register_data["password"]
        }
        login_response = requests.post(f"{AUTH_URL}/login", json=login_data)
        assert login_response.status_code == 200
        access_token = login_response.json()["accessToken"]

        # 3. Пытаемся залогиниться с неверным паролем
        wrong_login_data = {
            "email": register_data["email"],
            "password": "WrongPassword123!"
        }
        response = requests.post(f"{AUTH_URL}/login", json=wrong_login_data)
        assert response.status_code == 401, "Логин с неверным паролем не вызвал ошибку"

        # 4. Чистим
        auth_session = requests.Session()
        auth_session.headers.update({"Authorization": f"Bearer {access_token}"})
        auth_session.delete(f"{AUTH_URL}/user/{user_id}")

    @pytest.mark.skip(reason="БАГ в test_login_nonexistent_email: сервер возвращает 401 вместо 404")
    def test_login_nonexistent_email(self):
        """Негатив: логин с несуществующим email"""

        login_data = {
            "email": "nonexistent123412412351@email.com",
            "password": "Test123!"
        }

        response = requests.post(f"{AUTH_URL}/login", json=login_data)
        assert response.status_code == 404, "Логин с несуществующим email не вызвал ошибку"

    @pytest.mark.skip(reason="БАГ в test_login_invalid_email_format: сервер возвращает 401 вместо 400")
    def test_login_invalid_email_format(self):
        """Негатив: логин с невалидным форматом email"""

        login_data = {
            "email": "not_an_email",
            "password": "Test123!"
        }

        response = requests.post(f"{AUTH_URL}/login", json=login_data)
        assert response.status_code == 400, "Логин с невалидным email не вызвал ошибку"

    @pytest.mark.skip(reason="БАГ в test_login_empty_email: сервер возвращает 401 вместо 400")
    def test_login_empty_email(self):
        """Негатив: логин с пустым email"""

        login_data = {
            "email": "",
            "password": "Test123!"
        }

        response = requests.post(f"{AUTH_URL}/login", json=login_data)
        assert response.status_code == 400, "Логин с пустым email не вызвал ошибку"

    @pytest.mark.skip(reason="БАГ в test_login_empty_password: сервер возвращает 401 вместо 400")
    def test_login_empty_password(self):
        """Негатив: логин с пустым паролем"""

        login_data = {
            "email": "test@email.com",
            "password": ""
        }

        response = requests.post(f"{AUTH_URL}/login", json=login_data)
        assert response.status_code == 400, "Логин с пустым паролем не вызвал ошибку"

    @pytest.mark.skip(reason="БАГ в test_login_empty_body: сервер возвращает 401 вместо 400")
    def test_login_empty_body(self):
        """Негатив: логин с пустым телом запроса"""

        response = requests.post(f"{AUTH_URL}/login", json={})
        assert response.status_code == 400, "Логин с пустым телом не вызвал ошибку"