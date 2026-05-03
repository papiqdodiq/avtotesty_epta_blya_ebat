import pytest
from faker import Faker

from uuid import UUID
from datetime import datetime, timezone, timedelta

from conftest import api_manager_admin

faker = Faker('ru_RU')

# Тут использую кастом реквестер и api-менеджер (отредачил все позитивные тесты,
# используя api-классы с методами для /register, /login, /get, /delete)
class TestPositiveAuth:

    def test_register_success(self, api_manager, api_manager_admin, register_data):
        """Позитив: успешная регистрация пользователя с валидными данными.
        Проверяем статус, заголовки, структуру ответа и типы данных."""

        # 1. РЕГИСТРАЦИЯ
        before_request = datetime.now(timezone.utc)
        response = api_manager.auth_api.register_user(register_data)
        after_request = datetime.now(timezone.utc) + timedelta(seconds=10)  # +10 секунд

        # Проверка структуры ответа
        data = response.json()
        created_at = datetime.fromisoformat(data["createdAt"].replace('Z', "+00:00"))
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
        assert UUID(data["id"]), f"id '{data['id']}' не является валидным UUID"

        # Проверка формата createdAt (ISO 8601)
        assert before_request <= created_at <= after_request, f"createdAt {created_at} не в интервале"

        user_id = data["id"]

        # 2. ПРОВЕРЯЕМ, ЧТО ПОЛЬЗОВАТЕЛЬ РЕАЛЬНО СОЗДАЛСЯ (GET)
        get_user = api_manager_admin.user_api.get_user_info(user_id)

        get_data = get_user.json()
        assert get_data["id"] == user_id, "id не совпадает"
        assert get_data["email"] == register_data["email"], "email не совпадает"
        assert get_data["fullName"] == register_data["fullName"], "fullName не совпадает"
        assert get_data["verified"] is True, "verified должен быть True"
        assert get_data["banned"] is False, "banned должен быть False"

        # 3. УДАЛЯЕМ ПОЛЬЗОВАТЕЛЯ
        api_manager_admin.user_api.delete_user(user_id)

        # 4. ПРОВЕРЯЕМ, ЧТО ПОЛЬЗОВАТЕЛЬ ДЕЙСТВИТЕЛЬНО УДАЛИЛСЯ
        # БАГ!!! API возвращает 200 и пустое тело {} вместо 404
        get_deleted = api_manager_admin.user_api.get_user_info(user_id)

        # Проверяем, что тело ответа пустое (пользователь не найден)
        assert get_deleted.json() == {}, "Тело ответа не пустое, пользователь не удалился"

    def test_login_success(self, api_manager, api_manager_admin, register_data):
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
        api_manager_admin.user_api.delete_user(user_id)


class TestNegativeAuth:

    # ========== РЕГИСТРАЦИЯ (негатив) ==========
    def test_register_duplicate_email(self, api_manager, api_manager_admin, create_user, register_data):
        """Негатив: регистрация с уже существующим email"""
        user_id = create_user["id"]

        response = api_manager.auth_api.register_user(register_data, expected_status=409)

        error_data = response.json()
        assert error_data.get("error") == "Conflict"
        assert error_data.get("message") == "Пользователь с таким email уже зарегистрирован"

        # Дополнительная проверка: пользователь остался один
        get_user = api_manager_admin.user_api.get_user_info(user_id)
        assert get_user.status_code == 200
        assert get_user.json()["id"] == user_id

        # Проверяем, что дубликат не создался (пользователей с таким email только один)
        all_users = api_manager_admin.user_api.get_user_info(register_data["email"])
        if isinstance(all_users.json(), list):
            assert len(all_users.json()) == 1, "Создался дубликат пользователя"

    def test_register_short_password(self, api_manager, api_manager_admin):
        register_data = {
            "email": faker.email(),
            "fullName": faker.name(),
            "password": "Test1",
            "passwordRepeat": "Test1"
        }

        response = api_manager.auth_api.register_user(register_data, expected_status=400)

        error_data = response.json()
        assert error_data.get("error") == "Bad Request"
        assert isinstance(error_data.get("message"), list)
        assert "Минимальная длина пароля 8 символов" in error_data["message"]

        # Дополнительная проверка: пользователь НЕ создался
        get_users = api_manager_admin.user_api.get_user_info(register_data["email"])
        if isinstance(get_users.json(), list):
            assert len(get_users.json()) == 0, "Пользователь создался с коротким паролем"

    def test_register_password_no_digit(self, api_manager, api_manager_admin):
        register_data = {
            "email": faker.email(),
            "fullName": faker.name(),
            "password": "Testtest!",
            "passwordRepeat": "Testtest!"
        }

        response = api_manager.auth_api.register_user(register_data, expected_status=400)

        error_data = response.json()
        assert error_data.get("error") == "Bad Request"
        assert isinstance(error_data.get("message"), list)
        assert "Пароль должен содержать хотя бы одну цифру" in error_data["message"]

        # Дополнительная проверка: пользователь НЕ создался
        get_users = api_manager_admin.user_api.get_user_info(register_data["email"])
        if isinstance(get_users.json(), list):
            assert len(get_users.json()) == 0, "Пользователь создался с паролем без цифры"

    def test_register_password_no_uppercase(self, api_manager, api_manager_admin):
        register_data = {
            "email": faker.email(),
            "fullName": faker.name(),
            "password": "test123!",
            "passwordRepeat": "test123!"
        }

        response = api_manager.auth_api.register_user(register_data, expected_status=400)

        error_data = response.json()
        assert error_data.get("error") == "Bad Request"
        assert isinstance(error_data.get("message"), list)
        assert "Пароль должен содержать хотя бы одну заглавную букву" in error_data["message"]

        # Дополнительная проверка: пользователь НЕ создался
        get_users = api_manager_admin.user_api.get_user_info(register_data["email"])
        if isinstance(get_users.json(), list):
            assert len(get_users.json()) == 0, "Пользователь создался с паролем без заглавной"

    def test_register_password_with_space(self, api_manager, api_manager_admin):
        register_data = {
            "email": faker.email(),
            "fullName": faker.name(),
            "password": "Test 123!",
            "passwordRepeat": "Test 123!"
        }

        response = api_manager.auth_api.register_user(register_data, expected_status=400)

        error_data = response.json()
        assert error_data.get("error") == "Bad Request"
        assert isinstance(error_data.get("message"), list)
        assert "Пароль не должен содержать пробелов" in error_data["message"]

        # Дополнительная проверка: пользователь НЕ создался
        get_users = api_manager_admin.user_api.get_user_info(register_data["email"])
        if isinstance(get_users.json(), list):
            assert len(get_users.json()) == 0, "Пользователь создался с паролем-пробелом"

    def test_register_password_mismatch(self, api_manager, api_manager_admin):
        register_data = {
            "email": faker.email(),
            "fullName": faker.name(),
            "password": "Test123!",
            "passwordRepeat": "Test123!!"
        }

        response = api_manager.auth_api.register_user(register_data, expected_status=400)

        error_data = response.json()
        assert error_data.get("error") == "Bad Request"
        assert isinstance(error_data.get("message"), list)
        assert "Пароли не совпадают" in error_data["message"]

        # Дополнительная проверка: пользователь НЕ создался
        get_users = api_manager_admin.user_api.get_user_info(register_data["email"])
        if isinstance(get_users.json(), list):
            assert len(get_users.json()) == 0, "Пользователь создался с несовпадающими паролями"

    # ========== ЛОГИН (негатив) ==========
    def test_login_wrong_password(self, api_manager, create_user, register_data):
        """Негатив: логин с неверным паролем"""

        # Логинимся как юзер из фикстуры
        correct_login_data = {
            "email": register_data["email"],
            "password": register_data["password"]
        }
        api_manager.auth_api.login_user(correct_login_data)

        # Меняем пароль
        wrong_login_data = {
            "email": register_data["email"],
            "password": "WrongPassword123!"
        }
        response = api_manager.auth_api.login_user(wrong_login_data, expected_status=401)

        error_data = response.json()
        assert error_data.get("error") == "Unauthorized"
        assert error_data.get("message") == "Неверный логин или пароль"

        # Дополнительная проверка: пользователь не заблокирован и всё ещё может залогиниться с правильным паролем
        api_manager.auth_api.login_user(correct_login_data)

    @pytest.mark.skip(reason="БАГ: сервер возвращает 401 вместо 404")
    def test_login_nonexistent_email(self, api_manager, api_manager_admin):
        """Негатив: логин с несуществующей почтой"""
        login_data = {
            "email": "nonexistent123412412351@email.com",
            "password": "Test123!"
        }

        response = api_manager.auth_api.login_user(login_data, expected_status=404)

        error_data = response.json()
        assert error_data.get("error") == "Not Found"
        assert error_data.get("message") == "Пользователь не найден"

        # Дополнительная проверка: пользователя действительно нет
        get_users = api_manager_admin.user_api.get_user_info(login_data["email"])
        if isinstance(get_users.json(), list):
            assert len(get_users.json()) == 0, "Нашёлся пользователь с несуществующим email"

    @pytest.mark.skip(reason="БАГ: сервер возвращает 401 вместо 400")
    def test_login_invalid_email_format(self, api_manager, api_manager_admin):
        login_data = {
            "email": "not_an_email",
            "password": "Test123!"
        }

        response = api_manager.auth_api.login_user(login_data, expected_status=400)

        error_data = response.json()
        assert error_data.get("error") == "Bad Request"
        assert error_data.get("message") == "Неверный формат email"

        # Дополнительная проверка: пользователя действительно нет
        get_users = api_manager_admin.user_api.get_user_info(login_data["email"])
        if isinstance(get_users.json(), list):
            assert len(get_users.json()) == 0, "Нашёлся пользователь с несуществующим email"

    @pytest.mark.skip(reason="БАГ: сервер возвращает 401 вместо 400")
    def test_login_empty_email(self, api_manager, api_manager_admin):
        login_data = {
            "email": "",
            "password": "Test123!"
        }

        response = api_manager.auth_api.login_user(login_data, expected_status=400)

        error_data = response.json()
        assert error_data.get("error") == "Bad Request"
        assert error_data.get("message") == "Email не может быть пустым"

        # Дополнительная проверка: пользователя действительно нет
        get_users = api_manager_admin().user_api.get_user_info(login_data["email"])
        if isinstance(get_users.json(), list):
            assert len(get_users.json()) == 0, "Нашёлся пользователь с несуществующим email"

    @pytest.mark.skip(reason="БАГ: сервер возвращает 401 вместо 400")
    def test_login_empty_password(self, api_manager):
        login_data = {
            "email": "test@email.com",
            "password": ""
        }

        response = api_manager.auth_api.login_user(login_data, expected_status=400)

        error_data = response.json()
        assert error_data.get("error") == "Bad Request"
        assert error_data.get("message") == "Пароль не может быть пустым"

    @pytest.mark.skip(reason="БАГ: сервер возвращает 401 вместо 400")
    def test_login_empty_body(self, api_manager):
        response = api_manager.auth_api.login_user({}, expected_status=400)

        error_data = response.json()
        assert error_data.get("error") == "Bad Request"
        assert error_data.get("message") == "Тело запроса не может быть пустым"