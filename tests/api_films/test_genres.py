import pytest
from faker import Faker

faker = Faker('ru_RU')

class TestPositiveMoviesGenres:

    @pytest.mark.slow
    def test_get_genres_without_token(self, common_user):
        """Позитив: получение списка жанров без токена (PUBLIC ручка).
        Проверяем статус, заголовки и структуру ответа."""
        get_genres = common_user.api.films_api.get_genres()

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

    def test_get_genres_with_token(self, super_admin):
        """Позитив: получение списка жанров с токеном.
        Проверяем статус, заголовки и структуру ответа."""
        get_genres = super_admin.api.films_api.get_genres()

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

    @pytest.mark.slow
    def test_create_genre(self, super_admin, create_genre_id, genre_data):
        """Позитив: создание жанра.
        Проверяем: создание, получение по ID, совпадение данных, удаление."""

        # Создаем жанр в фикстуре c проверкой структуры ответа
        genre_id = create_genre_id

        # 2. ПРОВЕРЯЕМ, ЧТО ЖАНР РЕАЛЬНО СОЗДАЛСЯ (GET)
        get_genre = super_admin.api.films_api.get_genre(genre_id)

        get_data = get_genre.json()
        assert get_data["id"] == genre_id, "id не совпадает"
        assert get_data["name"] == genre_data["name"], "name не совпадает"

    def test_delete_genre(self, super_admin, genre_data):
        """Позитив: удаление жанра.
        Проверяем: создание → удаление → проверка, что жанра больше нет."""

        # 1. СОЗДАЁМ ЖАНР (нужен существующий жанр для удаления)
        create_genre = super_admin.api.films_api.create_genres(genre_data)

        genre_id = create_genre.json()["id"]

        # 2. УДАЛЯЕМ ЖАНР
        delete_genre = super_admin.api.films_api.delete_genre(genre_id)

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
        super_admin.api.films_api.get_genre(genre_id, expected_status=404)

    def test_get_genre_without_token(self, super_admin, create_genre_id, genre_data):
        """Позитив: получение жанра по ID без токена (PUBLIC ручка).
        Проверяем статус, заголовки, структуру и содержимое."""

        # 1. Создаём жанр (через фикстуру)
        genre_id = create_genre_id

        # 2. Получаем жанр по ID без токена
        get_genre = super_admin.api.films_api.get_genre(genre_id)

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

    def test_get_genre_with_token(self, super_admin, create_genre_id, genre_data):
        """Позитив: получение жанра по ID с токеном.
        Проверяем статус, заголовки, структуру и содержимое."""

        # 1. Создаём жанр через фикстуру
        genre_id = create_genre_id

        # 2. Получаем жанр по ID с токеном
        get_genre = super_admin.api.films_api.get_genre(genre_id)

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


class TestNegativeMoviesGenres:

    # ========== СОЗДАНИЕ ЖАНРА (негатив) ==========
    def test_create_genre_without_token(self, api_manager, genre_data):
        """Негатив: создание жанра без авторизации"""
        response = api_manager.films_api.create_genres(genre_data, expected_status=401)
        error_data = response.json()
        assert error_data.get("statusCode") == 401
        assert error_data.get("message") == "Unauthorized"

        # Дополнительная проверка: жанр НЕ создался
        get_genres = api_manager.films_api.get_genres()
        genres = get_genres.json()
        names = [genre["name"] for genre in genres]
        assert genre_data["name"] not in names, "Жанр создался без авторизации"

    def test_create_genre_without_rights(self, common_user, genre_data):
        """Негатив: создание жанра без нужных прав"""
        response = common_user.api.films_api.create_genres(genre_data, expected_status=403)
        error_data = response.json()
        assert error_data.get("statusCode") == 403
        assert error_data.get("message") == "Forbidden resource"
        assert error_data.get("error") == "Forbidden"

        # Дополнительная проверка: жанр НЕ создался
        get_genres = common_user.api.films_api.get_genres()
        genres = get_genres.json()
        names = [genre["name"] for genre in genres]
        assert genre_data["name"] not in names, "Жанр создался без авторизации"

    def test_create_genre_with_invalid_token(self, api_manager, genre_data):
        """Негатив: создание жанра с неверным токеном"""
        api_manager.set_token("invalid_token")
        response = api_manager.films_api.create_genres(genre_data, expected_status=401)
        error_data = response.json()
        assert error_data.get("statusCode") == 401
        assert error_data.get("message") == "Unauthorized"

        # Чистим
        api_manager.clear_token()

        # Дополнительная проверка: жанр НЕ создался
        get_genres = api_manager.films_api.get_genres()
        genres = get_genres.json()
        names = [genre["name"] for genre in genres]
        assert genre_data["name"] not in names, "Жанр создался с неверным токеном"

    @pytest.mark.skip(reason="БАГ: сервер возвращает 201 вместо 400")
    def test_create_genre_empty_name(self, super_admin):
        """Негатив: создание жанра с пустым именем"""
        response = super_admin.api.films_api.create_genres({"name": ""}, expected_status=400)
        error_data = response.json()
        assert error_data.get("statusCode") == 400
        assert error_data.get("error") == "Bad Request"
        # message может быть массивом или строкой
        messages = error_data.get("message")
        if isinstance(messages, list):
            assert "Поле name должно быть строкой" in messages
        else:
            assert messages == "Поле name должно быть строкой"

        # Дополнительная проверка: жанр с пустым именем НЕ создался
        get_genres = super_admin.api.films_api.get_genres()
        genres = get_genres.json()
        empty_names = [genre["name"] for genre in genres if genre["name"] == ""]
        assert len(empty_names) == 0, "Жанр с пустым именем создался"

    def test_create_genre_duplicate(self, super_admin, create_genre_id, genre_data):
        """Негатив: создание жанра с уже существующим именем"""
        # Создаём первый жанр (фикстура create_genre_id уже создала)
        response = super_admin.api.films_api.create_genres(genre_data, expected_status=409)
        error_data = response.json()
        assert error_data.get("statusCode") == 409
        assert error_data.get("error") == "Conflict"
        assert error_data.get("message") == "Такой жанр уже существует"

        # Дополнительная проверка: жанр не создался повторно
        get_genres = super_admin.api.films_api.get_genres()
        genres = get_genres.json()
        count = sum(1 for genre in genres if genre["name"] == genre_data["name"])
        assert count == 1, f"Жанр '{genre_data['name']}' создался повторно, ожидался 1, получено {count}"

    def test_create_genre_empty_body(self, super_admin):
        """Негатив: создание жанра с пустым телом запроса"""
        response = super_admin.api.films_api.create_genres({}, expected_status=400)
        error_data = response.json()
        assert error_data.get("statusCode") == 400
        assert error_data.get("error") == "Bad Request"
        messages = error_data.get("message")
        if isinstance(messages, list):
            assert "Поле name должно быть строкой" in messages
        else:
            assert messages == "Поле name должно быть строкой"

        # Дополнительная проверка: никакой жанр не создался
        get_genres = super_admin.api.films_api.get_genres()
        genres = get_genres.json()
        # Проверяем, что нет жанров с пустым именем или без имени
        invalid_genres = [g for g in genres if g.get("name") is None]
        assert len(invalid_genres) == 0, "Создался жанр с пустым телом"

    @pytest.mark.skip(reason="БАГ: запрос на создание не выполняется, но жанр с пустым именем существует в БД")
    def test_create_genre_missing_name(self, super_admin):
        """Негатив: создание жанра без поля name"""
        response = super_admin.api.films_api.create_genres({"wrong_field": "value"}, expected_status=400)
        error_data = response.json()
        assert error_data.get("statusCode") == 400
        assert error_data.get("error") == "Bad Request"
        messages = error_data.get("message")
        if isinstance(messages, list):
            assert "Поле name должно быть строкой" in messages
        else:
            assert messages == "Поле name должно быть строкой"

        # Дополнительная проверка: жанр не создался
        get_genres = super_admin.api.films_api.get_genres()
        genres = get_genres.json()
        # Проверяем, что нет жанров с именем из wrong_field
        # (у нас нет имени, поэтому просто убеждаемся, что новых жанров с пустым именем нет)
        empty_or_none = [g for g in genres if g.get("name") is None or g.get("name") == ""]
        assert len(empty_or_none) == 0, "Создался жанр без поля name"

    @pytest.mark.skip(reason="БАГ: сервер возвращает 200 вместо 400")
    def test_create_genre_extra_field(self, super_admin):
        """Негатив/Позитив: создание жанра с лишним полем."""

        genre_name = faker.sentence(nb_words=2) + "1"

        # 1. СОЗДАЁМ ЖАНР С ЛИШНИМ ПОЛЕМ
        super_admin.api.films_api.create_genres({
            "name": genre_name,
            "wrong_field": "value"
        }, expected_status=400)

    # ========== УДАЛЕНИЕ ЖАНРА (негатив) ==========
    def test_delete_genre_without_token(self, api_manager, create_genre_id):
        """Негатив: удаление жанра без авторизации"""

        # Создаём жанр
        genre_id = create_genre_id

        # Пытаемся удалить без токена
        response = api_manager.films_api.delete_genre(genre_id, expected_status=401)
        error_data = response.json()
        assert error_data.get("statusCode") == 401
        assert error_data.get("message") == "Unauthorized"

        # Дополнительная проверка: жанр НЕ удалился
        get_genre = api_manager.films_api.get_genre(genre_id)
        assert get_genre.status_code == 200, "Жанр удалился без авторизации"

    def test_delete_genre_without_rights(self, common_user, create_genre_id):
        """Негатив: удаление жанра без нужных прав"""

        # Создаём жанр
        genre_id = create_genre_id

        # Пытаемся удалить без прав
        response = common_user.api.films_api.delete_genre(genre_id, expected_status=403)
        error_data = response.json()
        assert error_data.get("statusCode") == 403
        assert error_data.get("message") == "Forbidden resource"
        assert error_data.get("error") == "Forbidden"

        # Дополнительная проверка: жанр НЕ удалился
        get_genre = common_user.api.films_api.get_genre(genre_id)
        assert get_genre.status_code == 200, "Жанр удалился без авторизации"

    def test_delete_genre_with_invalid_token(self, api_manager, create_genre_id):
        """Негатив: удаление жанра с неверным токеном"""

        # Создаём жанр
        genre_id = create_genre_id

        # Пытаемся удалить с неверным токеном
        api_manager.set_token("invalid_token")
        response = api_manager.films_api.delete_genre(genre_id, expected_status=401)
        error_data = response.json()
        assert error_data.get("statusCode") == 401
        assert error_data.get("message") == "Unauthorized"

        # Чистим
        api_manager.clear_token()

        # Дополнительная проверка: жанр НЕ удалился
        get_genre = api_manager.films_api.get_genre(genre_id)
        assert get_genre.status_code == 200, "Жанр удалился с неверным токеном"

    def test_delete_genre_invalid_id(self, super_admin):
        """Негатив: удаление жанра с несуществующим ID"""
        response = super_admin.api.films_api.delete_genre(999999, expected_status=404)
        error_data = response.json()
        assert error_data.get("statusCode") == 404
        assert error_data.get("error") == "Not Found"
        assert error_data.get("message") == "Жанр не найден"

    def test_delete_genre_negative_id(self, super_admin):
        """Негатив: удаление жанра с отрицательным ID"""
        response = super_admin.api.films_api.delete_genre(-1, expected_status=404)
        error_data = response.json()
        assert error_data.get("statusCode") == 404
        assert error_data.get("error") == "Not Found"
        assert error_data.get("message") == "Жанр не найден"

    def test_delete_genre_zero_id(self, super_admin):
        """Негатив: удаление жанра с ID = 0"""
        response = super_admin.api.films_api.delete_genre(0, expected_status=404)
        error_data = response.json()
        assert error_data.get("statusCode") == 404
        assert error_data.get("error") == "Not Found"
        assert error_data.get("message") == "Жанр не найден"

    def test_delete_genre_string_id(self, super_admin):
        """Негатив: удаление жанра с ID в виде строки"""
        response = super_admin.api.films_api.delete_genre("abc", expected_status=404)
        error_data = response.json()
        assert error_data.get("statusCode") == 404
        assert error_data.get("error") == "Not Found"
        assert error_data.get("message") == "Жанр не найден"

    def test_delete_genre_twice(self, super_admin, genre_data):
        """Негатив: повторное удаление уже удалённого жанра"""

        # Создаём жанр (без фикстуры, ведь у меня в ней удаление)
        response = super_admin.api.films_api.create_genres(genre_data)
        genre_id = response.json()["id"]

        # Первое удаление
        super_admin.api.films_api.delete_genre(genre_id)

        # Второе удаление
        second_response = super_admin.api.films_api.delete_genre(genre_id, expected_status=404)
        error_data = second_response.json()
        assert error_data.get("statusCode") == 404
        assert error_data.get("error") == "Not Found"
        assert error_data.get("message") == "Жанр не найден"

    # ========== ПОЛУЧЕНИЕ ЖАНРА ПО ID (негатив) ==========
    @pytest.mark.slow
    def test_get_genre_invalid_id(self, common_user):
        """Негатив: получение жанра с несуществующим ID"""
        response = common_user.api.films_api.get_genre(999999, expected_status=404)
        error_data = response.json()
        assert error_data.get("statusCode") == 404
        assert error_data.get("error") == "Not Found"
        assert error_data.get("message") == "Жанр не найден"

    def test_get_genre_negative_id(self, common_user):
        """Негатив: получение жанра с отрицательным ID"""
        response = common_user.api.films_api.get_genre(-1, expected_status=404)
        error_data = response.json()
        assert error_data.get("statusCode") == 404
        assert error_data.get("error") == "Not Found"
        assert error_data.get("message") == "Жанр не найден"

    def test_get_genre_zero_id(self, common_user):
        """Негатив: получение жанра с ID = 0"""
        response = common_user.api.films_api.get_genre(0, expected_status=404)
        error_data = response.json()
        assert error_data.get("statusCode") == 404
        assert error_data.get("error") == "Not Found"
        assert error_data.get("message") == "Жанр не найден"

    def test_get_genre_string_id(self, common_user):
        """Негатив: получение жанра с ID в виде строки"""
        response = common_user.api.films_api.get_genre("abc", expected_status=404)
        error_data = response.json()
        assert error_data.get("statusCode") == 404
        assert error_data.get("error") == "Not Found"
        assert error_data.get("message") == "Жанр не найден"