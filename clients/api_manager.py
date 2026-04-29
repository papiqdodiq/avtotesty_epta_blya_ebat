from clients.api.auth_api import AuthAPI
from clients.api.user_api import UserAPI
from clients.api.films_api import FilmsAPI


class ApiManager:
    """
    Класс для управления API-классами с единой HTTP-сессией.

    Централизованно управляет аутентификацией и синхронизацией токенов
    между всеми API-классами (AuthAPI, UserAPI, FilmsAPI).
    """

    def __init__(self, session):
        """
        Инициализация ApiManager.

        Принимает объект HTTP-сессии и создаёт экземпляры всех API-классов,
        передавая им эту сессию.

        :param session: HTTP-сессия (requests.Session), используемая всеми API-классами.
        """
        self.session = session
        self.auth_api = AuthAPI(session)
        self.user_api = UserAPI(session)
        self.films_api = FilmsAPI(session)
        self._current_token = None  # Добавлен атрибут для хранения текущего токена

    def authenticate(self, user_creds):
        """
        Выполняет аутентификацию пользователя и синхронизирует токен во всех API-классах.

        Сначала аутентифицируется через AuthAPI, получает токен,
        затем устанавливает этот же токен в UserAPI и FilmsAPI.

        :param user_creds: Список или кортеж из двух элементов: [email, password].
        """
        self.auth_api.authenticate(user_creds)
        self._current_token = self.auth_api.get_token()
        # Синхронизируем токен с UserAPI и FilmsAPI
        self.user_api.set_token(self._current_token)
        self.films_api.set_token(self._current_token)

    def clear_token(self):
        """
        Сбрасывает токен во всех API-классах (AuthAPI, UserAPI, FilmsAPI).

        Используется для атомарности тестов — гарантирует,
        что каждый тест начинается с чистого состояния без токена.
        """
        self.auth_api.clear_token()
        self.user_api.clear_token()
        self.films_api.clear_token()

    def set_token(self, token):
        """
        Устанавливает переданный токен во всех API-классах.

        Позволяет задать невалидный токен или любой другой токен вручную,
        минуя процесс аутентификации.

        :param token: Строка accessToken (без префикса "Bearer ").
        """
        self.auth_api.set_token(token)
        self.user_api.set_token(token)
        self.films_api.set_token(token)


"""
Конструктор `ApiManager`:
- Принимает объект `session` (HTTP-сессия).
- Создаёт экземпляры AuthAPI, UserAPI и FilmsAPI, передавая им единую сессию.
- Иными словами, конструктор принимает session — объект сессии,
который будет передаваться в каждый API-класс.
"""