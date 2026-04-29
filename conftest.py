import pytest
import requests
from faker import Faker

from constants import HEADERS, LOGIN_DATA, login_data_list, AUTH_URL, MOVIES_URL, CURRENT_USER_ID, REGISTER_ENDPOINT
from custom_requester.custom_requester import CustomRequester
from utils.data_generator import DataGenerator
from clients.api_manager import ApiManager

faker_ru = Faker('ru_RU')
faker_en = Faker('en_US')


#фикстуры для кастом реквестера в test_auth и test_user:

# @pytest.fixture(scope="function") === НЕ АКТУАЛЬНО ===
# def test_user():
#     """
#     Генерация случайного пользователя для тестов.
#     """
#     random_email = DataGenerator.generate_random_email()
#     random_name = DataGenerator.generate_random_name()
#     random_password = DataGenerator.generate_random_password()
#
#     return {
#         "email": random_email,
#         "fullName": random_name,
#         "password": random_password,
#         "passwordRepeat": random_password,
#         "roles": ["USER"]
#     }


# @pytest.fixture(scope="function") === НЕ АКТУАЛЬНО ===
# def registered_user(requester, test_user):
#     """
#     Фикстура для регистрации и получения данных зарегистрированного пользователя.
#     """
#     response = requester.send_request(
#         method="POST",
#         endpoint=REGISTER_ENDPOINT,
#         data=test_user,
#         expected_status=201
#     )
#     response_data = response.json()
#     registered_user = test_user.copy()
#     registered_user["id"] = response_data["id"]
#     return registered_user


# @pytest.fixture(scope="session") === НЕ АКТУАЛЬНО ===
# def requester():
#     """
#     Фикстура для создания экземпляра CustomRequester.
#     """
#     session = requests.Session()
#     session.headers.update(HEADERS)
#
#     return CustomRequester(session=session, base_url=AUTH_URL)


#фикстуры для api-менеджера в test_auth и test_user:

@pytest.fixture(scope="session")
def session():
    """
    Фикстура для создания HTTP-сессии.

    :return: Чистая сессия.
    """
    http_session = requests.Session()

    yield http_session

    http_session.close()


@pytest.fixture(scope="session")
def api_manager(session):
    """
    Фикстура для создания экземпляра ApiManager.

    :param session: HTTP-сессия, передаваемая в ApiManager.
    :return: Экземпляр ApiManager для управления API-классами.
    """
    return ApiManager(session)


# фикстуры для auth:

@pytest.fixture(scope="session")
def auth_session():
    """
    Фикстура для создания авторизованной HTTP-сессии с правами SUPER_ADMIN.
    Выполняет логин с данными LOGIN_DATA, получает токен и добавляет его в заголовки.

    :return: Сессия с установленным заголовком Authorization.
    """
    session = requests.Session()
    session.headers.update(HEADERS)

    response = requests.post(f"{AUTH_URL}/login", headers=HEADERS, json=LOGIN_DATA)
    assert response.status_code == 200, "Ошибка авторизации"
    token = response.json().get("accessToken")
    assert token is not None, "В ответе не оказалось токена"

    session.headers.update({"Authorization": f"Bearer {token}"})

    yield session

    session.close()


@pytest.fixture(scope="function")
def get_user_id(api_manager):
    """
    Фикстура для получения ID текущего авторизованного пользователя.
    Выполняет логин с данными из login_data_list, извлекает user.id из ответа.

    :param api_manager: Экземпляр ApiManager.
    :return: ID пользователя (строка UUID).
    """
    login_data = {
        "email": login_data_list[0],
        "password": login_data_list[1]
    }

    response = api_manager.auth_api.login_user(login_data).json()
    user_id = response["user"]["id"]

    yield user_id

    api_manager.clear_token()


@pytest.fixture(scope="function")
def create_user(auth_session):
    """
    Фикстура для создания пользователя (обычного, не админа) через админскую сессию.
    Генерирует уникальные email, fullName и пароль, создаёт пользователя через POST /user.

    :param auth_session: Админская сессия.
    :return: Словарь с ключами id, email, full_name созданного пользователя.
    """
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

    response = auth_session.post(f"{AUTH_URL}/user", json=user_data)
    assert response.status_code == 201, f"Ошибка при создании пользователя: {response.text}"

    user_id = response.json()["id"]

    yield {
        "id": user_id,
        "email": email,
        "full_name": full_name
    }

    # Чистим после теста
    auth_session.delete(f"{AUTH_URL}/user/{user_id}")


@pytest.fixture(scope="function")
def register_data():
    """
    Фикстура для генерации случайных данных для регистрации пользователя.
    Использует DataGenerator для email, имени и пароля.

    :return: Словарь с данными для регистрации (email, fullName, password, passwordRepeat, roles).
    """
    email = DataGenerator.generate_random_email()
    full_name = DataGenerator.generate_random_name()
    password = DataGenerator.generate_random_password()  # "Test123456!"

    data = {
        "email": email,
        "fullName": full_name,
        "password": password,
        "passwordRepeat": password,
        "roles": ["USER"]
    }

    return data


# фикстуры для films:

@pytest.fixture(scope="function")
def create_film_with_review(api_manager, film_data, review_data):
    """
    Фикстура для создания фильма с одним отзывом.
    Аутентифицируется как админ, создаёт фильм, затем добавляет к нему отзыв.

    :param api_manager: Экземпляр ApiManager.
    :param film_data: Данные для создания фильма.
    :param review_data: Данные для создания отзыва.
    :return: ID созданного фильма.
    """
    api_manager.authenticate(login_data_list)
    create_movie = api_manager.films_api.create_movie(film_data)
    movie_id = create_movie.json()["id"]

    create_movie_reviews = api_manager.films_api.create_review(movie_id, review_data)
    assert create_movie_reviews.status_code == 201, "Ошибка при создании отзыва к фильму"
    # БАГ: в Swagger ожидается 200, но API возвращает 201.

    yield movie_id

    api_manager.authenticate(login_data_list)
    api_manager.films_api.delete_movie(movie_id)
    api_manager.clear_token()


@pytest.fixture(scope="function")  # переделано под ApiManager
def create_film_id(api_manager, film_data):
    """
    Фикстура для создания фильма и возврата его ID.
    Аутентифицируется как админ, создаёт фильм, возвращает ID, а после теста удаляет фильм.

    :param api_manager: Экземпляр ApiManager.
    :param film_data: Данные для создания фильма.
    :return: ID созданного фильма.
    """
    api_manager.authenticate(login_data_list)
    create_movie = api_manager.films_api.create_movie(film_data)
    movie_id = create_movie.json()["id"]

    yield movie_id

    api_manager.authenticate(login_data_list)
    api_manager.films_api.delete_movie(movie_id)
    api_manager.clear_token()


@pytest.fixture(scope="function")
def genre_data():
    """
    Фикстура для генерации случайных данных для создания жанра.

    :return: Словарь с ключом name (случайная строка + цифра).
    """
    return {
        "name": faker_ru.sentence(nb_words=2) + "1"
    }


@pytest.fixture(scope="function")
def review_data():
    """
    Фикстура для генерации случайных данных для отзыва.

    :return: Словарь с полями rating (1–5) и text (случайное предложение).
    """
    return {
        "rating": faker_ru.random_int(min=1, max=5),
        "text": faker_ru.sentence(nb_words=15)
    }


@pytest.fixture(scope="function")
def film_data():
    """
    Фикстура для генерации случайных данных для фильма.

    :return: Словарь с полями name, imageUrl, price, description, location, published, genreId.
    """
    return {
        "name": faker_ru.sentence(nb_words=4),
        "imageUrl": "https://image.url",
        "price": 100,
        "description": faker_ru.sentence(nb_words=15),
        "location": "SPB",
        "published": True,
        "genreId": 1
    }


@pytest.fixture(scope="function")
def billboard_params():
    """
    Фикстура для генерации параметров запроса GET /movies.

    :return: Словарь с параметрами pageSize, page, minPrice, maxPrice, locations, published, genreId, createdAt.
    """
    return {
        "pageSize": 10,
        "page": faker_ru.random_int(min=1, max=100),
        "minPrice": 1,
        "maxPrice": 1000,
        "locations": ["MSK", "SPB"],  # несколько значений
        "published": True,
        "genreId": 1,
        "createdAt": "asc"
    }


# фикстура для payment:

@pytest.fixture(scope="function")
def valid_card_data():
    """Фикстура с валидными данными карты.
    Используем тестовые данные, которые принимает API."""

    return {
        "cardNumber": "5555555555554444",  # 16 цифр
        "cardHolder": faker_en.name(),      # имя владельца
        "expirationDate": "12/28",          # формат MM/YY
        "securityCode": 123                 # число от 0 до 999
    }


@pytest.fixture(scope="function")
def create_payment_data(create_film_id, valid_card_data):
    """Фикстура с данными для создания оплаты.
    Использует существующий фильм (create_film_id)."""

    return {
        "movieId": create_film_id,
        "amount": faker_ru.random_int(min=1, max=10),
        "card": valid_card_data
    }
