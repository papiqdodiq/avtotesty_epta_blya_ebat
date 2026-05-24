import pytest
import requests
from faker import Faker

from for_custom_requester.constants import BASE_URL, REGISTER_ENDPOINT
from custom_requester.custom_requester import CustomRequester
from utils.data_generator import DataGenerator
from clients.api_manager import ApiManager

from resources.user_creds import SuperAdminCreds, AdminCreds
from entities.user import User
from enum_constants.roles import Roles

from models.base_models import TestUser

faker = Faker()

#фикстуры для создании сессии юзера (ролевая модель, начало 5 модуля):

@pytest.fixture(scope="function") # общая фикстура для admin, super_admin и common_user
def user_session():
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

    admin.api.auth_api.authenticate(admin.creds) # лучше вызывать super_admin.api.authenticate
    return admin

@pytest.fixture
def super_admin(user_session):
    new_session = user_session()

    super_admin = User(
        SuperAdminCreds.USERNAME,
        SuperAdminCreds.PASSWORD,
        [Roles.SUPER_ADMIN.value],
        new_session)

    super_admin.api.auth_api.authenticate(super_admin.creds) # лучше вызывать super_admin.api.authenticate
    return super_admin

@pytest.fixture
def common_user(user_session, super_admin, creation_user_data):
    new_session = user_session()

    common_user = User(
        creation_user_data['email'],
        creation_user_data['password'],
        [Roles.USER.value],
        new_session)

    super_admin.api.user_api.create_user(creation_user_data)
    common_user.api.auth_api.authenticate(common_user.creds) # лучше вызывать super_admin.api.authenticate
    return common_user

@pytest.fixture(scope="function")
def creation_user_data(test_user): # для негативных тестов
    """
    Создание данных пользователя с дополнительными полями verified и banned.
    """
    updated_data = test_user.copy()
    updated_data.update({
        "verified": True,
        "banned": False
    })
    return updated_data

@pytest.fixture(scope="function")
def creation_user_data_pydantic(test_user_pydantic):
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

# остальные фикстуры:

@pytest.fixture
def test_user(): # для негативных тестов
    """
    Генерация случайного пользователя для тестов.
    """
    random_email = DataGenerator.generate_random_email()
    random_name = DataGenerator.generate_random_name()
    random_password = DataGenerator.generate_random_password()

    return {
        "email": random_email,
        "fullName": random_name,
        "password": random_password,
        "passwordRepeat": random_password,
        "roles": [Roles.USER.value]
    }

@pytest.fixture(scope="function")
def test_user_pydantic() -> TestUser:
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

@pytest.fixture(scope="function")
def registered_user(requester, test_user):
    """
    Фикстура для регистрации и получения данных зарегистрированного пользователя.
    """
    response = requester.send_request(
        method="POST",
        endpoint=REGISTER_ENDPOINT,
        data=test_user,
        expected_status=201
    )
    response_data = response.json()
    registered_user = test_user.copy()
    registered_user["id"] = response_data["id"]
    return registered_user

@pytest.fixture(scope="session")
def requester():
    """
    Фикстура для создания экземпляра CustomRequester.
    """
    session = requests.Session()
    return CustomRequester(session=session, base_url=BASE_URL)

#фикстуры для централизации:
@pytest.fixture(scope="session")
def session():
    """
    Фикстура для создания HTTP-сессии.
    """
    http_session = requests.Session()
    yield http_session
    http_session.close()

@pytest.fixture(scope="session")
def api_manager(session):
    """
    Фикстура для создания экземпляра ApiManager.
    """
    return ApiManager(session)