from for_custom_requester.constants import REGISTER_ENDPOINT, LOGIN_ENDPOINT
from custom_requester.custom_requester import CustomRequester

# - Класс наследуется от `CustomRequester`, получая доступ к методам (`send_request`).
class AuthAPI(CustomRequester):
    """
    Класс для работы с аутентификацией.
    """

    # - Принимает `session`, которая передается в базовый класс.
    def __init__(self, session):
        super().__init__(session=session, base_url="https://auth.dev-cinescope.coconutqa.ru/")
        self._token = None # добавил атрибут для функции от меня
        # - При инициализации получает сессию и базовый URL API.

    # - Использует метод `send_request` для отправки POST-запроса на регистрацию.
    # - Проверяет статус ответа (по умолчанию `201`).
    def register_user(self, user_data, expected_status=201):
        """
        Регистрация нового пользователя.

        Отправляет POST-запрос на эндпоинт регистрации для создания нового пользователя.

        :param user_data: Словарь с данными пользователя:
            - email: Email пользователя (строка)
            - fullName: Полное имя (строка)
            - password: Пароль (строка, соответствует требованиям)
            - passwordRepeat: Повтор пароля (строка)
            - roles: Список ролей (например, ["USER"])
        :param expected_status: Ожидаемый статус-код ответа (по умолчанию 201).
        :return: Response объект requests.
        """
        return self.send_request(
            method="POST",
            endpoint=REGISTER_ENDPOINT,
            data=user_data,
            expected_status=expected_status
        )

    def login_user(self, login_data, expected_status=200):
        """
        Авторизация пользователя.

        Отправляет POST-запрос на эндпоинт логина для аутентификации пользователя.

        :param login_data: Словарь с данными для входа:
            - email: Email пользователя (строка)
            - password: Пароль (строка)
        :param expected_status: Ожидаемый статус-код ответа (по умолчанию 200).
        :return: Response объект requests, содержащий:
            - user: Информация о пользователе (id, email, fullName, roles)
            - accessToken: Токен доступа (JWT)
            - refreshToken: Токен обновления
            - expiresIn: Время истечения токена в миллисекундах
        """
        return self.send_request(
            method="POST",
            endpoint=LOGIN_ENDPOINT,
            data=login_data,
            expected_status=expected_status
        )

    def authenticate(self, user_creds):
        """
        Выполняет аутентификацию пользователя по email и паролю.
        Отправляет запрос на /login, извлекает accessToken, сохраняет его в атрибут _token
        и обновляет заголовки сессии.

        :param user_creds: Список или кортеж из двух элементов: [email, password].
        :raises KeyError: Если в ответе отсутствует поле accessToken.
        """
        login_data = {
            "email": user_creds[0],
            "password": user_creds[1]
        }

        response = self.login_user(login_data).json()
        if "accessToken" not in response:
            raise KeyError("token is missing")

        token = response["accessToken"]
        self._token = token  # запоминаем токен
        self._update_session_headers(**{"Authorization": "Bearer " + token})

    def set_token(self, token):
        """
        Устанавливает переданный токен в качестве текущего для аутентификации.
        Обновляет заголовки сессии и сохраняет токен в атрибут _token.

        :param token: Строка с accessToken (без префикса "Bearer ").
        """
        self._token = token
        self._update_session_headers(**{"Authorization": "Bearer " + token})

    def get_token(self):
        """
        Возвращает текущий сохранённый токен.

        :return: Строка accessToken.
        :raises AssertionError: Если токен не был установлен (None).
        """
        assert self._token is not None, "Токен пуст, аутентификация не прошла."
        return self._token

    def clear_token(self):
        """
        Сбрасывает текущий токен, удаляя его из атрибута _token и заголовков сессии.
        """
        self._token = None
        self._update_session_headers(**{"Authorization": None})