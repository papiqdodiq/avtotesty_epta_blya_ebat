import allure
import pytest
from faker import Faker

faker = Faker('ru_RU')

@allure.epic("Управление жанрами фильмов")
@allure.feature("Позитивные сценарии работы с жанрами")
class TestPositiveMoviesGenres:

    @allure.story("Получение списка жанров")
    @allure.title("Получение списка жанров без токена (PUBLIC ручка)")
    @allure.description("""
        Проверяем, что публичный эндпоинт /genres доступен без авторизации.
        Ожидаем: статус 200, список жанров не пуст, каждый жанр имеет id и name.
        """)
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.slow
    @pytest.mark.regression
    @pytest.mark.smoke
    @pytest.mark.api
    def test_get_genres_without_token(self, common_user):
        """Позитив: получение списка жанров без токена (PUBLIC ручка)."""
        with allure.step("Отправляем GET запрос на /genres"):
            get_genres = common_user.api.films_api.get_genres()

        with allure.step("Проверяем, что ответ — список и не пустой"):
            genres = get_genres.json()
            assert isinstance(genres, list), "Ответ должен быть списком"
            assert len(genres) > 0, "Список жанров пуст"

        with allure.step("Проверяем структуру первого жанра"):
            genre = genres[0]
            required_fields = ["id", "name"]
            for field in required_fields:
                assert field in genre, f"У жанра отсутствует поле {field}"

        with allure.step("Проверяем типы полей"):
            assert isinstance(genre, dict), f"Жанр должен быть словарём, получено {type(genre)}"
            assert isinstance(genre["id"], int), "id должен быть числом"
            assert isinstance(genre["name"], str), "name должен быть строкой"
            assert genre["name"] is not None, "name не может быть пустым"
            assert genre["id"] > 0, "id должен быть больше 0"

    @allure.story("Получение списка жанров")
    @allure.title("Получение списка жанров с токеном")
    @allure.description("""
    Проверяем, что авторизованный пользователь может получить список жанров.
    Ожидаем: статус 200, список жанров не пуст, каждый жанр имеет id и name.
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.smoke
    @pytest.mark.api
    def test_get_genres_with_token(self, super_admin):
        """Позитив: получение списка жанров с токеном."""
        with allure.step("Отправляем GET запрос на /genres с токеном"):
            get_genres = super_admin.api.films_api.get_genres()

        with allure.step("Проверяем, что ответ — список и не пустой"):
            genres = get_genres.json()
            assert isinstance(genres, list), "Ответ должен быть списком"
            assert len(genres) > 0, "Список жанров пуст"

        with allure.step("Проверяем структуру первого жанра"):
            genre = genres[0]
            required_fields = ["id", "name"]
            for field in required_fields:
                assert field in genre, f"У жанра отсутствует поле {field}"

        with allure.step("Проверяем типы полей"):
            assert isinstance(genre, dict), f"Жанр должен быть словарём, получено {type(genre)}"
            assert isinstance(genre["id"], int), "id должен быть числом"
            assert isinstance(genre["name"], str), "name должен быть строкой"
            assert genre["name"] is not None, "name не может быть пустым"
            assert genre["id"] > 0, "id должен быть больше 0"

    @allure.story("Создание жанра")
    @allure.title("Успешное создание жанра")
    @allure.description("""
    Проверяем создание жанра через API.
    Шаги:
    1. Создаём жанр (фикстура create_genre)
    2. Получаем жанр по ID
    3. Проверяем совпадение данных
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.slow
    @pytest.mark.regression
    @pytest.mark.smoke
    @pytest.mark.api
    def test_create_genre(self, super_admin, create_genre, genre_data):
        """Позитив: создание жанра."""
        with allure.step("Создаём жанр через фикстуру"):
            genre_id = create_genre

        with allure.step("Получаем жанр по ID и проверяем данные"):
            get_genre = super_admin.api.films_api.get_genre(genre_id)
            get_data = get_genre.json()
            assert get_data["id"] == genre_id, "id не совпадает"
            assert get_data["name"] == genre_data["name"], "name не совпадает"

    @allure.story("Удаление жанра")
    @allure.title("Успешное удаление жанра")
    @allure.description("""
    Проверяем удаление жанра через API.
    Шаги:
    1. Создаём жанр
    2. Удаляем жанр
    3. Проверяем, что жанр больше не существует (404)
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.smoke
    @pytest.mark.api
    def test_delete_genre(self, super_admin, genre_data):
        """Позитив: удаление жанра."""
        with allure.step("Создаём жанр"):
            create_genre = super_admin.api.films_api.create_genres(genre_data)
            genre_id = create_genre.json()["id"]

        with allure.step("Удаляем жанр и проверяем структуру ответа"):
            delete_genre = super_admin.api.films_api.delete_genre(genre_id)
            data = delete_genre.json()
            required_fields = ["id", "name"]
            for field in required_fields:
                assert field in data, f"У ответа отсутствует поле {field}"
            assert isinstance(data["id"], int), "id должен быть числом"
            assert isinstance(data["name"], str), "name должен быть строкой"
            assert data["id"] == genre_id, "id не совпадает"
            assert data["name"] == genre_data["name"], "name не совпадает"

        with allure.step("Проверяем, что жанр действительно удалился"):
            super_admin.api.films_api.get_genre(genre_id, expected_status=404)

    @allure.story("Получение жанра по ID")
    @allure.title("Получение жанра по ID без токена (PUBLIC ручка)")
    @allure.description("""
        Проверяем, что публичный эндпоинт /genres/{id} доступен без авторизации.
        Ожидаем: статус 200, структура ответа содержит id и name.
        """)
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.smoke
    @pytest.mark.api
    def test_get_genre_without_token(self, super_admin, create_genre, genre_data):
        """Позитив: получение жанра по ID без токена."""
        with allure.step("Создаём жанр через фикстуру"):
            genre_id = create_genre

        with allure.step("Получаем жанр по ID без токена и проверяем данные"):
            get_genre = super_admin.api.films_api.get_genre(genre_id)
            data = get_genre.json()
            required_fields = ["id", "name"]
            for field in required_fields:
                assert field in data, f"У ответа отсутствует поле {field}"
            assert isinstance(data["id"], int), "id должен быть числом"
            assert isinstance(data["name"], str), "name должен быть строкой"
            assert data["id"] == genre_id, "id не совпадает"
            assert data["name"] == genre_data["name"], "name не совпадает"

    @allure.story("Получение жанра по ID")
    @allure.title("Получение жанра по ID с токеном")
    @allure.description("""
        Проверяем, что авторизованный пользователь может получить жанр по ID.
        Ожидаем: статус 200, структура ответа содержит id и name.
        """)
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.smoke
    @pytest.mark.api
    def test_get_genre_with_token(self, super_admin, create_genre, genre_data):
        """Позитив: получение жанра по ID с токеном."""
        with allure.step("Создаём жанр через фикстуру"):
            genre_id = create_genre

        with allure.step("Получаем жанр по ID с токеном и проверяем данные"):
            get_genre = super_admin.api.films_api.get_genre(genre_id)
            data = get_genre.json()
            required_fields = ["id", "name"]
            for field in required_fields:
                assert field in data, f"У ответа отсутствует поле {field}"
            assert isinstance(data["id"], int), "id должен быть числом"
            assert isinstance(data["name"], str), "name должен быть строкой"
            assert data["id"] == genre_id, "id не совпадает"
            assert data["name"] == genre_data["name"], "name не совпадает"


@allure.epic("Управление жанрами фильмов")
@allure.feature("Негативные сценарии работы с жанрами")
class TestNegativeMoviesGenres:

    # ========== СОЗДАНИЕ ЖАНРА (негатив) ==========
    @allure.story("Создание жанра")
    @allure.title("Создание жанра без авторизации")
    @allure.description("Проверяем, что без токена нельзя создать жанр. Ожидаем 401.")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_create_genre_without_token(self, api_manager, genre_data):
        """Негатив: создание жанра без авторизации"""
        with allure.step("Пытаемся создать жанр без токена"):
            response = api_manager.films_api.create_genres(genre_data, expected_status=401)
            error_data = response.json()
            assert error_data.get("statusCode") == 401
            assert error_data.get("message") == "Unauthorized"

        with allure.step("Проверяем, что жанр не создался"):
            get_genres = api_manager.films_api.get_genres()
            genres = get_genres.json()
            names = [genre["name"] for genre in genres]
            assert genre_data["name"] not in names, "Жанр создался без авторизации"

    @allure.story("Создание жанра")
    @allure.title("Создание жанра без нужных прав")
    @allure.description("Проверяем, что обычный пользователь (common_user) не может создать жанр. Ожидаем 403.")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_create_genre_without_rights(self, common_user, genre_data):
        """Негатив: создание жанра без нужных прав"""
        with allure.step("Пытаемся создать жанр от имени common_user"):
            response = common_user.api.films_api.create_genres(genre_data, expected_status=403)
            error_data = response.json()
            assert error_data.get("statusCode") == 403
            assert error_data.get("message") == "Forbidden resource"
            assert error_data.get("error") == "Forbidden"

        with allure.step("Проверяем, что жанр не создался"):
            get_genres = common_user.api.films_api.get_genres()
            genres = get_genres.json()
            names = [genre["name"] for genre in genres]
            assert genre_data["name"] not in names, "Жанр создался без прав"

    @allure.story("Создание жанра")
    @allure.title("Создание жанра с неверным токеном")
    @allure.description("Проверяем, что с невалидным токеном нельзя создать жанр. Ожидаем 401.")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_create_genre_with_invalid_token(self, api_manager, genre_data):
        """Негатив: создание жанра с неверным токеном"""
        with allure.step("Устанавливаем неверный токен"):
            api_manager.set_token("invalid_token")

        with allure.step("Пытаемся создать жанр"):
            response = api_manager.films_api.create_genres(genre_data, expected_status=401)
            error_data = response.json()
            assert error_data.get("statusCode") == 401
            assert error_data.get("message") == "Unauthorized"

        with allure.step("Чистим токен и проверяем, что жанр не создался"):
            api_manager.clear_token()
            get_genres = api_manager.films_api.get_genres()
            genres = get_genres.json()
            names = [genre["name"] for genre in genres]
            assert genre_data["name"] not in names, "Жанр создался с неверным токеном"

    @allure.story("Создание жанра")
    @allure.title("Создание жанра с пустым именем")
    @allure.description("Проверяем, что нельзя создать жанр с пустым именем. Ожидаем 400.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.skip(reason="БАГ: сервер возвращает 201 вместо 400")
    @pytest.mark.regression
    @pytest.mark.api
    def test_create_genre_empty_name(self, super_admin):
        """Негатив: создание жанра с пустым именем"""
        with allure.step("Пытаемся создать жанр с пустым именем"):
            response = super_admin.api.films_api.create_genres({"name": ""}, expected_status=400)
            error_data = response.json()
            assert error_data.get("statusCode") == 400
            assert error_data.get("error") == "Bad Request"
            messages = error_data.get("message")
            if isinstance(messages, list):
                assert "Поле name должно быть строкой" in messages
            else:
                assert messages == "Поле name должно быть строкой"

        with allure.step("Проверяем, что жанр с пустым именем не создался"):
            get_genres = super_admin.api.films_api.get_genres()
            genres = get_genres.json()
            empty_names = [genre["name"] for genre in genres if genre["name"] == ""]
            assert len(empty_names) == 0, "Жанр с пустым именем создался"

    @allure.story("Создание жанра")
    @allure.title("Создание дублирующего жанра")
    @allure.description("Проверяем, что нельзя создать жанр с уже существующим именем. Ожидаем 409.")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_create_genre_duplicate(self, super_admin, create_genre, genre_data):
        """Негатив: создание жанра с уже существующим именем"""
        with allure.step("Пытаемся создать жанр с уже существующим именем"):
            response = super_admin.api.films_api.create_genres(genre_data, expected_status=409)
            error_data = response.json()
            assert error_data.get("statusCode") == 409
            assert error_data.get("error") == "Conflict"
            assert error_data.get("message") == "Такой жанр уже существует"

        with allure.step("Проверяем, что жанр не создался повторно"):
            get_genres = super_admin.api.films_api.get_genres()
            genres = get_genres.json()
            count = sum(1 for genre in genres if genre["name"] == genre_data["name"])
            assert count == 1, f"Жанр '{genre_data['name']}' создался повторно, ожидался 1, получено {count}"

    @allure.story("Создание жанра")
    @allure.title("Создание жанра с пустым телом запроса")
    @allure.description("Проверяем, что при пустом теле запроса возвращается 400.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_create_genre_empty_body(self, super_admin):
        """Негатив: создание жанра с пустым телом запроса"""
        with allure.step("Пытаемся создать жанр с пустым телом"):
            response = super_admin.api.films_api.create_genres({}, expected_status=400)
            error_data = response.json()
            assert error_data.get("statusCode") == 400
            assert error_data.get("error") == "Bad Request"
            messages = error_data.get("message")
            if isinstance(messages, list):
                assert "Поле name должно быть строкой" in messages
            else:
                assert messages == "Поле name должно быть строкой"

        with allure.step("Проверяем, что жанр не создался"):
            get_genres = super_admin.api.films_api.get_genres()
            genres = get_genres.json()
            invalid_genres = [g for g in genres if g.get("name") is None]
            assert len(invalid_genres) == 0, "Создался жанр с пустым телом"

    @allure.story("Создание жанра")
    @allure.title("Создание жанра без поля name")
    @allure.description("Проверяем, что при отсутствии поля name возвращается 400.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.skip(reason="БАГ: запрос на создание не выполняется, но жанр с пустым именем существует в БД")
    @pytest.mark.regression
    @pytest.mark.api
    def test_create_genre_missing_name(self, super_admin):
        """Негатив: создание жанра без поля name"""
        with allure.step("Пытаемся создать жанр без поля name"):
            response = super_admin.api.films_api.create_genres({"wrong_field": "value"}, expected_status=400)
            error_data = response.json()
            assert error_data.get("statusCode") == 400
            assert error_data.get("error") == "Bad Request"
            messages = error_data.get("message")
            if isinstance(messages, list):
                assert "Поле name должно быть строкой" in messages
            else:
                assert messages == "Поле name должно быть строкой"

        with allure.step("Проверяем, что жанр не создался"):
            get_genres = super_admin.api.films_api.get_genres()
            genres = get_genres.json()
            empty_or_none = [g for g in genres if g.get("name") is None or g.get("name") == ""]
            assert len(empty_or_none) == 0, "Создался жанр без поля name"

    @allure.story("Создание жанра")
    @allure.title("Создание жанра с лишним полем")
    @allure.description("Проверяем, как сервер реагирует на лишние поля в запросе.")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.skip(reason="БАГ: сервер возвращает 200 вместо 400")
    @pytest.mark.regression
    @pytest.mark.api
    def test_create_genre_extra_field(self, super_admin):
        """Негатив/Позитив: создание жанра с лишним полем."""
        genre_name = faker.sentence(nb_words=2) + "1"

        with allure.step("Пытаемся создать жанр с лишним полем"):
            super_admin.api.films_api.create_genres({
                "name": genre_name,
                "wrong_field": "value"
            }, expected_status=400)

    # ========== УДАЛЕНИЕ ЖАНРА (негатив) ==========
    @allure.story("Удаление жанра")
    @allure.title("Удаление жанра без авторизации")
    @allure.description("Проверяем, что без токена нельзя удалить жанр. Ожидаем 401.")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_delete_genre_without_token(self, api_manager, create_genre):
        """Негатив: удаление жанра без авторизации"""
        genre_id = create_genre

        with allure.step("Пытаемся удалить жанр без токена"):
            response = api_manager.films_api.delete_genre(genre_id, expected_status=401)
            error_data = response.json()
            assert error_data.get("statusCode") == 401
            assert error_data.get("message") == "Unauthorized"

        with allure.step("Проверяем, что жанр не удалился"):
            get_genre = api_manager.films_api.get_genre(genre_id)
            assert get_genre.status_code == 200, "Жанр удалился без авторизации"

    @allure.story("Удаление жанра")
    @allure.title("Удаление жанра без нужных прав")
    @allure.description("Проверяем, что обычный пользователь (common_user) не может удалить жанр. Ожидаем 403.")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_delete_genre_without_rights(self, common_user, create_genre):
        """Негатив: удаление жанра без нужных прав"""
        genre_id = create_genre

        with allure.step("Пытаемся удалить жанр от имени common_user"):
            response = common_user.api.films_api.delete_genre(genre_id, expected_status=403)
            error_data = response.json()
            assert error_data.get("statusCode") == 403
            assert error_data.get("message") == "Forbidden resource"
            assert error_data.get("error") == "Forbidden"

        with allure.step("Проверяем, что жанр не удалился"):
            get_genre = common_user.api.films_api.get_genre(genre_id)
            assert get_genre.status_code == 200, "Жанр удалился без прав"

    @allure.story("Удаление жанра")
    @allure.title("Удаление жанра с неверным токеном")
    @allure.description("Проверяем, что с невалидным токеном нельзя удалить жанр. Ожидаем 401.")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_delete_genre_with_invalid_token(self, api_manager, create_genre):
        """Негатив: удаление жанра с неверным токеном"""
        genre_id = create_genre

        with allure.step("Устанавливаем неверный токен и пытаемся удалить жанр"):
            api_manager.set_token("invalid_token")
            response = api_manager.films_api.delete_genre(genre_id, expected_status=401)
            error_data = response.json()
            assert error_data.get("statusCode") == 401
            assert error_data.get("message") == "Unauthorized"

        with allure.step("Чистим токен и проверяем, что жанр не удалился"):
            api_manager.clear_token()
            get_genre = api_manager.films_api.get_genre(genre_id)
            assert get_genre.status_code == 200, "Жанр удалился с неверным токеном"

    @allure.story("Удаление жанра")
    @allure.title("Удаление жанра с несуществующим ID")
    @allure.description("Проверяем, что при удалении с несуществующим ID возвращается 404.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_delete_genre_invalid_id(self, super_admin):
        """Негатив: удаление жанра с несуществующим ID"""
        with allure.step("Пытаемся удалить жанр с ID 999999"):
            response = super_admin.api.films_api.delete_genre(999999, expected_status=404)
            error_data = response.json()
            assert error_data.get("statusCode") == 404
            assert error_data.get("error") == "Not Found"
            assert error_data.get("message") == "Жанр не найден"

    @allure.story("Удаление жанра")
    @allure.title("Удаление жанра с отрицательным ID")
    @allure.description("Проверяем, что при удалении с отрицательным ID возвращается 404.")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    @pytest.mark.api
    def test_delete_genre_negative_id(self, super_admin):
        """Негатив: удаление жанра с отрицательным ID"""
        with allure.step("Пытаемся удалить жанр с ID -1"):
            response = super_admin.api.films_api.delete_genre(-1, expected_status=404)
            error_data = response.json()
            assert error_data.get("statusCode") == 404
            assert error_data.get("error") == "Not Found"
            assert error_data.get("message") == "Жанр не найден"

    @allure.story("Удаление жанра")
    @allure.title("Удаление жанра с ID = 0")
    @allure.description("Проверяем, что при удалении с ID 0 возвращается 404.")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    @pytest.mark.api
    def test_delete_genre_zero_id(self, super_admin):
        """Негатив: удаление жанра с ID = 0"""
        with allure.step("Пытаемся удалить жанр с ID 0"):
            response = super_admin.api.films_api.delete_genre(0, expected_status=404)
            error_data = response.json()
            assert error_data.get("statusCode") == 404
            assert error_data.get("error") == "Not Found"
            assert error_data.get("message") == "Жанр не найден"

    @allure.story("Удаление жанра")
    @allure.title("Удаление жанра с ID в виде строки")
    @allure.description("Проверяем, что при удалении с строковым ID возвращается 404.")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    @pytest.mark.api
    def test_delete_genre_string_id(self, super_admin):
        """Негатив: удаление жанра с ID в виде строки"""
        with allure.step("Пытаемся удалить жанр с ID 'abc'"):
            response = super_admin.api.films_api.delete_genre("abc", expected_status=404)
            error_data = response.json()
            assert error_data.get("statusCode") == 404
            assert error_data.get("error") == "Not Found"
            assert error_data.get("message") == "Жанр не найден"

    @allure.story("Удаление жанра")
    @allure.title("Повторное удаление уже удалённого жанра")
    @allure.description("Проверяем, что при повторном удалении возвращается 404.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_delete_genre_twice(self, super_admin, genre_data):
        """Негатив: повторное удаление уже удалённого жанра"""
        with allure.step("Создаём жанр"):
            response = super_admin.api.films_api.create_genres(genre_data)
            genre_id = response.json()["id"]

        with allure.step("Удаляем жанр первый раз"):
            super_admin.api.films_api.delete_genre(genre_id)

        with allure.step("Пытаемся удалить жанр повторно"):
            second_response = super_admin.api.films_api.delete_genre(genre_id, expected_status=404)
            error_data = second_response.json()
            assert error_data.get("statusCode") == 404
            assert error_data.get("error") == "Not Found"
            assert error_data.get("message") == "Жанр не найден"

    # ========== ПОЛУЧЕНИЕ ЖАНРА ПО ID (негатив) ==========
    @allure.story("Получение жанра по ID")
    @allure.title("Получение жанра с несуществующим ID")
    @allure.description("Проверяем, что при GET запросе с несуществующим ID возвращается 404.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.slow
    @pytest.mark.regression
    @pytest.mark.api
    def test_get_genre_invalid_id(self, common_user):
        """Негатив: получение жанра с несуществующим ID"""
        with allure.step("Пытаемся получить жанр с ID 999999"):
            response = common_user.api.films_api.get_genre(999999, expected_status=404)
            error_data = response.json()
            assert error_data.get("statusCode") == 404
            assert error_data.get("error") == "Not Found"
            assert error_data.get("message") == "Жанр не найден"

    @allure.story("Получение жанра по ID")
    @allure.title("Получение жанра с отрицательным ID")
    @allure.description("Проверяем, что при GET запросе с отрицательным ID возвращается 404.")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    @pytest.mark.api
    def test_get_genre_negative_id(self, common_user):
        """Негатив: получение жанра с отрицательным ID"""
        with allure.step("Пытаемся получить жанр с ID -1"):
            response = common_user.api.films_api.get_genre(-1, expected_status=404)
            error_data = response.json()
            assert error_data.get("statusCode") == 404
            assert error_data.get("error") == "Not Found"
            assert error_data.get("message") == "Жанр не найден"

    @allure.story("Получение жанра по ID")
    @allure.title("Получение жанра с ID = 0")
    @allure.description("Проверяем, что при GET запросе с ID 0 возвращается 404.")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    @pytest.mark.api
    def test_get_genre_zero_id(self, common_user):
        """Негатив: получение жанра с ID = 0"""
        with allure.step("Пытаемся получить жанр с ID 0"):
            response = common_user.api.films_api.get_genre(0, expected_status=404)
            error_data = response.json()
            assert error_data.get("statusCode") == 404
            assert error_data.get("error") == "Not Found"
            assert error_data.get("message") == "Жанр не найден"

    @allure.story("Получение жанра по ID")
    @allure.title("Получение жанра с ID в виде строки")
    @allure.description("Проверяем, что при GET запросе с строковым ID возвращается 404.")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    @pytest.mark.api
    def test_get_genre_string_id(self, common_user):
        """Негатив: получение жанра с ID в виде строки"""
        with allure.step("Пытаемся получить жанр с ID 'abc'"):
            response = common_user.api.films_api.get_genre("abc", expected_status=404)
            error_data = response.json()
            assert error_data.get("statusCode") == 404
            assert error_data.get("error") == "Not Found"
            assert error_data.get("message") == "Жанр не найден"