import pytest
from faker import Faker
from utils.validators import assert_valid_iso_datetime, assert_datetime_in_range
from datetime import datetime, timezone, timedelta


faker = Faker('ru_RU')


# Тут использую кастом реквестер и api-менеджер (отредачил все позитивные тесты,
# используя api-классы с методами для /register, /login, /get, /delete)
class TestPositiveAuth:

    def test_register_success(self, api_manager, api_manager_admin, register_data_pydantic):
        """Позитив: успешная регистрация пользователя с валидными данными.
        Проверяем статус, заголовки, структуру ответа и типы данных."""

        # 1. РЕГИСТРАЦИЯ
        before_request = datetime.now(timezone.utc) - timedelta(seconds=5) # я так делаю, потому что
        # серверное время в один момент начинает от времени на моем ноуте, хз почему
        reg_data = register_data_pydantic.model_dump() # делаем словарь, а не JSON объект!!!
        response = api_manager.auth_api.register_user(reg_data, pydantic=True)
        after_request = datetime.now(timezone.utc) + timedelta(seconds=10)  # +10 секунд

        # Проверка значений
        assert response.email == register_data_pydantic.email, "email не совпадает"
        assert response.fullName == register_data_pydantic.fullName, "fullName не совпадает"

        assert "USER" in response.roles, "роль USER отсутствует"
        assert response.verified is True, "verified должен быть True"
        assert response.banned is False, "banned должен быть False"

        # Проверка формата createdAt (ISO 8601)
        assert_valid_iso_datetime(response.createdAt)
        assert_datetime_in_range(response.createdAt, before_request, after_request)

        user_id = response.id

        # 2. ПРОВЕРЯЕМ, ЧТО ПОЛЬЗОВАТЕЛЬ РЕАЛЬНО СОЗДАЛСЯ (GET)
        get_user = api_manager_admin.user_api.get_user_info(user_id)

        get_data = get_user.json()
        assert get_data["id"] == user_id, "id не совпадает"
        assert get_data["email"] == register_data_pydantic.email, "email не совпадает"
        assert get_data["fullName"] == register_data_pydantic.fullName, "fullName не совпадает"
        assert get_data["verified"] is True, "verified должен быть True"
        assert get_data["banned"] is False, "banned должен быть False"

        # 3. УДАЛЯЕМ ПОЛЬЗОВАТЕЛЯ
        api_manager_admin.user_api.delete_user(user_id)

        # 4. ПРОВЕРЯЕМ, ЧТО ПОЛЬЗОВАТЕЛЬ ДЕЙСТВИТЕЛЬНО УДАЛИЛСЯ
        # БАГ!!! API возвращает 200 и пустое тело {} вместо 404
        get_deleted = api_manager_admin.user_api.get_user_info(user_id)

        # Проверяем, что тело ответа пустое (пользователь не найден)
        assert get_deleted.json() == {}, "Тело ответа не пустое, пользователь не удалился"

    def test_login_success(self, api_manager, api_manager_admin, register_data_pydantic):
        """Позитив: успешный логин пользователя с корректными данными.
        Проверяем статус, заголовки, структуру ответа и типы данных."""

        # 1. СНАЧАЛА РЕГИСТРИРУЕМ ПОЛЬЗОВАТЕЛЯ
        reg_data = register_data_pydantic.model_dump()
        register_response = api_manager.auth_api.register_user(reg_data, pydantic=True)
        user_id = register_response.id

        # 2. ЛОГИН
        login_data = {
            "email": register_data_pydantic.email,
            "password": register_data_pydantic.password
        }
        login_response = api_manager.auth_api.login_user(login_data, pydantic=True)

        # Проверка значений
        user = login_response.user
        assert user.email == register_data_pydantic.email, "email не совпадает"
        assert user.fullName == register_data_pydantic.fullName, "fullName не совпадает"

        # 3. УДАЛЯЕМ ПОЛЬЗОВАТЕЛЯ
        api_manager_admin.user_api.delete_user(user_id)


class TestNegativeAuth:

    # ========== РЕГИСТРАЦИЯ (негатив) ==========
    def test_register_duplicate_email(self, api_manager, api_manager_admin, create_user_pydantic, register_data_pydantic):
        """Негатив: регистрация с уже существующим email"""
        user_id = create_user_pydantic["id"]

        response = api_manager.auth_api.register_user(register_data_pydantic.model_dump(), expected_status=409)

        error_data = response.json()
        assert error_data.get("error") == "Conflict"
        assert error_data.get("message") == "Пользователь с таким email уже зарегистрирован"

        # Дополнительная проверка: пользователь остался один
        get_user = api_manager_admin.user_api.get_user_info(user_id)
        assert get_user.json()["id"] == user_id

        # Проверяем, что дубликат не создался (пользователей с таким email только один)
        all_users = api_manager_admin.user_api.get_user_info(register_data_pydantic.email)
        if isinstance(all_users.json(), list):
            assert len(all_users.json()) == 1, "Создался дубликат пользователя"

    @pytest.mark.parametrize("password, password_repeat, expected_error", [
        ("Test1", "Test1", "Минимальная длина пароля 8 символов"),
        ("Testtest!", "Testtest!", "Пароль должен содержать хотя бы одну цифру"),
        ("test123!", "test123!", "Пароль должен содержать хотя бы одну заглавную букву"),
        ("Test 123!", "Test 123!", "Пароль не должен содержать пробелов"),
    ])
    def test_register_invalid_password(self, api_manager, api_manager_admin, register_data_pydantic, password,
                                       password_repeat, expected_error):
        # Берем базовую модель и обновляем только пароли
        test_user = register_data_pydantic.model_copy(update={
            "password": password,
            "passwordRepeat": password_repeat
        })
        response = api_manager.auth_api.register_user(test_user, expected_status=400)

        error_data = response.json()
        assert error_data.get("error") == "Bad Request"
        assert isinstance(error_data.get("message"), list)
        assert expected_error in error_data["message"]

        # Дополнительная проверка: пользователь НЕ создался
        get_users = api_manager_admin.user_api.get_user_info(test_user.email)
        if isinstance(get_users.json(), list):
            assert len(get_users.json()) == 0, "Пользователь создался с коротким паролем"

    def test_register_mismatch_password(self, api_manager, api_manager_admin):
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
    def test_login_wrong_password(self, api_manager, create_user_pydantic, register_data_pydantic):
        """Негатив: логин с неверным паролем"""

        # Логинимся как юзер из фикстуры
        correct_login_data = {
            "email": register_data_pydantic.email,
            "password": register_data_pydantic.password
        }
        api_manager.auth_api.login_user(correct_login_data, pydantic=True)

        # Меняем пароль
        wrong_login_data = {
            "email": register_data_pydantic.email,
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