import pytest
from faker import Faker

from constants import login_data_list

faker = Faker('ru_RU')

class TestPositiveMoviesGenres:

    def test_get_genres_without_token(self, api_manager):
        """Позитив: получение списка жанров без токена (PUBLIC ручка).
        Проверяем статус, заголовки и структуру ответа."""
        get_genres = api_manager.films_api.get_genres()

        # Статус и заголовки
        assert get_genres.status_code == 200, "Список жанров не загрузился"
        assert get_genres.headers.get("Content-Type") == "application/json; charset=utf-8", "Неверный Content-Type"

        # Проверка структуры ответа (список жанров)
        genres = get_genres.json()
        assert isinstance(genres, list), "Ответ должен быть списком"
        assert len(genres) > 0, "Список жанров пуст"

        # Проверка структуры первого жанра
        genre = genres[0]
        required_fields = ["id", "name"]
        for field in required_fields:
            assert field in genre, f"У жанра отсутствует поле {field}"

        # Проверка типов
        assert isinstance(genre, dict), f"Жанр должен быть словарём, получено {type(genre)}"
        assert isinstance(genre["id"], int), "id должен быть числом"
        assert isinstance(genre["name"], str), "name должен быть строкой"
        assert genre["name"] is not None, "name не может быть пустым"
        assert genre["id"] > 0, "id должен быть больше 0"

    def test_get_genres_with_token(self, api_manager):
        """Позитив: получение списка жанров с токеном.
        Проверяем статус, заголовки и структуру ответа."""
        api_manager.authenticate(login_data_list)
        get_genres = api_manager.films_api.get_genres()
        api_manager.clear_token()

        # Статус и заголовки
        assert get_genres.status_code == 200, "Список жанров не загрузился с токеном"
        assert get_genres.headers.get("Content-Type") == "application/json; charset=utf-8", "Неверный Content-Type"

        # Проверка структуры ответа (список жанров)
        genres = get_genres.json()
        assert isinstance(genres, list), "Ответ должен быть списком"
        assert len(genres) > 0, "Список жанров пуст"

        # Проверка структуры первого жанра
        genre = genres[0]
        required_fields = ["id", "name"]
        for field in required_fields:
            assert field in genre, f"У жанра отсутствует поле {field}"

        # Проверка типов
        assert isinstance(genre, dict), f"Жанр должен быть словарём, получено {type(genre)}"
        assert isinstance(genre["id"], int), "id должен быть числом"
        assert isinstance(genre["name"], str), "name должен быть строкой"
        assert genre["name"] is not None, "name не может быть пустым"
        assert genre["id"] > 0, "id должен быть больше 0"

    def test_get_genres_structure_multiple(self, api_manager):
        """Позитив: проверка структуры нескольких жанров.
        Убеждаемся, что все жанры в списке имеют корректную структуру."""
        get_genres = api_manager.films_api.get_genres()

        genres = get_genres.json()
        assert isinstance(genres, list)
        assert len(genres) > 0

        # Проверяем первые 10 жанров (не нужно проверять все 1000)
        for genre in genres[:10]:
            assert isinstance(genre, dict), f"Жанр должен быть словарём, получено {type(genre)}"
            assert "id" in genre, "У жанра отсутствует поле id"
            assert "name" in genre, "У жанра отсутствует поле name"
            assert isinstance(genre["id"], int), "id должен быть числом"
            assert isinstance(genre["name"], str), "name должен быть строкой"
            assert genre["id"] > 0, "id должен быть больше 0"
            assert genre["name"] is not None, "name не может быть пустым"

    def test_create_genre(self, api_manager, genre_data):
        """Позитив: создание жанра.
        Проверяем: создание, получение по ID, совпадение данных, удаление."""

        # 1. СОЗДАЁМ ЖАНР
        api_manager.authenticate(login_data_list)
        create_genre = api_manager.films_api.create_genres(genre_data)
        assert create_genre.headers.get("Content-Type") == "application/json; charset=utf-8", "Неверный Content-Type"

        # Проверка структуры ответа
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

        # 2. ПРОВЕРЯЕМ, ЧТО ЖАНР РЕАЛЬНО СОЗДАЛСЯ (GET)
        get_genre = api_manager.films_api.get_genre(genre_id)

        get_data = get_genre.json()
        assert get_data["id"] == genre_id, "id не совпадает"
        assert get_data["name"] == genre_data["name"], "name не совпадает"

        # 3. УДАЛЯЕМ ЖАНР
        api_manager.films_api.delete_genre(genre_id)

        api_manager.clear_token()

    def test_delete_genre(self, api_manager, genre_data):
        """Позитив: удаление жанра.
        Проверяем: создание → удаление → проверка, что жанра больше нет."""

        # 1. СОЗДАЁМ ЖАНР (нужен существующий жанр для удаления)
        api_manager.authenticate(login_data_list)
        create_genre = api_manager.films_api.create_genres(genre_data)

        genre_id = create_genre.json()["id"]

        # 2. УДАЛЯЕМ ЖАНР
        delete_genre = api_manager.films_api.delete_genre(genre_id)
        assert delete_genre.headers.get("Content-Type") == "application/json; charset=utf-8", "Неверный Content-Type"

        # Проверка структуры ответа
        data = delete_genre.json()
        required_fields = ["id", "name"]
        for field in required_fields:
            assert field in data, f"У ответа отсутствует поле {field}"

        # Проверка типов
        assert isinstance(data["id"], int), "id должен быть числом"
        assert isinstance(data["name"], str), "name должен быть строкой"

        # Проверка совпадения с созданным жанром
        assert data["id"] == genre_id, "id не совпадает"
        assert data["name"] == genre_data["name"], "name не совпадает"

        # 3. ПРОВЕРЯЕМ, ЧТО ЖАНР ДЕЙСТВИТЕЛЬНО УДАЛИЛСЯ
        get_deleted = api_manager.films_api.get_genre(genre_id, expected_status=404)
        assert get_deleted.status_code == 404, "Жанр не удалился"

        api_manager.clear_token()

    def test_get_genre_without_token(self, api_manager, genre_data):
        """Позитив: получение жанра по ID без токена (PUBLIC ручка).
        Проверяем статус, заголовки, структуру и содержимое."""

        # 1. Создаём жанр (через админа)
        api_manager.authenticate(login_data_list)
        create_genre = api_manager.films_api.create_genres(genre_data)
        api_manager.clear_token()

        genre_id = create_genre.json()["id"]

        # 2. Получаем жанр по ID без токена
        get_genre = api_manager.films_api.get_genre(genre_id)

        # Статус и заголовки
        assert get_genre.status_code == 200, "Жанр не загрузился без токена"
        assert get_genre.headers.get("Content-Type") == "application/json; charset=utf-8", "Неверный Content-Type"

        # Проверка структуры ответа
        data = get_genre.json()
        required_fields = ["id", "name"]
        for field in required_fields:
            assert field in data, f"У ответа отсутствует поле {field}"

        # Проверка типов
        assert isinstance(data["id"], int), "id должен быть числом"
        assert isinstance(data["name"], str), "name должен быть строкой"

        # Проверка значений
        assert data["id"] == genre_id, "id не совпадает"
        assert data["name"] == genre_data["name"], "name не совпадает"

        # 3. Чистим
        api_manager.authenticate(login_data_list)
        api_manager.films_api.delete_genre(genre_id)
        api_manager.clear_token()

    def test_get_genre_with_token(self, api_manager, genre_data):
        """Позитив: получение жанра по ID с токеном.
        Проверяем статус, заголовки, структуру и содержимое."""

        # 1. Создаём жанр
        api_manager.authenticate(login_data_list)
        create_genre = api_manager.films_api.create_genres(genre_data)
        genre_id = create_genre.json()["id"]

        # 2. Получаем жанр по ID с токеном
        get_genre = api_manager.films_api.get_genre(genre_id)

        # Статус и заголовки
        assert get_genre.status_code == 200, "Жанр не загрузился с токеном"
        assert get_genre.headers.get("Content-Type") == "application/json; charset=utf-8", "Неверный Content-Type"

        # Проверка структуры ответа
        data = get_genre.json()
        required_fields = ["id", "name"]
        for field in required_fields:
            assert field in data, f"У ответа отсутствует поле {field}"

        # Проверка типов
        assert isinstance(data["id"], int), "id должен быть числом"
        assert isinstance(data["name"], str), "name должен быть строкой"

        # Проверка значений
        assert data["id"] == genre_id, "id не совпадает"
        assert data["name"] == genre_data["name"], "name не совпадает"

        # 3. Чистим
        api_manager.films_api.delete_genre(genre_id)
        api_manager.clear_token()


class TestNegativeMoviesGenres:

    # ========== СОЗДАНИЕ ЖАНРА (негатив) ==========
    def test_create_genre_without_token(self, api_manager, genre_data):
        """Негатив: создание жанра без авторизации (только SUPER_ADMIN)"""
        response = api_manager.films_api.create_genres(genre_data, expected_status=401)
        assert response.status_code == 401, "Жанр создался без авторизации"
        api_manager.clear_token()

    def test_create_genre_with_invalid_token(self, api_manager, genre_data):
        """Негатив: создание жанра с неверным токеном"""
        api_manager.set_token("invalid_token")
        response = api_manager.films_api.create_genres(genre_data, expected_status=401)
        assert response.status_code == 401, "Жанр создался с неверным токеном"
        api_manager.clear_token()

    @pytest.mark.skip(reason="БАГ: сервер возвращает 201 вместо 400")
    def test_create_genre_empty_name(self, api_manager):
        """Негатив: создание жанра с пустым именем"""
        api_manager.authenticate(login_data_list)
        response = api_manager.films_api.create_genres({"name": ""}, expected_status=400)
        assert response.status_code == 400, "Жанр создался с пустым именем"
        api_manager.clear_token()

    def test_create_genre_duplicate(self, api_manager, genre_data):
        """Негатив: создание жанра с уже существующим именем"""
        api_manager.authenticate(login_data_list)

        # Создаём первый жанр
        response1 = api_manager.films_api.create_genres(genre_data)
        assert response1.status_code == 201
        genre_id = response1.json()["id"]

        # Пытаемся создать дубликат
        response2 = api_manager.films_api.create_genres(genre_data, expected_status=409)
        assert response2.status_code == 409, "Создался дубликат жанра"

        # Чистим
        api_manager.films_api.delete_genre(genre_id)
        api_manager.clear_token()

    def test_create_genre_empty_body(self, api_manager):
        """Негатив: создание жанра с пустым телом запроса"""
        api_manager.authenticate(login_data_list)
        response = api_manager.films_api.create_genres({}, expected_status=400)
        assert response.status_code == 400, "Жанр создался с пустым телом"
        api_manager.clear_token()

    def test_create_genre_missing_name(self, api_manager):
        """Негатив: создание жанра без поля name"""
        api_manager.authenticate(login_data_list)
        response = api_manager.films_api.create_genres({"wrong_field": "value"}, expected_status=400)
        assert response.status_code == 400, "Жанр создался без поля name"
        api_manager.clear_token()

    def test_create_genre_extra_field(self, api_manager):
        """Негатив/Позитив: создание жанра с лишним полем.
        API должно проигнорировать лишнее поле и создать жанр."""

        api_manager.authenticate(login_data_list)
        genre_name = faker.sentence(nb_words=2) + "1"

        # 1. СОЗДАЁМ ЖАНР С ЛИШНИМ ПОЛЕМ
        response = api_manager.films_api.create_genres({
            "name": genre_name,
            "wrong_field": "value"
        }, expected_status=201)

        assert response.status_code == 201, "Жанр не создался из-за лишнего поля"

        data = response.json()
        genre_id = data["id"]

        # 2. ПРОВЕРЯЕМ, ЧТО В ОТВЕТЕ ТОЛЬКО id И name
        assert list(data.keys()) == ["id", "name"], "В ответе есть лишние поля"
        assert isinstance(data["id"], int)
        assert isinstance(data["name"], str)
        assert data["name"] == genre_name

        # 3. ПРОВЕРЯЕМ, ЧТО ЖАНР РЕАЛЬНО СОЗДАЛСЯ (GET)
        get_genre = api_manager.films_api.get_genre(genre_id)
        assert get_genre.status_code == 200, "Жанр не найден после создания"

        get_data = get_genre.json()
        assert get_data["id"] == genre_id
        assert get_data["name"] == genre_name

        # 4. ЧИСТИМ
        api_manager.films_api.delete_genre(genre_id)
        api_manager.clear_token()

    # ========== УДАЛЕНИЕ ЖАНРА (негатив) ==========
    def test_delete_genre_without_token(self, api_manager, genre_data):
        """Негатив: удаление жанра без авторизации (только SUPER_ADMIN)"""
        api_manager.authenticate(login_data_list)

        # Создаём жанр
        create_genre = api_manager.films_api.create_genres(genre_data)
        assert create_genre.status_code == 201
        genre_id = create_genre.json()["id"]

        # Пытаемся удалить без токена
        api_manager.clear_token()
        response = api_manager.films_api.delete_genre(genre_id, expected_status=401)
        assert response.status_code == 401, "Жанр удалился без авторизации"

        # Чистим
        api_manager.authenticate(login_data_list)
        api_manager.films_api.delete_genre(genre_id)
        api_manager.clear_token()

    def test_delete_genre_with_invalid_token(self, api_manager, genre_data):
        """Негатив: удаление жанра с неверным токеном"""
        api_manager.authenticate(login_data_list)

        # Создаём жанр
        create_genre = api_manager.films_api.create_genres(genre_data)
        assert create_genre.status_code == 201
        genre_id = create_genre.json()["id"]

        # Пытаемся удалить с неверным токеном
        api_manager.set_token("invalid_token")
        response = api_manager.films_api.delete_genre(genre_id, expected_status=401)
        assert response.status_code == 401, "Жанр удалился с неверным токеном"

        # Чистим
        api_manager.authenticate(login_data_list)
        api_manager.films_api.delete_genre(genre_id)
        api_manager.clear_token()

    def test_delete_genre_invalid_id(self, api_manager):
        """Негатив: удаление жанра с несуществующим ID"""
        api_manager.authenticate(login_data_list)
        response = api_manager.films_api.delete_genre(999999, expected_status=404)
        assert response.status_code == 404, "Удалился несуществующий жанр"
        api_manager.clear_token()

    def test_delete_genre_negative_id(self, api_manager):
        """Негатив: удаление жанра с отрицательным ID"""
        api_manager.authenticate(login_data_list)
        response = api_manager.films_api.delete_genre(-1, expected_status=404)
        assert response.status_code == 404, "Отрицательный ID обработался неверно"
        api_manager.clear_token()

    def test_delete_genre_zero_id(self, api_manager):
        """Негатив: удаление жанра с ID = 0"""
        api_manager.authenticate(login_data_list)
        response = api_manager.films_api.delete_genre(0, expected_status=404)
        assert response.status_code == 404, "ID = 0 обработался неверно"
        api_manager.clear_token()

    def test_delete_genre_string_id(self, api_manager):
        """Негатив: удаление жанра с ID в виде строки"""
        api_manager.authenticate(login_data_list)
        response = api_manager.films_api.delete_genre("abc", expected_status=404)
        assert response.status_code == 404, "Строковый ID не вызвал ошибку"
        api_manager.clear_token()

    def test_delete_genre_twice(self, api_manager, genre_data):
        """Негатив: повторное удаление уже удалённого жанра"""
        api_manager.authenticate(login_data_list)

        # Создаём жанр
        create_genre = api_manager.films_api.create_genres(genre_data)
        assert create_genre.status_code == 201
        genre_id = create_genre.json()["id"]

        # Первое удаление
        response1 = api_manager.films_api.delete_genre(genre_id)
        assert response1.status_code == 200

        # Второе удаление
        response2 = api_manager.films_api.delete_genre(genre_id, expected_status=404)
        assert response2.status_code == 404, "Повторное удаление не вызвало ошибку"

        api_manager.clear_token()

    # ========== ПОЛУЧЕНИЕ ЖАНРА ПО ID (негатив) ==========
    def test_get_genre_invalid_id(self, api_manager):
        """Негатив: получение жанра с несуществующим ID"""
        response = api_manager.films_api.get_genre(999999, expected_status=404)
        assert response.status_code == 404, "Нашёлся жанр с несуществующим ID"

    def test_get_genre_negative_id(self, api_manager):
        """Негатив: получение жанра с отрицательным ID"""
        response = api_manager.films_api.get_genre(-1, expected_status=404)
        assert response.status_code == 404, "Отрицательный ID обработался неверно"

    def test_get_genre_zero_id(self, api_manager):
        """Негатив: получение жанра с ID = 0"""
        response = api_manager.films_api.get_genre(0, expected_status=404)
        assert response.status_code == 404, "ID = 0 обработался неверно"

    def test_get_genre_string_id(self, api_manager):
        """Негатив: получение жанра с ID в виде строки"""
        response = api_manager.films_api.get_genre("abc", expected_status=404)
        assert response.status_code == 404, "Строковый ID не вызвал ошибку"
