import pytest
import requests
from faker import Faker

from constants import HEADERS, LOGIN_DATA, login_data_list, AUTH_URL, MOVIES_URL, CURRENT_USER_ID, REGISTER_ENDPOINT
from custom_requester.custom_requester import CustomRequester
from utils.data_generator import DataGenerator
from utils.validators import assert_valid_uuid, assert_valid_iso_datetime, assert_datetime_in_range
from datetime import datetime, timezone, timedelta
from clients.api_manager import ApiManager

from resources.user_creds import SuperAdminCreds, AdminCreds
from entities.user import User
from enum_constants.roles import Roles

from models.base_models import TestUser, CreateUserData, CreateUserResponse

faker_ru = Faker('ru_RU')
faker_en = Faker('en_US')


#фикстуры для создании сессии юзера (ролевая модель, начало 5 модуля):

@pytest.fixture(scope="session")
def user_session():  # общая фикстура для admin, super_admin и common_user
    user_pool = []

    def _create_user_session():
        session = requests.Session()
        user_session = ApiManager(session)
        user_pool.append(user_session)
        return user_session

    yield _create_user_session

    for user in user_pool:
        user.close_session()


@pytest.fixture
def admin(user_session):
    new_session = user_session()

    admin = User(
        AdminCreds.USERNAME,
        AdminCreds.PASSWORD,
        [Roles.ADMIN.value],
        new_session)

    admin.api.authenticate(admin.creds) # во всех апи-классах одновременно
    return admin


@pytest.fixture
def super_admin(user_session):
    new_session = user_session()

    super_admin = User(
        SuperAdminCreds.USERNAME,
        SuperAdminCreds.PASSWORD,
        [Roles.SUPER_ADMIN.value],
        new_session)

    super_admin.api.authenticate(super_admin.creds) # во всех апи-классах одновременно
    return super_admin


@pytest.fixture
def common_user(user_session, super_admin, create_user_data):
    new_session = user_session()

    common_user = User(
        create_user_data['email'],
        create_user_data['password'],
        [Roles.USER.value],
        new_session)

    super_admin.api.user_api.create_user(create_user_data)
    common_user.api.authenticate(common_user.creds) # во всех апи-классах одновременно
    return common_user


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
def admin_session():
    """
    Фикстура для создания HTTP-сессии с авторизацией администратора.
    Логинимся один раз, сохраняем токен в сессию.
    """
    session = requests.Session()
    session.headers.update(HEADERS)

    # Логинимся как админ
    login_data = {
        "email": login_data_list[0],
        "password": login_data_list[1]
    }
    response = session.post(f"{AUTH_URL}/login", json=login_data)
    assert response.status_code == 200
    token = response.json().get("accessToken")
    assert token is not None

    session.headers.update({"Authorization": f"Bearer {token}"})

    yield session

    session.close()


@pytest.fixture(scope="session")
def api_manager(session):
    """
    Фикстура для создания экземпляра ApiManager.

    :param session: HTTP-сессия, передаваемая в ApiManager.
    :return: Экземпляр ApiManager для управления API-классами.
    """
    return ApiManager(session)


@pytest.fixture(scope="session")
def api_manager_admin(admin_session):
    """
    Экземпляр ApiManager с уже авторизованной сессией (админ).
    """
    return ApiManager(admin_session)


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

    # Проверка формата UUID
    assert_valid_uuid(response["user"]["id"])

    user_id = response["user"]["id"]

    return user_id


@pytest.fixture(scope="function")
def create_user(auth_session, register_data):
    """
    Фикстура для создания пользователя (обычного, не админа) через админскую сессию.
    Генерирует уникальные email, fullName и пароль, создаёт пользователя через POST /user.

    :param register_data: Данные для регистрации из фикстуры.
    :param auth_session: Админская сессия.
    :return: Словарь с ключами id, email, full_name созданного пользователя.
    """

    user_data = {
        "email": register_data["email"],
        "fullName": register_data["fullName"],
        "password": register_data["password"],
        "verified": True,
        "banned": False
    }

    response = auth_session.post(f"{AUTH_URL}/user", json=user_data)
    assert response.status_code == 201, f"Ошибка при создании пользователя: {response.text}"

    # Проверка формата UUID
    assert_valid_uuid(response.json()["id"])

    user_id = response.json()["id"]

    yield {
        "id": user_id,
        "email": register_data["email"],
        "full_name": register_data["fullName"]
    }

    # Чистим после теста
    auth_session.delete(f"{AUTH_URL}/user/{user_id}")


@pytest.fixture(scope="function")
def create_user_pydantic(api_manager_admin, register_data_pydantic):
    """
    Фикстура для создания пользователя (обычного, не админа) через админскую сессию.
    Генерирует уникальные email, fullName и пароль, создаёт пользователя через POST /user.
    Использует Pydantic модель CreateTestUser.

    :param register_data_pydantic: Данные для регистрации из пайдентик фикстуры.
    :param api_manager_admin: Админская сессия.
    :return: Словарь с ключами id, email, full_name созданного пользователя.
    """

    user_data = CreateUserData(
        email=register_data_pydantic.email,
        fullName=register_data_pydantic.fullName,
        password=register_data_pydantic.password,
        verified=True,
        banned=False
    )

    response = api_manager_admin.user_api.create_user(user_data.model_dump())

    data = CreateUserResponse(**response.json())

    user_id = data.id

    yield {
        "id": user_id,
        "email": register_data_pydantic.email,
        "full_name": register_data_pydantic.fullName
    }

    # Чистим после теста
    api_manager_admin.user_api.delete_user(user_id)


@pytest.fixture(scope="function")
def register_data(): # для негативных тестов
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
        "roles": [Roles.USER.value]
    }

    return data


@pytest.fixture(scope="function")
def register_data_pydantic() -> TestUser:
    """
    Генерация случайного пользователя для тестов.
    Использует Pydantic модель TestUser.
    """
    random_email = DataGenerator.generate_random_email()
    random_name = DataGenerator.generate_random_name()
    random_password = DataGenerator.generate_random_password()

    return TestUser(
        email=random_email,
        fullName=random_name,
        password=random_password,
        passwordRepeat=random_password,
        roles=[Roles.USER]
    )


@pytest.fixture(scope="function") # для test_user (register_data) (ролевая модель, 5 модуль), название отличается от обучалки
def create_user_data(register_data): # для негативных тестов
    updated_data = register_data.copy()
    updated_data.update({
        "verified": True,
        "banned": False
    })
    return updated_data


@pytest.fixture(scope="function")
def create_user_data_pydantic(test_user_pydantic):
    """
    Создание данных пользователя с дополнительными полями verified и banned.
    Использует Pydantic модель TestUser.
    """
    # Создаем копию модели и обновляем поля
    updated_user = test_user_pydantic.model_copy(update={
        "verified": True,
        "banned": False
    })
    return updated_user


# фикстуры для films:


@pytest.fixture(scope="function")
def film_should_exist_after_test(create_film_id, api_manager_admin):
    yield  # тест выполняется здесь
    # После теста проверяем что фильм существует
    api_manager_admin.films_api.get_movie(create_film_id)


@pytest.fixture(scope="function")
def create_film_with_review(api_manager_admin, create_film_response, review_data, get_user_id):
    """
    Фикстура для создания фильма с одним отзывом.
    Аутентифицируется как админ, создаёт фильм, затем добавляет к нему отзыв.

    :param get_user_id: Получение идентификатора юзера из админского ApiManager.
    :param api_manager_admin: Экземпляр админского ApiManager.
    :param create_film_response: Фикстура для создания фильма.
    :param review_data: Данные для создания отзыва.
    :return: ID созданного фильма.
    """

    movie_id = create_film_response.json()["id"]

    before_request = datetime.now(timezone.utc) - timedelta(seconds=5) # я так делаю, потому что серверное время
    # в один момент начинает от времени на моем ноуте, хз почему
    create_review = api_manager_admin.films_api.create_review(movie_id, review_data)
    after_request = datetime.now(timezone.utc) + timedelta(seconds=10)

    create_data = create_review.json()
    required_fields = ["userId", "rating", "text", "createdAt", "user"]
    for field in required_fields:
        assert field in create_data, f"У отзыва отсутствует поле {field}"

    assert isinstance(create_data["userId"], str)
    assert isinstance(create_data["rating"], int)
    assert isinstance(create_data["text"], str)
    assert isinstance(create_data["user"], dict)
    assert "fullName" in create_data["user"]

    # Проверяем формат createdAt через чекеры
    assert_valid_iso_datetime(create_data["createdAt"])
    assert_datetime_in_range(create_data["createdAt"], before_request, after_request)

    assert create_data["rating"] == review_data["rating"]
    assert create_data["text"] == review_data["text"]
    assert 1 <= create_data["rating"] <= 5
    assert create_data["userId"] == get_user_id

    yield movie_id


@pytest.fixture(scope="function")  # переделано под ApiManager
def create_film_response(api_manager_admin, film_data):
    """
    Фикстура для создания фильма и возврата его ID.
    Аутентифицируется как админ, создаёт фильм, возвращает ID, а после теста удаляет фильм.

    :param api_manager_admin: Экземпляр админского ApiManager.
    :param film_data: Данные для создания фильма.
    :return: ID созданного фильма.
    """
    before_request = datetime.now(timezone.utc) - timedelta(seconds=5) # я так делаю, потому что серверное время
    # в один момент начинает от времени на моем ноуте, хз почему
    create_movie = api_manager_admin.films_api.create_movie(film_data)
    after_request = datetime.now(timezone.utc) + timedelta(seconds=10)

    create_data = create_movie.json()

    # Проверяем структуру ответа на создание
    required_fields = ["id", "name", "price", "description", "imageUrl",
                       "location", "published", "genreId", "genre", "createdAt", "rating"]
    for field in required_fields:
        assert field in create_data, f"Отсутствует поле {field}"

    # Проверяем типы в ответе на создание
    assert isinstance(create_data["id"], int)
    assert isinstance(create_data["name"], str)
    assert isinstance(create_data["price"], int)
    assert isinstance(create_data["published"], bool)
    assert isinstance(create_data["genreId"], int)
    assert isinstance(create_data["genre"], dict)
    assert "name" in create_data["genre"]

    # Проверяем формат createdAt через чекеры
    assert_valid_iso_datetime(create_data["createdAt"])
    assert_datetime_in_range(create_data["createdAt"], before_request, after_request)

    movie_id = create_data["id"]

    yield create_movie

    api_manager_admin.films_api.delete_movie(movie_id)


@pytest.fixture(scope="function")  # переделано под ApiManager
def create_film_id(api_manager_admin, create_film_response):
    """
    Фикстура для создания фильма и возврата его ID.
    Аутентифицируется как админ, создаёт фильм, возвращает ID, а после теста удаляет фильм.

    :param api_manager_admin: Экземпляр админского ApiManager.
    :param create_film_response: Фикстура для создания фильма.
    :return: ID созданного фильма.
    """

    movie_id = create_film_response.json()["id"]

    yield movie_id


@pytest.fixture(scope="function")
def create_genre_id(api_manager_admin, genre_data):
    """
    Фикстура для создания жанра и возврата его ID.
    Аутентифицируется как админ, создаёт жанр, проверяет структуру ответа,
    возвращает ID жанра, а после теста удаляет жанр.

    :param api_manager_admin: Экземпляр админского ApiManager.
    :param genre_data: Данные для создания жанра.
    :return: ID созданного жанра.
    """
    create_genre = api_manager_admin.films_api.create_genres(genre_data)
    data = create_genre.json()
    required_fields = ["id", "name"]
    for field in required_fields:
        assert field in data, f"У ответа отсутствует поле {field}"

    # Проверка типов
    assert isinstance(data["id"], int), "id должен быть числом"
    assert isinstance(data["name"], str), "name должен быть строкой"

    # Проверка значений
    assert data["name"] == genre_data["name"], "name не совпадает"
    assert data["id"] > 0, "id должен быть больше 0"

    genre_id = data["id"]

    yield genre_id

    api_manager_admin.films_api.delete_genre(genre_id)


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
