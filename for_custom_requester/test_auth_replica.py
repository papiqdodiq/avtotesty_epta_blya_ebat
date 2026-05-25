from clients.api_manager import ApiManager
from models.base_models import RegisterUserResponse

class TestAuthAPI:
    def test_register_user(self, api_manager: ApiManager, test_user_pydantic):
        """
        Тест на регистрацию пользователя.
        """
        user_data = test_user_pydantic.model_dump() # делаем словарь, а не JSON объект!!!
        response = api_manager.auth_api.register_user(user_data)

        # Проверки
        assert response.email == test_user_pydantic.email, "Email не совпадает"

    # Сначала он ебанет регистрационный тест (setup) и только после логин тест,
    # ведь тест регистрации у нас зашит в фикстуре.
    def test_register_and_login_user(self, api_manager, registered_user):
        """
        Тест на регистрацию и авторизацию пользователя.
        """
        login_data = {
            "email": registered_user["email"],
            "password": registered_user["password"]
        }
        response = api_manager.auth_api.login_user(login_data)
        response_data = response.json()

        # Проверки
        assert "accessToken" in response_data, "Токен доступа отсутствует в ответе"
        assert response_data["user"]["email"] == registered_user["email"], "Email не совпадает"