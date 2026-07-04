from custom_requester.custom_requester import CustomRequester
from models.base_models import CreateUserResponse, PatchUserResponse
from typing import Union
from requests import Response

# - Наследует методы от CustomRequester.
class UserAPI(CustomRequester):
    """
    Класс для работы с API пользователей.
    """

    # - Инициализируется с той же сессией, что и другие API-классы.
    def __init__(self, session):
        super().__init__(session=session, base_url="https://auth.dev-cinescope.coconutqa.ru/")
        # - При инициализации получает сессию и базовый URL API.

    # создание и получение юзера по локатору (здесь это user_id) может быть по id или email

    def get_user_info(self, user_id, expected_status=200):
        """
        Получение информации о пользователе по его ID.

        :param user_id: ID пользователя (строка UUID).
        :param expected_status: Ожидаемый статус-код ответа.
        :return: Response объект requests.
        """
        return self.send_request(
            method="GET",
            endpoint=f"user/{user_id}",
            expected_status=expected_status
        )

    def create_user(self, user_data, expected_status=201, pydantic=False) -> Union[CreateUserResponse, Response]:
        response = self.send_request(
            method="POST",
            endpoint="user",
            data=user_data,
            expected_status=expected_status
        )
        response: Response = response
        if pydantic:
            return CreateUserResponse(**response.json())
        else:
            return response

    def patch_user(self, user_id, user_data, expected_status=200, pydantic=False) -> Union[PatchUserResponse, Response]:
        response = self.send_request(
            method="PATCH",
            endpoint=f"user/{user_id}",
            data=user_data,
            expected_status=expected_status
        )
        response: Response = response
        if pydantic:
            return PatchUserResponse(**response.json())
        else:
            return response

    def delete_user(self, user_id, expected_status=200):
        """
        Удаление пользователя по его ID.

        :param user_id: ID пользователя (строка UUID).
        :param expected_status: Ожидаемый статус-код ответа.
        :return: Response объект requests.
        """
        return self.send_request(
            method="DELETE",
            endpoint=f"user/{user_id}",
            expected_status=expected_status
        )

    def set_token(self, token):
        """
        Устанавливает токен авторизации для запросов UserAPI.
        Обновляет заголовок Authorization в сессии.

        :param token: Строка accessToken (без префикса "Bearer ").
        """
        self._update_session_headers(**{"Authorization": "Bearer " + token})

    def clear_token(self):
        """
        Сбрасывает токен авторизации для запросов UserAPI.
        Удаляет заголовок Authorization из сессии.
        """
        self._update_session_headers(**{"Authorization": None})