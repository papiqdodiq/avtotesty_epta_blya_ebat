import pytest
from faker import Faker

from constants import login_data_list

faker = Faker('ru_RU')

class TestPositiveMovies:

    def test_get_billboard_without_token(self, api_manager, billboard_params):
        """Позитив: получение афиши без токена.
        Проверяем структуру ответа, типы данных и содержимое."""
        get_billboard = api_manager.films_api.get_billboard(billboard_params)
        assert get_billboard.headers.get("Content-Type") == "application/json; charset=utf-8", "Неверный Content-Type"

        # Проверка структуры ответа
        data = get_billboard.json()
        required_fields = ["movies", "count", "page", "pageSize", "pageCount"]
        for field in required_fields:
            assert field in data, f"Отсутствует поле {field}"

        # Проверка типов
        assert isinstance(data["movies"], list), "movies должен быть списком"
        assert isinstance(data["count"], int), "count должен быть числом"
        assert isinstance(data["page"], int), "page должен быть числом"
        assert isinstance(data["pageSize"], int), "pageSize должен быть числом"
        assert isinstance(data["pageCount"], int), "pageCount должен быть числом"

        # Проверка совпадения ответа с params в запросе
        assert data["page"] == billboard_params["page"], "Номер страницы отличается от номера в params запроса"
        assert data["pageSize"] == billboard_params["pageSize"], "Размер страницы отличается от номера в params запроса"

        # Если есть фильмы, проверяем структуру первого
        if data["movies"]:
            movie = data["movies"][0]
            movie_fields = ["id", "name", 'description', "price", 'rating', 'createdAt', 'genre',
                            'imageUrl', "location", "published", "genreId"]
            for field in movie_fields:
                assert field in movie, f"У фильма отсутствует поле {field}"

    def test_get_billboard(self, api_manager, billboard_params):
        """Позитив: получение афиши с токеном.
        Проверяем структуру ответа, типы данных и содержимое."""
        api_manager.authenticate(login_data_list)
        get_billboard = api_manager.films_api.get_billboard(billboard_params)
        api_manager.clear_token()
        assert get_billboard.headers.get("Content-Type") == "application/json; charset=utf-8", "Неверный Content-Type"

        # Проверка структуры ответа
        data = get_billboard.json()
        required_fields = ["movies", "count", "page", "pageSize", "pageCount"]
        for field in required_fields:
            assert field in data, f"Отсутствует поле {field}"

        # Проверка типов
        assert isinstance(data["movies"], list), "movies должен быть списком"
        assert isinstance(data["count"], int), "count должен быть числом"
        assert isinstance(data["page"], int), "page должен быть числом"
        assert isinstance(data["pageSize"], int), "pageSize должен быть числом"
        assert isinstance(data["pageCount"], int), "pageCount должен быть числом"

        # Проверка совпадения ответа с params в запросе
        assert data["page"] == billboard_params["page"], "Номер страницы отличается от номера в params запроса"
        assert data["pageSize"] == billboard_params["pageSize"], "Размер страницы отличается от номера в params запроса"

        # Если есть фильмы, проверяем структуру первого
        if data["movies"]:
            movie = data["movies"][0]
            movie_fields = ["id", "name", 'description', "price", 'rating', 'createdAt', 'genre',
                            'imageUrl', "location", "published", "genreId"]
            for field in movie_fields:
                assert field in movie, f"У фильма отсутствует поле {field}"

    def test_get_billboard_updated(self, api_manager, billboard_params):
        """Позитив: получение афиши с изменёнными параметрами.
        Убираем locations, меняем published на False, createdAt на desc."""
        new_billboard_params = billboard_params.copy()
        new_billboard_params.update({
            "published": False,
            "createdAt": "desc"
        })
        del new_billboard_params["locations"]

        api_manager.films_api.get_billboard(new_billboard_params)

    def test_create_movie(self, api_manager, film_data):
        """Позитив: создание фильма.
        Проверяем структуру ответа, типы данных и содержимое."""
        # 1. СОЗДАЁМ ФИЛЬМ
        api_manager.authenticate(login_data_list)
        create_movie = api_manager.films_api.create_movie(film_data)
        assert create_movie.headers.get("Content-Type") == "application/json; charset=utf-8"

        create_data = create_movie.json()
        movie_id = create_data["id"]

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

        # Проверяем совпадение с отправленными данными
        assert create_data["name"] == film_data["name"]
        assert create_data["price"] == film_data["price"]
        assert create_data["location"] == film_data["location"]
        assert create_data["published"] == film_data["published"]
        assert create_data["genreId"] == film_data["genreId"]

        # 2. ПРОВЕРЯЕМ, ЧТО ФИЛЬМ РЕАЛЬНО В БАЗЕ (GET)
        get_movie = api_manager.films_api.get_movie(movie_id)

        get_data = get_movie.json()

        # Проверяем совпадение данных с тем, что создали
        assert get_data["id"] == movie_id
        assert get_data["name"] == film_data["name"]
        assert get_data["price"] == film_data["price"]
        assert get_data["location"] == film_data["location"]
        assert get_data["published"] == film_data["published"]
        assert get_data["genreId"] == film_data["genreId"]
        assert get_data["description"] == film_data["description"]
        assert get_data["imageUrl"] == film_data["imageUrl"]

        # 3. ЧИСТИМ
        api_manager.films_api.delete_movie(movie_id)
        api_manager.clear_token()

    def test_create_movie_updated(self, api_manager, film_data):
        """Позитив: создание фильма с обновлёнными параметрами.
        Проверяем создание фильма с location=MSK, published=False, genreId=2."""
        new_film_data = film_data.copy()
        new_film_data.update({
            "name": faker.sentence(nb_words=4),
            "location": "MSK",
            "published": False,
            "genreId": 2
        })

        api_manager.authenticate(login_data_list)
        create_movie = api_manager.films_api.create_movie(new_film_data)
        assert create_movie.headers.get("Content-Type") == "application/json; charset=utf-8"

        movie_id = create_movie.json()["id"]

        # Проверяем через GET
        get_movie = api_manager.films_api.get_movie(movie_id)
        get_data = get_movie.json()

        assert get_data["name"] == new_film_data["name"]
        assert get_data["location"] == new_film_data["location"]
        assert get_data["published"] == new_film_data["published"]
        assert get_data["genreId"] == new_film_data["genreId"]

        api_manager.films_api.delete_movie(movie_id)
        api_manager.clear_token()

    def test_create_movie_unique_id(self, api_manager, film_data):
        """Позитив: при создании двух фильмов id разные"""
        api_manager.authenticate(login_data_list)
        movie1 = api_manager.films_api.create_movie(film_data)
        id1 = movie1.json()["id"]

        film_data2 = film_data.copy()
        film_data2["name"] = faker.sentence(nb_words=4)
        movie2 = api_manager.films_api.create_movie(film_data2)
        id2 = movie2.json()["id"]

        assert id1 != id2, "ID совпадают у разных фильмов"

        api_manager.films_api.delete_movie(id1)
        api_manager.films_api.delete_movie(id2)
        api_manager.clear_token()

    def test_get_movie_without_token(self, api_manager, create_film_id):
        """Позитив: получение фильма по ID без токена.
        Проверяем структуру ответа, типы данных и содержимое."""
        movie_id = create_film_id

        api_manager.clear_token()
        get_movie = api_manager.films_api.get_movie(movie_id)
        assert get_movie.headers.get("Content-Type") == "application/json; charset=utf-8", "Неверный Content-Type"

        # Проверка структуры (все обязательные поля есть)
        data = get_movie.json()
        required_fields = ["id", "name", "price", "description", "imageUrl",
                           "location", "published", "genreId", "genre", "createdAt", "reviews", "rating"]
        for field in required_fields:
            assert field in data, f"Отсутствует поле {field}"

        # Проверка типов данных
        assert isinstance(data["genre"], dict), "genre должен быть словарем"
        assert isinstance(data["reviews"], list), "movies должен быть списком"
        assert isinstance(data["id"], int), "id должен быть числом"
        assert isinstance(data["name"], str), "name должен быть строкой"
        assert isinstance(data["price"], int), "price должен быть числом"
        assert isinstance(data["published"], bool), "published должен быть булевым"
        assert isinstance(data["genreId"], int), "genreId должен быть числом"

        # Проверка содержимого
        assert data["id"] == movie_id, "ID не совпадает"
        assert data["name"] is not None, "name не может быть пустым"
        assert data["price"] > 0, "price должен быть больше 0"

        # Проверка вложенного объекта genre
        assert "name" in data["genre"], "У genre отсутствует поле name"
        assert isinstance(data["genre"]["name"], str), "genre.name должен быть строкой"

    def test_get_movie(self, api_manager, create_film_id):
        """Позитив: получение фильма по ID с токеном.
        Проверяем структуру ответа, типы данных и содержимое."""
        movie_id = create_film_id

        get_movie = api_manager.films_api.get_movie(movie_id)
        assert get_movie.headers.get("Content-Type") == "application/json; charset=utf-8", "Неверный Content-Type"

        # Проверка структуры (все обязательные поля есть)
        data = get_movie.json()
        required_fields = ["id", "name", "price", "description", "imageUrl",
                           "location", "published", "genreId", "genre", "createdAt", "reviews", "rating"]
        for field in required_fields:
            assert field in data, f"Отсутствует поле {field}"

        # Проверка типов данных
        assert isinstance(data["genre"], dict), "genre должен быть словарем"
        assert isinstance(data["reviews"], list), "movies должен быть списком"
        assert isinstance(data["id"], int), "id должен быть числом"
        assert isinstance(data["name"], str), "name должен быть строкой"
        assert isinstance(data["price"], int), "price должен быть числом"
        assert isinstance(data["published"], bool), "published должен быть булевым"
        assert isinstance(data["genreId"], int), "genreId должен быть числом"

        # Проверка содержимого
        assert data["id"] == movie_id, "ID не совпадает"
        assert data["name"] is not None, "name не может быть пустым"
        assert data["price"] > 0, "price должен быть больше 0"

        # Проверка вложенного объекта genre
        assert "name" in data["genre"], "У genre отсутствует поле name"
        assert isinstance(data["genre"]["name"], str), "genre.name должен быть строкой"

    def test_delete_movie(self, api_manager, film_data):
        """Позитив: удаление фильма по ID.
        Проверяем, что после удаления фильм больше недоступен (404)."""
        api_manager.authenticate(login_data_list)
        create_movie = api_manager.films_api.create_movie(film_data)
        movie_id = create_movie.json()["id"]

        delete_movie = api_manager.films_api.delete_movie(movie_id)
        assert delete_movie.headers.get("Content-Type") == "application/json; charset=utf-8", "Неверный Content-Type"

        # Проверка структуры ответа при удалении
        data = delete_movie.json()
        required_fields = ["id", "name", "price", "description", "imageUrl",
                           "location", "published", "genreId", "genre", "createdAt", "rating"]
        for field in required_fields:
            assert field in data, f"Отсутствует поле {field}"

        api_manager.films_api.get_movie(movie_id, 404)
        api_manager.clear_token()

    def test_patch_movie(self, api_manager, film_data):
        """Позитив: частичное обновление фильма (PATCH).
        Проверяем структуру ответа, типы данных и содержимое."""
        api_manager.authenticate(login_data_list)
        create_movie = api_manager.films_api.create_movie(film_data)
        movie_id = create_movie.json()["id"]

        film_data_patch = {
        "name": faker.sentence(nb_words=4),
        "location": "MSK",
        }

        patch_movie = api_manager.films_api.patch_movie(movie_id, film_data_patch)
        assert patch_movie.headers.get("Content-Type") == "application/json; charset=utf-8", "Неверный Content-Type"

        # Проверка структуры ответа после PATCH
        data = patch_movie.json()
        required_fields = ["id", "name", "price", "description", "imageUrl",
                           "location", "published", "genreId", "genre", "createdAt", "rating"]
        for field in required_fields:
            assert field in data, f"Отсутствует поле {field}"

        # Проверка типов
        assert isinstance(data["genre"], dict), "genre должен быть словарем"
        assert isinstance(data["id"], int), "id должен быть числом"
        assert isinstance(data["name"], str), "name должен быть строкой"
        assert isinstance(data["price"], int), "price должен быть числом"
        assert isinstance(data["published"], bool), "published должен быть булевым"
        assert isinstance(data["genreId"], int), "genreId должен быть числом"

        # Проверка содержимого
        assert data["id"] == movie_id, "ID не совпадает"
        assert data["name"] is not None, "name не может быть пустым"
        assert data["price"] > 0, "price должен быть больше 0"

        # Проверка совпадения ответа с film_data_patch в запросе
        get_movie = api_manager.films_api.get_movie(movie_id)
        assert get_movie.json().get("name") == film_data_patch["name"]
        assert get_movie.json().get("location") == film_data_patch["location"]
        assert get_movie.json().get("price") == film_data["price"]

        # Проверка вложенного объекта genre
        assert "name" in data["genre"], "У genre отсутствует поле name"
        assert isinstance(data["genre"]["name"], str), "genre.name должен быть строкой"

        api_manager.films_api.delete_movie(movie_id)
        api_manager.clear_token()


class TestNegativeMovies:

    # ========== GET /movies ==========
    def test_get_billboard_min_price_greater_than_max(self, api_manager, billboard_params):
        """Негатив: запрос с минимальной ценой выше максимальной цены"""
        negative_params = billboard_params.copy()
        negative_params["minPrice"] = 1000
        negative_params["maxPrice"] = 100
        get_billboard = api_manager.films_api.get_billboard(negative_params, expected_status=400)
        assert get_billboard.status_code == 400, "Афиша загрузилась c минимальной ценой выше максимальной цены"

    def test_get_billboard_page_out_of_range(self, api_manager, billboard_params):
        """Негатив: запрос с несуществующей страницей"""
        negative_params = billboard_params.copy()
        negative_params["page"] = 999999
        get_billboard = api_manager.films_api.get_billboard(negative_params, expected_status=[200, 400])
        assert get_billboard.status_code in [200, 400], "Афиша загрузилась c неожиданным результатом"

    def test_get_billboard_with_invalid_genre(self, api_manager, billboard_params):
        """Негатив: запрос с несуществующим жанром"""
        negative_params = billboard_params.copy()
        negative_params["genreId"] = 999
        get_billboard = api_manager.films_api.get_billboard(negative_params, expected_status=[200, 400])
        assert get_billboard.status_code in [200, 400], "Афиша загрузилась c неожиданным результатом"

    def test_get_billboard_negative_page(self, api_manager, billboard_params):
        """Негатив: отрицательная страница"""
        negative_params = billboard_params.copy()
        negative_params["page"] = -1
        get_billboard = api_manager.films_api.get_billboard(negative_params, expected_status=400)
        assert get_billboard.status_code == 400, "Афиша загрузилась при -1 странице"

    def test_get_billboard_negative_page_size(self, api_manager, billboard_params):
        """Негатив: отрицательный pageSize"""
        negative_params = billboard_params.copy()
        negative_params["pageSize"] = -10
        get_billboard = api_manager.films_api.get_billboard(negative_params, expected_status=400)
        assert get_billboard.status_code == 400, "Афиша загрузилась при -10 размере страницы"

    def test_get_billboard_invalid_location(self, api_manager, billboard_params):
        """Негатив: несуществующая локация"""
        negative_params = billboard_params.copy()
        negative_params["locations"] = "MOON"
        get_billboard = api_manager.films_api.get_billboard(negative_params, expected_status=400)
        assert get_billboard.status_code == 400, "Афиша загрузилась с несуществующей локацией"

    # ========== POST /movies ==========
    def test_create_movie_without_token(self, api_manager, film_data):
        """Негатив: создание фильма без авторизации"""
        create_movie = api_manager.films_api.create_movie(film_data, expected_status=401)
        assert create_movie.status_code == 401, "Фильм создался без авторизации"

    def test_create_movie_with_invalid_token(self, api_manager, film_data):
        """Негатив: создание фильма с неверным токеном"""
        api_manager.set_token("invalid_token")
        create_movie = api_manager.films_api.create_movie(film_data, expected_status=401)
        assert create_movie.status_code == 401, "Фильм создался с неверным токеном авторизации"
        api_manager.clear_token()

    def test_create_movie_empty_name(self, api_manager, film_data):
        """Негатив: создание фильма с пустым именем"""
        api_manager.authenticate(login_data_list)
        new_film_data = film_data.copy()
        new_film_data["name"] = ""
        create_movie = api_manager.films_api.create_movie(new_film_data, expected_status=400)
        assert create_movie.status_code == 400, "Фильм создался с пустым именем"
        api_manager.clear_token()

    def test_create_movie_same_name(self, api_manager, film_data):
        """Негатив: создание фильма с таким же именем"""
        api_manager.authenticate(login_data_list)
        create_movie = api_manager.films_api.create_movie(film_data)
        assert create_movie.status_code == 201, "Ошибка при создании фильма"
        movie_id = create_movie.json()["id"]
        movie_name = create_movie.json()["name"]

        new_film_data = film_data.copy()
        new_film_data["name"] = movie_name
        create_movie = api_manager.films_api.create_movie(new_film_data, expected_status=409)
        assert create_movie.status_code == 409, "Фильм создался с уже существующим именем"

        api_manager.films_api.delete_movie(movie_id)
        api_manager.clear_token()

    def test_create_movie_without_required_field(self, api_manager, film_data):
        """Негатив: создание фильма без обязательного поля"""
        api_manager.authenticate(login_data_list)
        data = film_data.copy()
        del data["name"]
        response = api_manager.films_api.create_movie(data, expected_status=400)
        assert response.status_code == 400, "Фильм создался без обязательного поля"
        api_manager.clear_token()

    def test_create_movie_empty_body(self, api_manager):
        """Негатив: создание фильма с пустым телом запроса"""
        api_manager.authenticate(login_data_list)
        response = api_manager.films_api.create_movie({}, expected_status=400)
        assert response.status_code == 400, "Фильм создался с пустым телом"
        api_manager.clear_token()

    def test_create_movie_invalid_price_type(self, api_manager, film_data):
        """Негатив: создание фильма с ценой в виде строки (неверный тип)"""
        api_manager.authenticate(login_data_list)
        data = film_data.copy()
        data["price"] = "сто рублей"
        response = api_manager.films_api.create_movie(data, expected_status=400)
        assert response.status_code == 400, "Фильм создался с ценой-строкой"
        api_manager.clear_token()

    def test_create_movie_extra_field(self, api_manager, film_data):
        """Негатив: создание фильма с лишним полем"""
        api_manager.authenticate(login_data_list)
        data = film_data.copy()
        data["extraField"] = "что-то лишнее"
        response = api_manager.films_api.create_movie(data, expected_status=[201, 400])
        assert response.status_code in [201, 400], "Неожиданный статус при лишнем поле"
        if response.status_code == 201:
            movie_id = response.json().get("id")
            api_manager.films_api.delete_movie(movie_id)
        api_manager.clear_token()

    def test_create_movie_invalid_genre_id(self, api_manager, film_data):
        """Негатив: создание фильма с несуществующим genreId"""
        api_manager.authenticate(login_data_list)
        data = film_data.copy()
        data["genreId"] = 999999
        response = api_manager.films_api.create_movie(data, expected_status=400)
        assert response.status_code == 400, "Фильм создался с несуществующим жанром"
        api_manager.clear_token()

    @pytest.mark.skip(reason="БАГ: сервер возвращает 201 вместо 400")
    def test_create_movie_negative_price(self, api_manager, film_data):
        """Негатив: создание фильма с отрицательной ценой"""
        api_manager.authenticate(login_data_list)
        data = film_data.copy()
        data["price"] = -100
        response = api_manager.films_api.create_movie(data, expected_status=400)
        assert response.status_code == 400, "Фильм создался с отрицательной ценой"
        api_manager.clear_token()

    def test_create_movie_invalid_location(self, api_manager, film_data):
        """Негатив: создание фильма с несуществующей локацией"""
        api_manager.authenticate(login_data_list)
        data = film_data.copy()
        data["location"] = "MOON"
        response = api_manager.films_api.create_movie(data, expected_status=400)
        assert response.status_code == 400, "Фильм создался с несуществующей локацией"
        api_manager.clear_token()

    # ========== GET /movies/{id} ==========
    def test_get_movie_invalid_id(self, api_manager):
        """Негатив: получение фильма с несуществующим ID"""
        response = api_manager.films_api.get_movie(999999, expected_status=404)
        assert response.status_code == 404, "Нашёлся фильм с несуществующим ID"

    def test_get_movie_negative_id(self, api_manager):
        """Негатив: получение фильма с отрицательным ID"""
        response = api_manager.films_api.get_movie(-1, expected_status=404)
        assert response.status_code == 404, "Отрицательный ID обработался неверно"

    def test_get_movie_zero_id(self, api_manager):
        """Негатив: получение фильма с ID = 0"""
        response = api_manager.films_api.get_movie(0, expected_status=404)
        assert response.status_code == 404, "ID = 0 обработался неверно"

    @pytest.mark.skip(reason="БАГ: сервер возвращает 500 вместо 404")
    def test_get_movie_string_id(self, api_manager):
        """Негатив: получение фильма с ID в виде строки"""
        response = api_manager.films_api.get_movie("abc", expected_status=404)
        assert response.status_code == 404, "Строковый ID не вызвал ошибку"

    # ========== DELETE /movies/{id} ==========
    def test_delete_movie_without_token(self, api_manager, create_film_id):
        """Негатив: удаление фильма без авторизации"""
        movie_id = create_film_id
        api_manager.clear_token()
        response = api_manager.films_api.delete_movie(movie_id, expected_status=401)
        assert response.status_code == 401, "Фильм удалился без авторизации"
        api_manager.clear_token()

    def test_delete_movie_with_invalid_token(self, api_manager, create_film_id):
        """Негатив: удаление фильма с неверным токеном"""
        movie_id = create_film_id
        api_manager.set_token("invalid_token")
        response = api_manager.films_api.delete_movie(movie_id, expected_status=401)
        assert response.status_code == 401, "Фильм удалился с неверным токеном"
        api_manager.clear_token()

    def test_delete_movie_invalid_id(self, api_manager):
        """Негатив: удаление несуществующего фильма"""
        api_manager.authenticate(login_data_list)
        response = api_manager.films_api.delete_movie(999999, expected_status=[400, 404])
        assert response.status_code in [400, 404], "Удалился несуществующий фильм"
        api_manager.clear_token()

    def test_delete_movie_negative_id(self, api_manager):
        """Негатив: удаление фильма с отрицательным ID"""
        api_manager.authenticate(login_data_list)
        response = api_manager.films_api.delete_movie(-1, expected_status=[400, 404])
        assert response.status_code in [400, 404], "Отрицательный ID обработался неверно"
        api_manager.clear_token()

    def test_delete_movie_zero_id(self, api_manager):
        """Негатив: удаление фильма с ID = 0"""
        api_manager.authenticate(login_data_list)
        response = api_manager.films_api.delete_movie(0, expected_status=[400, 404])
        assert response.status_code in [400, 404], "ID = 0 обработался неверно"
        api_manager.clear_token()

    def test_delete_movie_string_id(self, api_manager):
        """Негатив: удаление фильма с ID в виде строки"""
        api_manager.authenticate(login_data_list)
        response = api_manager.films_api.delete_movie("abc", expected_status=[400, 404])
        assert response.status_code in [400, 404], "Строковый ID не вызвал ошибку"
        api_manager.clear_token()

    # ========== PATCH /movies/{id} ==========
    def test_patch_movie_without_token(self, api_manager, create_film_id):
        """Негатив: редактирование фильма без токена"""
        movie_id = create_film_id
        api_manager.clear_token()
        response = api_manager.films_api.patch_movie(movie_id, {"name": "new"}, expected_status=401)
        assert response.status_code == 401, "Фильм отредактировался без токена"
        api_manager.clear_token()

    def test_patch_movie_with_invalid_token(self, api_manager, create_film_id):
        """Негатив: редактирование фильма с неверным токеном"""
        movie_id = create_film_id
        api_manager.set_token("invalid_token")
        response = api_manager.films_api.patch_movie(movie_id, {"name": "new"}, expected_status=401)
        assert response.status_code == 401, "Фильм отредактировался с неверным токеном"
        api_manager.clear_token()

    def test_patch_movie_invalid_id(self, api_manager):
        """Негатив: редактирование несуществующего фильма"""
        api_manager.authenticate(login_data_list)
        response = api_manager.films_api.patch_movie(999999, {"name": "new"}, expected_status=404)
        assert response.status_code == 404, "Отредактировался несуществующий фильм"
        api_manager.clear_token()

    def test_patch_movie_negative_price(self, api_manager, create_film_id):
        """Негатив: редактирование с отрицательной ценой"""
        movie_id = create_film_id
        response = api_manager.films_api.patch_movie(movie_id, {"price": -100}, expected_status=400)
        assert response.status_code == 400, "Фильм обновился с отрицательной ценой"
        api_manager.clear_token()

    @pytest.mark.skip(reason="БАГ: сервер возвращает 404 вместо 409")
    def test_patch_movie_duplicate_name(self, api_manager, film_data):
        """Негатив: редактирование имени на уже существующее название фильма"""
        api_manager.authenticate(login_data_list)

        # Создаём первый фильм
        response1 = api_manager.films_api.create_movie(film_data)
        movie1_id = response1.json()["id"]
        existing_name = response1.json()["name"]

        # Создаём второй фильм с уникальным названием
        film_data2 = film_data.copy()
        film_data2["name"] = faker.sentence(nb_words=4)
        response2 = api_manager.films_api.create_movie(film_data2)
        movie2_id = response2.json()["id"]

        # Пытаемся обновить ВТОРОЙ фильм, меняя его имя на имя ПЕРВОГО
        response3 = api_manager.films_api.patch_movie(movie2_id, {"name": existing_name}, expected_status=409)
        assert response3.status_code == 409, "Фильм обновился с уже существующим именем"

        # Чистим
        api_manager.films_api.delete_movie(movie1_id)
        api_manager.films_api.delete_movie(movie2_id)
        api_manager.clear_token()

    @pytest.mark.skip(reason="БАГ: сервер возвращает 404 вместо 400")
    def test_patch_movie_empty_name(self, api_manager, create_film_id):
        """Негатив: редактирование с пустым названием"""
        movie_id = create_film_id
        response = api_manager.films_api.patch_movie(movie_id, {"name": ""}, expected_status=400)
        assert response.status_code == 400, "Фильм обновился с пустым названием"
        api_manager.clear_token()

    @pytest.mark.skip(reason="БАГ: сервер возвращает 404 вместо 400")
    def test_patch_movie_invalid_genre(self, api_manager, create_film_id):
        """Негатив: редактирование с несуществующим жанром"""
        movie_id = create_film_id
        response = api_manager.films_api.patch_movie(movie_id, {"genreId": 999}, expected_status=400)
        assert response.status_code == 400, "Фильм обновился с несуществующим жанром"
        api_manager.clear_token()

    def test_patch_movie_invalid_location(self, api_manager, create_film_id):
        """Негатив: редактирование с несуществующей локацией"""
        movie_id = create_film_id
        response = api_manager.films_api.patch_movie(movie_id, {"location": "MOON"}, expected_status=400)
        assert response.status_code == 400, "Фильм обновился с несуществующей локацией"
        api_manager.clear_token()

    def test_patch_movie_string_id(self, api_manager):
        """Негатив: редактирование с ID в виде строки"""
        api_manager.authenticate(login_data_list)
        response = api_manager.films_api.patch_movie("abc", {"name": "new"}, expected_status=404)
        assert response.status_code == 404, "Строковый ID не вызвал ошибку"
        api_manager.clear_token()

    def test_patch_movie_invalid_price_type(self, api_manager, create_film_id):
        """Негатив: PATCH с ценой в виде строки"""
        movie_id = create_film_id
        response = api_manager.films_api.patch_movie(movie_id, {"price": "сто рублей"}, expected_status=400)
        assert response.status_code == 400, "Цена-строка не вызвала ошибку"
        api_manager.clear_token()

    def test_patch_movie_empty_body(self, api_manager, create_film_id):
        """Негатив/Позитив: PATCH с пустым телом (должен вернуть 200 или 400)"""
        movie_id = create_film_id

        # Получаем текущие данные до PATCH
        get_before = api_manager.films_api.get_movie(movie_id)
        original_name = get_before.json().get("name")
        original_price = get_before.json().get("price")

        # Отправляем PATCH с пустым телом
        response = api_manager.films_api.patch_movie(movie_id, {}, expected_status=[200, 400])

        # Допустимо: 200 (ничего не изменилось) или 400 (ругается)
        assert response.status_code in [200, 400], f"Неожиданный статус: {response.status_code}"

        if response.status_code == 200:
            # Проверяем, что данные НЕ изменились
            get_after = api_manager.films_api.get_movie(movie_id)
            assert get_after.json().get("name") == original_name, "Имя изменилось без причины"
            assert get_after.json().get("price") == original_price, "Цена изменилась без причины"
        api_manager.clear_token()

    @pytest.mark.skip(reason="БАГ: сервер возвращает 404 вместо 400")
    def test_patch_movie_extra_field(self, api_manager, create_film_id):
        """Негатив/Позитив: PATCH с лишним полем (должен проигнорировать или вернуть ошибку)"""
        movie_id = create_film_id

        patch_data = {
            "name": faker.sentence(nb_words=4),
            "extraField": "что-то лишнее",
            "anotherExtra": 12345
        }

        response = api_manager.films_api.patch_movie(movie_id, patch_data, expected_status=[200, 400])

        assert response.status_code in [200, 400], f"Неожиданный статус: {response.status_code}"

        if response.status_code == 200:
            get_movie = api_manager.films_api.get_movie(movie_id)
            assert get_movie.json().get("name") == patch_data["name"], "Имя не обновилось"
            assert get_movie.json().get("extraField") is None, "Добавилось лишнее поле"
        api_manager.clear_token()

    @pytest.mark.skip(reason="БАГ: сервер возвращает 404 вместо 400")
    def test_patch_movie_only_extra_field(self, api_manager, create_film_id):
        """Негатив: PATCH только с лишним полем (без изменений)"""
        movie_id = create_film_id

        response = api_manager.films_api.patch_movie(movie_id, {"extraField": "лишнее"}, expected_status=[200, 400])

        assert response.status_code in [200, 400], f"Неожиданный статус: {response.status_code}"

        if response.status_code == 200:
            get_after = api_manager.films_api.get_movie(movie_id)
            assert get_after.json().get("extraField") is None, "Добавилось лишнее поле"
        api_manager.clear_token()

    @pytest.mark.skip(reason="БАГ: сервер возвращает 404 вместо 405")
    def test_put_movie_not_allowed(self, api_manager, create_film_id):
        """Негатив: PUT метод не должен работать (в документации его нет)"""
        movie_id = create_film_id
        response = api_manager.films_api.send_request("PUT", f"/movies/{movie_id}", data={"name": "new"},
                                                      expected_status=405)
        assert response.status_code == 405, "PUT метод работает, хотя не должен"
        api_manager.clear_token()