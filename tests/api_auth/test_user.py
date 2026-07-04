import pytest
from constants import AUTH_URL
from faker import Faker
from models.base_models import CreateUserData

faker_ru = Faker('ru_RU')  # для имён
faker_en = Faker('en_US')  # для email


class TestUserPositive:

    def test_create_user_success(self, api_manager_admin, register_data_pydantic):
        """Позитив: успешное создание пользователя админом с валидными данными.
        Проверяем статус, заголовки, структуру ответа и типы данных."""

        # БАГ!!! В регулярном выражении ПАРОЛЯ отсутствует символ "!" хотя в документации он указан:
        # password must match /^(?=.*[a-zA-Zа-яА-Я])(?=.*\\d)[a-zA-Zа-яА-Я\\d?@#$%^&*_\\-+()\\[\\]{}><\\\\/\\\\|\"'.,:;]
        # {8,20}$/ regular expression
        # Если пароль нагенерирует пароль с символом "!", то тест упадет.

        user_data = CreateUserData(
            email=register_data_pydantic.email,
            fullName=register_data_pydantic.fullName,
            password=register_data_pydantic.password,
            verified=True,
            banned=False
        )

        response = api_manager_admin.user_api.create_user(user_data.model_dump(), pydantic=True)

        # Проверка значений
        assert response.email == user_data.email, "email не совпадает"
        assert response.fullName == user_data.fullName, "fullName не совпадает"
        assert "USER" in response.roles, "роль USER отсутствует"
        assert "ADMIN" not in response.roles, "роль ADMIN не должна быть"
        assert "SUPER_ADMIN" not in response.roles, "роль SUPER_ADMIN не должна быть"
        assert response.verified is True, "verified должен быть True"
        assert response.banned is False, "banned должен быть False"

        # Чистим
        user_id = response.id
        api_manager_admin.user_api.delete_user(user_id)

    @pytest.mark.parametrize("update_data", [
        {"verified": False},
        {"banned": True},
        {"roles": ["USER", "ADMIN"]},
        {"roles": ["USER", "ADMIN", "SUPER_ADMIN"]},
        {"roles": []},
    ])
    def test_update_user(self, api_manager_admin, create_user_pydantic, update_data):
        """Позитив: успешное обновление статуса verified пользователя."""

        # БАГ!!! В ответе отсутствует поле id
        response = api_manager_admin.user_api.patch_user(create_user_pydantic["id"], update_data, pydantic=True)

        # Проверка значений
        assert response.email == create_user_pydantic["email"], "email не совпадает"
        assert response.fullName == create_user_pydantic["full_name"], "fullName не совпадает"
        if "verified" in update_data:
            assert update_data["verified"] == response.verified, "verified должен совпадать с изменением"
        else:
            assert response.verified is True, "verified должен быть True"
        if "banned" in update_data:
            assert update_data["banned"] == response.banned, "banned должен совпадать с изменением"
        else:
            assert response.banned is False, "banned должен быть False"
        if "roles" in update_data:
            assert update_data["roles"] == response.roles
        else:
            assert response.roles == ["USER"]


class TestUserNegative:

    # ========== СОЗДАНИЕ ЮЗЕРА (негатив) ==========
    def test_create_user_duplicate_email(self, api_manager_admin, register_data_pydantic):
        """Негатив: создание пользователя с уже существующим email"""

        user_data = CreateUserData(
            email=register_data_pydantic.email,
            fullName=register_data_pydantic.fullName,
            password=register_data_pydantic.password,
            verified=True,
            banned=False
        )

        # Первый запрос
        response = api_manager_admin.user_api.create_user(user_data.model_dump(), pydantic=True)

        # Второй запрос
        api_manager_admin.user_api.create_user(user_data.model_dump(), 409)

        user_id = response.id
        api_manager_admin.user_api.delete_user(user_id)

    def test_create_user_empty_email(self, auth_session):
        """Негатив: создание пользователя с пустым email"""

        user_data = {
            "email": "",
            "fullName": faker_ru.name(),
            "password": "Test123456@",
            "verified": True,
            "banned": False
        }

        response = auth_session.post(f"{AUTH_URL}/user", json=user_data)
        assert response.status_code == 400, "Создание с пустым email не вызвало ошибку"

    def test_create_user_invalid_email_format(self, auth_session):
        """Негатив: создание пользователя с невалидным форматом email"""

        user_data = {
            "email": "not_an_email",
            "fullName": faker_ru.name(),
            "password": "Test123456@",
            "verified": True,
            "banned": False
        }

        response = auth_session.post(f"{AUTH_URL}/user", json=user_data)
        assert response.status_code == 400, "Создание с невалидным email не вызвало ошибку"

    def test_create_user_empty_fullname(self, auth_session):
        """Негатив: создание пользователя с пустым fullName"""

        user_data = {
            "email": faker_en.email(),
            "fullName": "",
            "password": "Test123456@",
            "verified": True,
            "banned": False
        }

        response = auth_session.post(f"{AUTH_URL}/user", json=user_data)
        assert response.status_code == 400, "Создание с пустым fullName не вызвало ошибку"

    def test_create_user_short_password(self, auth_session):
        """Негатив: создание пользователя с коротким паролем (<8 символов)"""

        user_data = {
            "email": faker_en.email(),
            "fullName": faker_ru.name(),
            "password": "Test1@",
            "verified": True,
            "banned": False
        }

        response = auth_session.post(f"{AUTH_URL}/user", json=user_data)
        assert response.status_code == 400, "Создание с коротким паролем не вызвало ошибку"

    def test_create_user_password_no_digit(self, auth_session):
        """Негатив: создание пользователя с паролем без цифры"""

        user_data = {
            "email": faker_en.email(),
            "fullName": faker_ru.name(),
            "password": "Testtest@",
            "verified": True,
            "banned": False
        }

        response = auth_session.post(f"{AUTH_URL}/user", json=user_data)
        assert response.status_code == 400, "Создание с паролем без цифры не вызвало ошибку"

    @pytest.mark.skip(reason="БАГ: сервер возвращает 201 вместо 400")
    def test_create_user_password_no_uppercase(self, auth_session):
        """Негатив: создание пользователя с паролем без заглавной буквы"""

        user_data = {
            "email": faker_en.email(),
            "fullName": faker_ru.name(),
            "password": "test123456@",
            "verified": True,
            "banned": False
        }

        response = auth_session.post(f"{AUTH_URL}/user", json=user_data)
        assert response.status_code == 400, "Создание с паролем без заглавной не вызвало ошибку"

    def test_create_user_password_with_space(self, auth_session):
        """Негатив: создание пользователя с паролем, содержащим пробел"""

        user_data = {
            "email": faker_en.email(),
            "fullName": faker_ru.name(),
            "password": "Test 123456@",
            "verified": True,
            "banned": False
        }

        response = auth_session.post(f"{AUTH_URL}/user", json=user_data)
        assert response.status_code == 400, "Создание с паролем-пробелом не вызвало ошибку"

    def test_create_user_missing_email(self, auth_session):
        """Негатив: создание пользователя без поля email"""

        user_data = {
            "fullName": faker_ru.name(),
            "password": "Test123456@",
            "verified": True,
            "banned": False
        }

        response = auth_session.post(f"{AUTH_URL}/user", json=user_data)
        assert response.status_code == 400, "Создание без email не вызвало ошибку"

    def test_create_user_missing_fullname(self, auth_session):
        """Негатив: создание пользователя без поля fullName"""

        user_data = {
            "email": faker_en.email(),
            "password": "Test123456@",
            "verified": True,
            "banned": False
        }

        response = auth_session.post(f"{AUTH_URL}/user", json=user_data)
        assert response.status_code == 400, "Создание без fullName не вызвало ошибку"

    def test_create_user_missing_password(self, auth_session):
        """Негатив: создание пользователя без поля password"""

        user_data = {
            "email": faker_en.email(),
            "fullName": faker_ru.name(),
            "verified": True,
            "banned": False
        }

        response = auth_session.post(f"{AUTH_URL}/user", json=user_data)
        assert response.status_code == 400, "Создание без password не вызвало ошибку"

    def test_create_user_missing_verified(self, auth_session):
        """Негатив: создание пользователя без поля verified"""

        user_data = {
            "email": faker_en.email(),
            "fullName": faker_ru.name(),
            "password": "Test123456@",
            "banned": False
        }

        response = auth_session.post(f"{AUTH_URL}/user", json=user_data)
        assert response.status_code == 400, "Создание без verified не вызвало ошибку"

    def test_create_user_missing_banned(self, auth_session):
        """Негатив: создание пользователя без поля banned"""

        user_data = {
            "email": faker_en.email(),
            "fullName": faker_ru.name(),
            "password": "Test123456@",
            "verified": True
        }

        response = auth_session.post(f"{AUTH_URL}/user", json=user_data)
        assert response.status_code == 400, "Создание без banned не вызвало ошибку"

    def test_create_user_empty_body(self, auth_session):
        """Негатив: создание пользователя с пустым телом запроса"""

        response = auth_session.post(f"{AUTH_URL}/user", json={})
        assert response.status_code == 400, "Создание с пустым телом не вызвало ошибку"

    # ========== ИЗМЕНЕНИЕ ДАННЫХ ЮЗЕРА (негатив) ==========
    def test_update_user_invalid_roles(self, auth_session, create_user):
        """Негатив: обновление пользователя с некорректными ролями."""

        user_id = create_user["id"]

        update_data = {
            "verified": True,
            "banned": False,
            "roles": ["INVALID_ROLE"]
        }

        response = auth_session.patch(f"{AUTH_URL}/user/{user_id}", json=update_data)
        assert response.status_code == 400, "Обновление с некорректной ролью не вызвало ошибку"

    @pytest.mark.skip(reason="БАГ: сервер возвращает 200 вместо 400")
    def test_update_user_roles_without_user_role(self, auth_session, create_user):
        """Негатив: обновление пользователя с ролями без USER."""

        user_id = create_user["id"]

        update_data = {
            "verified": True,
            "banned": False,
            "roles": ["ADMIN"]
        }

        response = auth_session.patch(f"{AUTH_URL}/user/{user_id}", json=update_data)
        assert response.status_code == 400, "Обновление без роли USER не вызвало ошибку"

    def test_update_user_invalid_verified_type(self, auth_session, create_user):
        """Негатив: обновление пользователя с verified в виде строки."""

        user_id = create_user["id"]

        update_data = {
            "verified": "not_a_boolean",
            "banned": False,
            "roles": ["USER"]
        }

        response = auth_session.patch(f"{AUTH_URL}/user/{user_id}", json=update_data)
        assert response.status_code == 400, "Обновление с verified-строкой не вызвало ошибку"

    def test_update_user_invalid_banned_type(self, auth_session, create_user):
        """Негатив: обновление пользователя с banned в виде строки."""

        user_id = create_user["id"]

        update_data = {
            "verified": True,
            "banned": "not_a_boolean",
            "roles": ["USER"]
        }

        response = auth_session.patch(f"{AUTH_URL}/user/{user_id}", json=update_data)
        assert response.status_code == 400, "Обновление с banned-строкой не вызвало ошибку"

    @pytest.mark.skip(reason="БАГ: сервер возвращает 400 вместо 404")
    def test_update_user_invalid_id(self, auth_session):
        """Негатив: обновление несуществующего пользователя."""

        update_data = {
            "verified": True,
            "banned": False,
            "roles": ["USER"]
        }

        response = auth_session.patch(f"{AUTH_URL}/user/00000000-0000-0000-0000-000000000000", json=update_data)
        assert response.status_code == 404, "Обновление несуществующего пользователя не вызвало ошибку"

    @pytest.mark.skip(reason="БАГ: сервер возвращает 200 вместо 400")
    def test_update_user_empty_body(self, auth_session, create_user):
        """Негатив: обновление пользователя с пустым телом запроса."""

        user_id = create_user["id"]

        response = auth_session.patch(f"{AUTH_URL}/user/{user_id}", json={})
        assert response.status_code == 400, "Обновление с пустым телом не вызвало ошибку"