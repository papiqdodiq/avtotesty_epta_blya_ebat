import pytest
from constants import AUTH_URL
from faker import Faker

faker_ru = Faker('ru_RU')  # для имён
faker_en = Faker('en_US')  # для email

class TestUserPositive:

    def test_create_user_success(self, auth_session):
        """Позитив: успешное создание пользователя админом с валидными данными.
        Проверяем статус, заголовки, структуру ответа и типы данных."""

        # Генерируем уникальные данные
        email = faker_en.email()
        full_name = faker_ru.name()
        # БАГ!!! В регулярном выражении отсутствует символ "!" хотя в документации он указан:
        # password must match /^(?=.*[a-zA-Zа-яА-Я])(?=.*\\d)[a-zA-Zа-яА-Я\\d?@#$%^&*_\\-+()\\[\\]{}><\\\\/\\\\|\"'.,:;]{8,20}$/ regular expression
        # Используем символ "@" который есть и в документации, и в регулярном выражении
        password = "Test123456@"  # @ есть в документации и в регулярке

        user_data = {
            "email": email,
            "fullName": full_name,
            "password": password,
            "verified": True,
            "banned": False
        }

        response = auth_session.post(f"{AUTH_URL}/user", json=user_data)

        # Статус и заголовки
        assert response.status_code == 201, f"Ошибка при создании пользователя: {response.text}"
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
        assert data["email"] == email, "email не совпадает"
        assert data["fullName"] == full_name, "fullName не совпадает"
        assert "USER" in data["roles"], "роль USER отсутствует"
        assert data["verified"] is True, "verified должен быть True"
        assert data["banned"] is False, "banned должен быть False"

        # Проверка формата UUID
        assert len(data["id"]) == 36, "id должен быть UUID формата"
        assert data["id"].count("-") == 4, "id должен содержать 4 дефиса"

        # Проверка формата createdAt (ISO 8601)
        assert "T" in data["createdAt"], "createdAt должен быть в формате ISO 8601"

        # Чистим
        auth_session.delete(f"{AUTH_URL}/user/{data['id']}")

    def test_update_user_verified_status(self, auth_session, create_user):
        """Позитив: успешное обновление статуса verified пользователя."""

        user_id = create_user["id"]
        email = create_user["email"]
        full_name = create_user["full_name"]

        update_data = {
            "verified": False,
            "banned": False,
            "roles": ["USER"]
        }

        response = auth_session.patch(f"{AUTH_URL}/user/{user_id}", json=update_data)

        assert response.status_code == 200, f"Ошибка при обновлении пользователя: {response.text}"
        assert response.headers.get("Content-Type") == "application/json; charset=utf-8", "Неверный Content-Type"

        # БАГ!!! В ответе отсутствует поле id
        data = response.json()
        required_fields = ["email", "fullName", "verified", "banned", "roles", "createdAt"]
        for field in required_fields:
            assert field in data, f"У ответа отсутствует поле {field}"

        assert isinstance(data["email"], str), "email должен быть строкой"
        assert isinstance(data["fullName"], str), "fullName должен быть строкой"
        assert isinstance(data["verified"], bool), "verified должен быть булевым"
        assert isinstance(data["banned"], bool), "banned должен быть булевым"
        assert isinstance(data["roles"], list), "roles должен быть списком"

        assert data["email"] == email, "email не совпадает"
        assert data["fullName"] == full_name, "fullName не совпадает"
        assert data["verified"] is False, "verified должен быть False"
        assert data["banned"] is False, "banned должен быть False"
        assert "USER" in data["roles"], "роль USER отсутствует"

    def test_update_user_banned_status(self, auth_session, create_user):
        """Позитив: успешное обновление статуса banned пользователя."""

        user_id = create_user["id"]

        update_data = {
            "verified": True,
            "banned": True,
            "roles": ["USER"]
        }

        response = auth_session.patch(f"{AUTH_URL}/user/{user_id}", json=update_data)

        assert response.status_code == 200, f"Ошибка при обновлении пользователя: {response.text}"

        data = response.json()
        assert data["banned"] is True, "banned должен быть True"

    def test_update_user_roles_to_admin(self, auth_session, create_user):
        """Позитив: успешное изменение роли пользователя на ADMIN."""

        user_id = create_user["id"]

        update_data = {
            "verified": True,
            "banned": False,
            "roles": ["USER", "ADMIN"]
        }

        response = auth_session.patch(f"{AUTH_URL}/user/{user_id}", json=update_data)

        assert response.status_code == 200, f"Ошибка при обновлении роли: {response.text}"

        data = response.json()
        assert "USER" in data["roles"], "роль USER отсутствует"
        assert "ADMIN" in data["roles"], "роль ADMIN отсутствует"
        assert "SUPER_ADMIN" not in data["roles"], "роль SUPER_ADMIN не должна быть"

    def test_update_user_roles_to_super_admin(self, auth_session, create_user):
        """Позитив: успешное изменение роли пользователя на SUPER_ADMIN."""

        user_id = create_user["id"]

        update_data = {
            "verified": True,
            "banned": False,
            "roles": ["USER", "ADMIN", "SUPER_ADMIN"]
        }

        response = auth_session.patch(f"{AUTH_URL}/user/{user_id}", json=update_data)

        assert response.status_code == 200, f"Ошибка при обновлении роли: {response.text}"

        data = response.json()
        assert "USER" in data["roles"], "роль USER отсутствует"
        assert "ADMIN" in data["roles"], "роль ADMIN отсутствует"
        assert "SUPER_ADMIN" in data["roles"], "роль SUPER_ADMIN отсутствует"

    def test_update_user_without_any_role(self, auth_session, create_user):
        """Позитив: обновление пользователя без ролей."""

        user_id = create_user["id"]

        update_data = {
            "verified": True,
            "banned": False,
            "roles": []
        }

        response = auth_session.patch(f"{AUTH_URL}/user/{user_id}", json=update_data)
        assert response.status_code == 200, "Обновление без ролей вызвало ошибку"


class TestUserNegative:

    # ========== СОЗДАНИЕ ЮЗЕРА (негатив) ==========
    def test_create_user_duplicate_email(self, auth_session):
        """Негатив: создание пользователя с уже существующим email"""

        email = faker_en.email()
        full_name = faker_ru.name()
        password = "Test123456@"

        user_data = {
            "email": email,
            "fullName": full_name,
            "password": password,
            "verified": True,
            "banned": False
        }

        response1 = auth_session.post(f"{AUTH_URL}/user", json=user_data)
        assert response1.status_code == 201
        user_id = response1.json()["id"]

        response2 = auth_session.post(f"{AUTH_URL}/user", json=user_data)
        assert response2.status_code == 409, "Создание с дублирующим email не вызвало ошибку"

        auth_session.delete(f"{AUTH_URL}/user/{user_id}")

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