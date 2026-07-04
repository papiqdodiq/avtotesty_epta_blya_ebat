import pytest

class TestUser:

    def test_create_user(self, super_admin, creation_user_data):
        # IDE думает, что фикстура не используется, но она используется.
        # Pytest умнее IDE. Если тесты зелёные — значит pytest всё правильно понял.
        response = super_admin.api.user_api.create_user(creation_user_data).json()

        assert response.get('id') and response['id'] != '', "ID должен быть не пустым"
        assert response.get('email') == creation_user_data['email']
        assert response.get('fullName') == creation_user_data['fullName']
        assert response.get('roles', []) == creation_user_data['roles']
        assert response.get('verified') is True

    @pytest.mark.parametrize("search_field", ["id", "email"])
    def test_get_by_locator(self, super_admin, creation_user_data, search_field):
        # Создаем пользователя
        created_user = super_admin.api.user_api.create_user(creation_user_data).json()

        # Определяем значение для поиска в зависимости от поля
        if search_field == "id":
            search_value = created_user['id']
        else:
            search_value = created_user['email']

        # Ищем юзера
        response = super_admin.api.user_api.get_user_info(search_value).json()

        # Проверки
        assert response['id'] == created_user['id']
        assert response['email'] == creation_user_data['email']
        assert response['fullName'] == creation_user_data['fullName']
        assert response['roles'] == creation_user_data['roles']
        assert response['verified'] is True

    def test_get_user_by_id_common_user(self, common_user):
        common_user.api.user_api.get_user_info(common_user.email, expected_status=403)