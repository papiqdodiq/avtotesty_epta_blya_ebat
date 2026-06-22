import allure
import pytest
from faker import Faker
from utils.validators import assert_valid_iso_datetime, assert_datetime_in_range
from datetime import datetime, timezone, timedelta
from models.base_models import BillboardParams

faker = Faker('ru_RU')

@allure.epic("Управление фильмами")
@allure.feature("Позитивные сценарии работы с фильмами")
class TestPositiveMovies:

    # задание на параметризацию выполнено тут:
    @allure.story("Получение афиши")
    @allure.title("Получение афиши без токена с параметризацией фильтров")
    @allure.description("""
    Проверяем получение афиши (списка фильмов) без токена с различными параметрами фильтрации:
    - minPrice, maxPrice
    - locations (MSK/SPB)
    - genreId
    Ожидаем: статус 200, структура ответа валидна, цены и локации соответствуют фильтрам.
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.regression
    @pytest.mark.api
    @pytest.mark.parametrize("min_price,max_price,locations,genre_id", [(1, 1000, ["MSK", "SPB"], 1),
                                                                        (100, 1000, "SPB", 3), (10, 10000, "MSK", 4)])
    def test_get_billboard_without_token(self, api_manager, min_price, max_price, locations, genre_id):
        """Позитив: получение афиши без токена."""
        with allure.step("Формируем параметры запроса BillboardParams"):
            billboard_params = BillboardParams(
                pageSize=faker.random_int(min=1, max=15),
                page=faker.random_int(min=1, max=100),
                minPrice=min_price,
                maxPrice=max_price,
                locations=locations,
                published=True,
                genreId=genre_id,
                createdAt="asc"
            )

        with allure.step(f"Отправляем GET запрос на /movies с параметрами: minPrice={min_price}, maxPrice={max_price}, "
                         f"locations={locations}, genreId={genre_id}"):
            get_billboard = api_manager.films_api.get_billboard(billboard_params.model_dump(), pydantic=True)

        with allure.step("Проверяем совпадение page и pageSize с параметрами запроса"):
            assert get_billboard.page == billboard_params.page, "Номер страницы отличается"
            assert get_billboard.pageSize == billboard_params.pageSize, "Размер страницы отличается"

        with allure.step("Проверяем первые 3 фильма на соответствие фильтрам"):
            if get_billboard.movies:
                for idx, movie in enumerate(get_billboard.movies[:3]):
                    allure.attach(f"Фильм {idx + 1}: id={movie.id}, name={movie.name}, price={movie.price}, "
                                  f"location={movie.location}, genreId={movie.genreId}", name=f"movie_{idx + 1}",
                                  attachment_type=allure.attachment_type.TEXT)
                    assert min_price <= movie.price <= max_price, f"Цена {movie.price} вне диапазона"
                    if isinstance(locations, list):
                        assert movie.location in locations, f"Локация {movie.location} не в {locations}"
                    else:
                        assert movie.location == locations, f"Локация {movie.location} не равна {locations}"
                    assert movie.genreId == genre_id, f"Жанр {movie.genreId} не равен {genre_id}"

    @allure.story("Получение афиши")
    @allure.title("Получение афиши с токеном")
    @allure.description("Проверяем получение афиши (списка фильмов) авторизованным пользователем.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke
    @pytest.mark.regression
    @pytest.mark.api
    def test_get_billboard(self, api_manager_admin, billboard_params):
        """Позитив: получение афиши с токеном."""
        with allure.step("Отправляем GET запрос на /movies с токеном"):
            get_billboard = api_manager_admin.films_api.get_billboard(billboard_params)
            data = get_billboard.json()

        with allure.step("Проверяем структуру ответа"):
            required_fields = ["movies", "count", "page", "pageSize", "pageCount"]
            for field in required_fields:
                assert field in data, f"Отсутствует поле {field}"

        with allure.step("Проверяем типы данных"):
            assert isinstance(data["movies"], list), "movies должен быть списком"
            assert isinstance(data["count"], int), "count должен быть числом"
            assert isinstance(data["page"], int), "page должен быть числом"
            assert isinstance(data["pageSize"], int), "pageSize должен быть числом"
            assert isinstance(data["pageCount"], int), "pageCount должен быть числом"

        with allure.step("Проверяем совпадение page и pageSize с параметрами запроса"):
            assert data["page"] == billboard_params["page"], "Номер страницы отличается"
            assert data["pageSize"] == billboard_params["pageSize"], "Размер страницы отличается"

        with allure.step("Проверяем структуру первого фильма"):
            if data["movies"]:
                movie = data["movies"][0]
                movie_fields = ["id", "name", "description", "price", "rating", "createdAt", "genre",
                                "imageUrl", "location", "published", "genreId"]
                for field in movie_fields:
                    assert field in movie, f"У фильма отсутствует поле {field}"

    @allure.story("Получение афиши")
    @allure.title("Получение афиши с изменёнными параметрами")
    @allure.description("""
    Проверяем получение афиши с изменёнными параметрами:
    - убираем locations
    - меняем published на False
    - меняем createdAt на desc
    """)
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_get_billboard_updated(self, api_manager, billboard_params):
        """Позитив: получение афиши с изменёнными параметрами."""
        with allure.step("Модифицируем параметры запроса"):
            new_billboard_params = billboard_params.copy()
            new_billboard_params.update({
                "published": False,
                "createdAt": "desc"
            })
            del new_billboard_params["locations"]

        with allure.step("Отправляем GET запрос с изменёнными параметрами"):
            get_billboard = api_manager.films_api.get_billboard(new_billboard_params)
            data = get_billboard.json()

        with allure.step("Проверяем структуру ответа"):
            required_fields = ["movies", "count", "page", "pageSize", "pageCount"]
            for field in required_fields:
                assert field in data, f"Отсутствует поле {field}"

        with allure.step("Проверяем типы данных"):
            assert isinstance(data["movies"], list), "movies должен быть списком"
            assert isinstance(data["count"], int), "count должен быть числом"
            assert isinstance(data["page"], int), "page должен быть числом"
            assert isinstance(data["pageSize"], int), "pageSize должен быть числом"
            assert isinstance(data["pageCount"], int), "pageCount должен быть числом"

        with allure.step("Проверяем совпадение page и pageSize с параметрами запроса"):
            assert data["page"] == billboard_params["page"], "Номер страницы отличается"
            assert data["pageSize"] == billboard_params["pageSize"], "Размер страницы отличается"

        with allure.step("Проверяем структуру первого фильма"):
            if data["movies"]:
                movie = data["movies"][0]
                movie_fields = ["id", "name", "description", "price", "rating", "createdAt", "genre",
                                "imageUrl", "location", "published", "genreId"]
                for field in movie_fields:
                    assert field in movie, f"У фильма отсутствует поле {field}"

    @allure.story("Создание фильма")
    @allure.title("Успешное создание фильма")
    @allure.description("""
    Проверяем создание фильма через API.
    Шаги:
    1. Создаём фильм (фикстура create_film)
    2. Проверяем совпадение данных
    3. Получаем фильм по ID и проверяем, что он появился в БД
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.regression
    @pytest.mark.api
    def test_create_movie(self, api_manager, create_film, film_data, db_helper): # в фикстуре юзал бд проверки через sql alchemy
        """Позитив: создание фильма."""
        with allure.step("Создаём фильм через фикстуру"):
            create_data = create_film.json()
            movie_id = create_film.json()["id"]

        with allure.step("Проверяем совпадение с отправленными данными"):
            assert create_data["name"] == film_data["name"]
            assert create_data["price"] == film_data["price"]
            assert create_data["location"] == film_data["location"]
            assert create_data["published"] == film_data["published"]
            assert create_data["genreId"] == film_data["genreId"]

        with allure.step("Получаем фильм по ID и проверяем данные в БД"):
            get_movie = db_helper.get_movie_by_id(movie_id)
            get_data = get_movie.to_dict()
            assert get_data["id"] == movie_id
            assert get_data["name"] == film_data["name"]
            assert get_data["price"] == film_data["price"]
            assert get_data["location"] == film_data["location"]
            assert get_data["published"] == film_data["published"]
            assert get_data["genre_id"] == film_data["genreId"]
            assert get_data["description"] == film_data["description"]
            assert get_data["image_url"] == film_data["imageUrl"]

    @allure.story("Создание фильма")
    @allure.title("Создание фильма с обновлёнными параметрами")
    @allure.description("""
    Проверяем создание фильма с параметрами:
    - location = MSK
    - published = False
    - genreId = 2
    """)
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_create_movie_updated(self, api_manager_admin, film_data):
        """Позитив: создание фильма с обновлёнными параметрами."""
        new_film_data = film_data.copy()
        new_film_data.update({
            "name": faker.sentence(nb_words=4),
            "location": "MSK",
            "published": False,
            "genreId": 2
        })

        with allure.step("Создаем фильм и фиксируем время до и после запроса для проверки createdAt"):
            before_request = datetime.now(timezone.utc) - timedelta(seconds=5)
            create_movie = api_manager_admin.films_api.create_movie(new_film_data)
            after_request = datetime.now(timezone.utc) + timedelta(seconds=10)

        with allure.step("Проверяем формат createdAt (ISO 8601)"):
            assert_valid_iso_datetime(create_movie.json()["createdAt"])
            assert_datetime_in_range(create_movie.json()["createdAt"], before_request, after_request)

        movie_id = create_movie.json()["id"]

        with allure.step("Получаем фильм по ID и проверяем данные"):
            get_movie = api_manager_admin.films_api.get_movie(movie_id)
            get_data = get_movie.json()
            assert get_data["name"] == new_film_data["name"]
            assert get_data["location"] == new_film_data["location"]
            assert get_data["published"] == new_film_data["published"]
            assert get_data["genreId"] == new_film_data["genreId"]

        with allure.step("Удаляем созданный фильм"):
            api_manager_admin.films_api.delete_movie(movie_id)

    @allure.story("Создание фильма")
    @allure.title("Проверка уникальности ID при создании двух фильмов")
    @allure.description("Проверяем, что при создании двух фильмов их ID различаются.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_create_movie_unique_id(self, api_manager_admin, create_film, film_data):
        """Позитив: при создании двух фильмов id разные"""
        with allure.step("Создаём первый фильм"):
            first_id = create_film.json()["id"]

        with allure.step("Создаём второй фильм"):
            new_film_data = film_data.copy()
            new_film_data["name"] = faker.sentence(nb_words=4)
            second_movie = api_manager_admin.films_api.create_movie(new_film_data)
            second_id = second_movie.json()["id"]

        with allure.step("Проверяем, что ID разные"):
            assert first_id != second_id, "ID совпадают у разных фильмов"

        with allure.step("Удаляем второй фильм"):
            api_manager_admin.films_api.delete_movie(second_id)

    @allure.story("Получение фильма по ID")
    @allure.title("Получение фильма по ID без токена")
    @allure.description("Проверяем, что публичный эндпоинт /movies/{id} доступен без авторизации.")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.regression
    @pytest.mark.api
    def test_get_movie_without_token(self, api_manager, create_film):
        """Позитив: получение фильма по ID без токена."""
        movie_id = create_film.json()["id"]

        with allure.step(f"Отправляем GET запрос на /movies/{movie_id} без токена"):
            get_movie = api_manager.films_api.get_movie(movie_id)
            data = get_movie.json()

        with allure.step("Проверяем структуру ответа (все обязательные поля есть)"):
            required_fields = ["id", "name", "price", "description", "imageUrl",
                               "location", "published", "genreId", "genre", "createdAt", "reviews", "rating"]
            for field in required_fields:
                assert field in data, f"Отсутствует поле {field}"

        with allure.step("Проверяем типы данных"):
            assert isinstance(data["genre"], dict), "genre должен быть словарем"
            assert isinstance(data["reviews"], list), "reviews должен быть списком"
            assert isinstance(data["id"], int), "id должен быть числом"
            assert isinstance(data["name"], str), "name должен быть строкой"
            assert isinstance(data["price"], int), "price должен быть числом"
            assert isinstance(data["published"], bool), "published должен быть булевым"
            assert isinstance(data["genreId"], int), "genreId должен быть числом"

        with allure.step("Проверяем содержимое"):
            assert data["id"] == movie_id, "ID не совпадает"
            assert data["name"] is not None, "name не может быть пустым"
            assert data["price"] > 0, "price должен быть больше 0"
            assert "name" in data["genre"], "У genre отсутствует поле name"
            assert isinstance(data["genre"]["name"], str), "genre.name должен быть строкой"

    @allure.story("Получение фильма по ID")
    @allure.title("Получение фильма по ID с токеном")
    @allure.description("Проверяем, что авторизованный пользователь может получить фильм по ID.")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.regression
    @pytest.mark.api
    def test_get_movie(self, api_manager_admin, create_film):
        """Позитив: получение фильма по ID с токеном."""
        movie_id = create_film.json()["id"]

        with allure.step(f"Отправляем GET запрос на /movies/{movie_id} с токеном"):
            get_movie = api_manager_admin.films_api.get_movie(movie_id)
            data = get_movie.json()

        with allure.step("Проверяем структуру ответа"):
            required_fields = ["id", "name", "price", "description", "imageUrl",
                               "location", "published", "genreId", "genre", "createdAt", "reviews", "rating"]
            for field in required_fields:
                assert field in data, f"Отсутствует поле {field}"

        with allure.step("Проверяем типы данных"):
            assert isinstance(data["genre"], dict), "genre должен быть словарем"
            assert isinstance(data["reviews"], list), "reviews должен быть списком"
            assert isinstance(data["id"], int), "id должен быть числом"
            assert isinstance(data["name"], str), "name должен быть строкой"
            assert isinstance(data["price"], int), "price должен быть числом"
            assert isinstance(data["published"], bool), "published должен быть булевым"
            assert isinstance(data["genreId"], int), "genreId должен быть числом"

        with allure.step("Проверяем содержимое"):
            assert data["id"] == movie_id, "ID не совпадает"
            assert data["name"] is not None, "name не может быть пустым"
            assert data["price"] > 0, "price должен быть больше 0"
            assert "name" in data["genre"], "У genre отсутствует поле name"
            assert isinstance(data["genre"]["name"], str), "genre.name должен быть строкой"

    @allure.story("Удаление фильма")
    @allure.title("Успешное удаление фильма")
    @allure.description("""
        Проверяем удаление фильма через API.
        Шаги:
        1. Создаём фильм
        2. Удаляем его
        3. Проверяем, что при GET запросе возвращается 404
        """)
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.regression
    @pytest.mark.api
    def test_delete_movie(self, api_manager_admin, film_data):
        """Позитив: удаление фильма по ID."""
        with allure.step("Создаём фильм"):
            create_movie = api_manager_admin.films_api.create_movie(film_data)
            movie_id = create_movie.json()["id"]

        with allure.step(f"Удаляем фильм с ID {movie_id}"):
            delete_movie = api_manager_admin.films_api.delete_movie(movie_id)
            data = delete_movie.json()
            required_fields = ["id", "name", "price", "description", "imageUrl",
                               "location", "published", "genreId", "genre", "createdAt", "rating"]
            for field in required_fields:
                assert field in data, f"Отсутствует поле {field}"

        with allure.step("Проверяем, что фильм больше не доступен"):
            api_manager_admin.films_api.get_movie(movie_id, expected_status=404)

    @allure.story("Частичное обновление фильма")
    @allure.title("Успешное частичное обновление фильма (PATCH)")
    @allure.description("""
        Проверяем частичное обновление фильма через PATCH запрос.
        Обновляем только name и location, остальные поля не должны измениться.
        """)
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.regression
    @pytest.mark.api
    def test_patch_movie(self, api_manager_admin, create_film, film_data):
        """Позитив: частичное обновление фильма (PATCH)."""
        movie_id = create_film.json()["id"]

        film_data_patch = {
            "name": faker.sentence(nb_words=4),
            "location": "MSK",
        }

        with allure.step(f"Отправляем PATCH запрос на /movies/{movie_id} с новыми name и location"):
            patch_movie = api_manager_admin.films_api.patch_movie(movie_id, film_data_patch)
            data = patch_movie.json()
            required_fields = ["id", "name", "price", "description", "imageUrl",
                               "location", "published", "genreId", "genre", "createdAt", "rating"]
            for field in required_fields:
                assert field in data, f"Отсутствует поле {field}"

        with allure.step("Проверяем типы данных"):
            assert isinstance(data["genre"], dict), "genre должен быть словарем"
            assert isinstance(data["id"], int), "id должен быть числом"
            assert isinstance(data["name"], str), "name должен быть строкой"
            assert isinstance(data["price"], int), "price должен быть числом"
            assert isinstance(data["published"], bool), "published должен быть булевым"
            assert isinstance(data["genreId"], int), "genreId должен быть числом"
            assert data["id"] == movie_id, "ID не совпадает"

        with allure.step("Проверяем, что данные действительно обновились"):
            get_movie = api_manager_admin.films_api.get_movie(movie_id)
            assert get_movie.json().get("name") == film_data_patch["name"]
            assert get_movie.json().get("location") == film_data_patch["location"]
            assert get_movie.json().get("price") == film_data["price"]


@allure.epic("Управление фильмами")
@allure.feature("Негативные сценарии работы с фильмами")
class TestNegativeMovies:

    # ========== GET /movies ==========
    @allure.story("Получение афиши")
    @allure.title("Ошибка при minPrice > maxPrice")
    @allure.description("Проверяем, что при minPrice > maxPrice сервер возвращает 400.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_get_billboard_min_price_greater_than_max(self, api_manager, billboard_params):
        """Негатив: запрос с минимальной ценой выше максимальной цены"""
        with allure.step("Устанавливаем minPrice=1000, maxPrice=100"):
            negative_params = billboard_params.copy()
            negative_params["minPrice"] = 1000
            negative_params["maxPrice"] = 100

        with allure.step("Отправляем запрос и ожидаем 400"):
            api_manager.films_api.get_billboard(negative_params, expected_status=400)

    @allure.story("Получение афиши")
    @allure.title("Ошибка при запросе несуществующей страницы")
    @allure.description("Проверяем, что при запросе несуществующей страницы сервер возвращает 400.")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.skip(reason="БАГ: сервер возвращает 200 вместо 400")
    @pytest.mark.regression
    @pytest.mark.api
    def test_get_billboard_page_out_of_range(self, api_manager, billboard_params):
        """Негатив: запрос с несуществующей страницей"""
        with allure.step("Устанавливаем page=999999"):
            negative_params = billboard_params.copy()
            negative_params["page"] = 999999

        with allure.step("Отправляем запрос и ожидаем 400"):
            api_manager.films_api.get_billboard(negative_params, expected_status=400)

    @allure.story("Получение афиши")
    @allure.title("Ошибка при запросе с несуществующим жанром")
    @allure.description("Проверяем, что при запросе с несуществующим genreId сервер возвращает 400.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.skip(reason="БАГ: сервер возвращает 200 вместо 400")
    @pytest.mark.regression
    @pytest.mark.api
    def test_get_billboard_with_invalid_genre(self, api_manager, billboard_params):
        """Негатив: запрос с несуществующим жанром"""
        with allure.step("Устанавливаем genreId=999"):
            negative_params = billboard_params.copy()
            negative_params["genreId"] = 999

        with allure.step("Отправляем запрос и ожидаем 400"):
            api_manager.films_api.get_billboard(negative_params, expected_status=400)

    @allure.story("Получение афиши")
    @allure.title("Ошибка при отрицательной странице")
    @allure.description("Проверяем, что при page < 0 сервер возвращает 400.")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    @pytest.mark.api
    def test_get_billboard_negative_page(self, api_manager, billboard_params):
        """Негатив: отрицательная страница"""
        with allure.step("Устанавливаем page=-1"):
            negative_params = billboard_params.copy()
            negative_params["page"] = -1

        with allure.step("Отправляем запрос и ожидаем 400"):
            api_manager.films_api.get_billboard(negative_params, expected_status=400)

    @allure.story("Получение афиши")
    @allure.title("Ошибка при отрицательном pageSize")
    @allure.description("Проверяем, что при pageSize < 0 сервер возвращает 400.")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    @pytest.mark.api
    def test_get_billboard_negative_page_size(self, api_manager, billboard_params):
        """Негатив: отрицательный pageSize"""
        with allure.step("Устанавливаем pageSize=-10"):
            negative_params = billboard_params.copy()
            negative_params["pageSize"] = -10

        with allure.step("Отправляем запрос и ожидаем 400"):
            api_manager.films_api.get_billboard(negative_params, expected_status=400)

    @allure.story("Получение афиши")
    @allure.title("Ошибка при несуществующей локации")
    @allure.description("Проверяем, что при location=MOON сервер возвращает 400.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_get_billboard_invalid_location(self, api_manager, billboard_params):
        """Негатив: несуществующая локация"""
        with allure.step("Устанавливаем locations='MOON'"):
            negative_params = billboard_params.copy()
            negative_params["locations"] = "MOON"

        with allure.step("Отправляем запрос и ожидаем 400"):
            api_manager.films_api.get_billboard(negative_params, expected_status=400)

    # ========== POST /movies ==========
    @allure.story("Создание фильма")
    @allure.title("Создание фильма без авторизации")
    @allure.description("Проверяем, что без токена нельзя создать фильм. Ожидаем 401.")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_create_movie_without_token(self, api_manager, film_data):
        """Негатив: создание фильма без авторизации"""
        with allure.step("Пытаемся создать фильм без токена"):
            api_manager.films_api.create_movie(film_data, expected_status=401)

    @allure.story("Создание фильма")
    @allure.title("Создание фильма с неверным токеном")
    @allure.description("Проверяем, что с невалидным токеном нельзя создать фильм. Ожидаем 401.")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_create_movie_with_invalid_token(self, api_manager, film_data):
        """Негатив: создание фильма с неверным токеном"""
        with allure.step("Устанавливаем неверный токен"):
            api_manager.set_token("invalid_token")

        with allure.step("Пытаемся создать фильм"):
            api_manager.films_api.create_movie(film_data, expected_status=401)

        with allure.step("Чистим токен"):
            api_manager.clear_token()

    @allure.story("Создание фильма")
    @allure.title("Создание фильма с пустым именем")
    @allure.description("Проверяем, что нельзя создать фильм с пустым name. Ожидаем 400.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_create_movie_empty_name(self, api_manager_admin, film_data):
        """Негатив: создание фильма с пустым именем"""
        with allure.step("Устанавливаем пустое имя"):
            new_film_data = film_data.copy()
            new_film_data["name"] = ""

        with allure.step("Пытаемся создать фильм"):
            api_manager_admin.films_api.create_movie(new_film_data, expected_status=400)

    @allure.story("Создание фильма")
    @allure.title("Создание фильма с уже существующим именем")
    @allure.description("Проверяем, что нельзя создать фильм с именем, которое уже существует. Ожидаем 409.")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_create_movie_same_name(self, api_manager_admin, create_film, film_data):
        """Негатив: создание фильма с таким же именем"""
        with allure.step("Пытаемся создать фильм с уже существующим именем"):
            api_manager_admin.films_api.create_movie(film_data, expected_status=409)

    @allure.story("Создание фильма")
    @allure.title("Создание фильма без обязательного поля")
    @allure.description("Проверяем, что при отсутствии обязательного поля сервер возвращает 400.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_create_movie_without_required_field(self, api_manager_admin, film_data):
        """Негатив: создание фильма без обязательного поля"""
        with allure.step("Удаляем обязательное поле name"):
            data = film_data.copy()
            del data["name"]

        with allure.step("Пытаемся создать фильм"):
            api_manager_admin.films_api.create_movie(data, expected_status=400)

    @allure.story("Создание фильма")
    @allure.title("Создание фильма с пустым телом запроса")
    @allure.description("Проверяем, что при пустом теле запроса сервер возвращает 400.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_create_movie_empty_body(self, api_manager_admin):
        """Негатив: создание фильма с пустым телом запроса"""
        with allure.step("Отправляем пустой запрос"):
            api_manager_admin.films_api.create_movie({}, expected_status=400)

    @allure.story("Создание фильма")
    @allure.title("Создание фильма с ценой в виде строки")
    @allure.description("Проверяем, что при передаче price в виде строки (неверный тип) сервер возвращает 400.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_create_movie_invalid_price_type(self, api_manager_admin, film_data):
        """Негатив: создание фильма с ценой в виде строки (неверный тип)"""
        with allure.step("Устанавливаем price='сто рублей'"):
            data = film_data.copy()
            data["price"] = "сто рублей"

        with allure.step("Пытаемся создать фильм"):
            api_manager_admin.films_api.create_movie(data, expected_status=400)

    @allure.story("Создание фильма")
    @allure.title("Создание фильма с лишним полем")
    @allure.description("Проверяем, как сервер реагирует на лишние поля в запросе.")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.skip(reason="БАГ: сервер возвращает 200 вместо 400")
    @pytest.mark.regression
    @pytest.mark.api
    def test_create_movie_extra_field(self, api_manager_admin, film_data):
        """Негатив: создание фильма с лишним полем"""
        with allure.step("Добавляем лишнее поле extraField"):
            data = film_data.copy()
            data["extraField"] = "что-то лишнее"

        with allure.step("Пытаемся создать фильм"):
            api_manager_admin.films_api.create_movie(data, expected_status=400)

    @allure.story("Создание фильма")
    @allure.title("Создание фильма с несуществующим genreId")
    @allure.description("Проверяем, что при создании фильма с несуществующим genreId сервер возвращает 400.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_create_movie_invalid_genre_id(self, api_manager_admin, film_data):
        """Негатив: создание фильма с несуществующим genreId"""
        with allure.step("Устанавливаем genreId=999999"):
            data = film_data.copy()
            data["genreId"] = 999999

        with allure.step("Пытаемся создать фильм"):
            api_manager_admin.films_api.create_movie(data, expected_status=400)

    @allure.story("Создание фильма")
    @allure.title("Создание фильма с отрицательной ценой")
    @allure.description("Проверяем, что при отрицательной цене сервер возвращает 400.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.skip(reason="БАГ: сервер возвращает 201 вместо 400")
    @pytest.mark.regression
    @pytest.mark.api
    def test_create_movie_negative_price(self, api_manager_admin, film_data):
        """Негатив: создание фильма с отрицательной ценой"""
        with allure.step("Устанавливаем price=-100"):
            data = film_data.copy()
            data["price"] = -100

        with allure.step("Пытаемся создать фильм"):
            api_manager_admin.films_api.create_movie(data, expected_status=400)

    @allure.story("Создание фильма")
    @allure.title("Создание фильма с несуществующей локацией")
    @allure.description("Проверяем, что при создании фильма с location='MOON' сервер возвращает 400.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_create_movie_invalid_location(self, api_manager_admin, film_data):
        """Негатив: создание фильма с несуществующей локацией"""
        with allure.step("Устанавливаем location='MOON'"):
            data = film_data.copy()
            data["location"] = "MOON"

        with allure.step("Пытаемся создать фильм"):
            api_manager_admin.films_api.create_movie(data, expected_status=400)

    # ========== GET /movies/{id} ==========
    @allure.story("Получение фильма по ID")
    @allure.title("Получение фильма с несуществующим ID")
    @allure.description("Проверяем, что при GET запросе с несуществующим ID возвращается 404.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_get_movie_invalid_id(self, api_manager):
        """Негатив: получение фильма с несуществующим ID"""
        with allure.step("Пытаемся получить фильм с ID 999999"):
            api_manager.films_api.get_movie(999999, expected_status=404)

    @allure.story("Получение фильма по ID")
    @allure.title("Получение фильма с отрицательным ID")
    @allure.description("Проверяем, что при GET запросе с отрицательным ID возвращается 404.")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    @pytest.mark.api
    def test_get_movie_negative_id(self, api_manager):
        """Негатив: получение фильма с отрицательным ID"""
        with allure.step("Пытаемся получить фильм с ID -1"):
            api_manager.films_api.get_movie(-1, expected_status=404)

    @allure.story("Получение фильма по ID")
    @allure.title("Получение фильма с ID = 0")
    @allure.description("Проверяем, что при GET запросе с ID 0 возвращается 404.")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    @pytest.mark.api
    def test_get_movie_zero_id(self, api_manager):
        """Негатив: получение фильма с ID = 0"""
        with allure.step("Пытаемся получить фильм с ID 0"):
            api_manager.films_api.get_movie(0, expected_status=404)

    @allure.story("Получение фильма по ID")
    @allure.title("Получение фильма с ID в виде строки")
    @allure.description("Проверяем, что при GET запросе с строковым ID возвращается 404.")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.skip(reason="БАГ: сервер возвращает 500 вместо 404")
    @pytest.mark.regression
    @pytest.mark.api
    def test_get_movie_string_id(self, api_manager):
        """Негатив: получение фильма с ID в виде строки"""
        with allure.step("Пытаемся получить фильм с ID 'abc'"):
            api_manager.films_api.get_movie("abc", expected_status=404)

    # ========== DELETE /movies/{id} ==========, задание на параметризацию и ролевую модель выполнено тут:
    @allure.story("Удаление фильма")
    @allure.title("Удаление фильма без авторизации")
    @allure.description("Проверяем, что без токена нельзя удалить фильм. Ожидаем 401.")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_delete_movie_without_token(self, api_manager, create_film):
        """Негатив: удаление фильма без авторизации"""
        movie_id = create_film.json()["id"]

        with allure.step(f"Пытаемся удалить фильм {movie_id} без токена"):
            api_manager.films_api.delete_movie(movie_id, expected_status=401)

    @allure.story("Удаление фильма")
    @allure.title("Удаление фильма без нужных прав")
    @allure.description("Проверяем, что обычный пользователь (common_user) и admin не могут удалить фильм. Ожидаем 403.")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.slow
    @pytest.mark.parametrize("role", ["common_user", "admin"])
    @pytest.mark.skip(
        reason="Баг: в сваге ADMIN не может удалять, только SUPER_ADMIN, но тест спокойно удаляет через ADMIN фикстуру")
    @pytest.mark.regression
    @pytest.mark.api
    def test_delete_movie_without_rights(self, role, create_film, request):
        """Негатив: удаление фильма без нужных прав. Параметризация ролевой модели."""
        user = request.getfixturevalue(role)
        movie_id = create_film.json()["id"]

        with allure.step(f"Пытаемся удалить фильм от имени {role}"):
            response = user.api.films_api.delete_movie(movie_id, expected_status=403)
            error_data = response.json()
            assert error_data.get("statusCode") == 403
            assert error_data.get("message") == "Forbidden resource"
            assert error_data.get("error") == "Forbidden"

        with allure.step("Проверяем, что фильм не удалился"):
            user.api.films_api.get_movie(movie_id)

    @allure.story("Удаление фильма")
    @allure.title("Удаление фильма с неверным токеном")
    @allure.description("Проверяем, что с невалидным токеном нельзя удалить фильм. Ожидаем 401.")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_delete_movie_with_invalid_token(self, api_manager, create_film):
        """Негатив: удаление фильма с неверным токеном"""
        movie_id = create_film.json()["id"]

        with allure.step("Устанавливаем неверный токен"):
            api_manager.set_token("invalid_token")

        with allure.step("Пытаемся удалить фильм"):
            api_manager.films_api.delete_movie(movie_id, expected_status=401)

        with allure.step("Чистим токен"):
            api_manager.clear_token()

    @allure.story("Удаление фильма")
    @allure.title("Удаление фильма с некорректными ID (параметризация)")
    @allure.description("Проверяем, что при удалении с некорректными ID (999999, -1, 0, 'abc') возвращается 404.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    @pytest.mark.parametrize("movie_id", [999999, -1, 0, "abc"])
    def test_delete_movie_invalid_id(self, super_admin, movie_id):
        """Негатив: удаление фильма с некорректными ID"""
        with allure.step(f"Пытаемся удалить фильм с ID {movie_id}"):
            super_admin.api.films_api.delete_movie(movie_id, expected_status=404)

    # ========== PATCH /movies/{id} ==========
    @allure.story("Частичное обновление фильма")
    @allure.title("PATCH без авторизации")
    @allure.description("Проверяем, что без токена нельзя обновить фильм. Ожидаем 401.")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_patch_movie_without_token(self, api_manager, create_film):
        """Негатив: редактирование фильма без токена"""
        movie_id = create_film.json()["id"]

        with allure.step(f"Пытаемся обновить фильм {movie_id} без токена"):
            api_manager.films_api.patch_movie(movie_id, {"name": "new"}, expected_status=401)

    @allure.story("Частичное обновление фильма")
    @allure.title("PATCH с неверным токеном")
    @allure.description("Проверяем, что с невалидным токеном нельзя обновить фильм. Ожидаем 401.")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_patch_movie_with_invalid_token(self, api_manager, create_film):
        """Негатив: редактирование фильма с неверным токеном"""
        movie_id = create_film.json()["id"]

        with allure.step("Устанавливаем неверный токен"):
            api_manager.set_token("invalid_token")

        with allure.step(f"Пытаемся обновить фильм {movie_id}"):
            api_manager.films_api.patch_movie(movie_id, {"name": "new"}, expected_status=401)

        with allure.step("Чистим токен"):
            api_manager.clear_token()

    @allure.story("Частичное обновление фильма")
    @allure.title("PATCH с несуществующим ID")
    @allure.description("Проверяем, что при обновлении несуществующего фильма возвращается 404.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_patch_movie_invalid_id(self, api_manager_admin):
        """Негатив: редактирование несуществующего фильма"""
        with allure.step("Пытаемся обновить фильм с ID 999999"):
            api_manager_admin.films_api.patch_movie(999999, {"name": "new"}, expected_status=404)

    @allure.story("Частичное обновление фильма")
    @allure.title("PATCH с отрицательной ценой")
    @allure.description("Проверяем, что при обновлении с отрицательной ценой возвращается 400.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_patch_movie_negative_price(self, api_manager_admin, create_film):
        """Негатив: редактирование с отрицательной ценой"""
        movie_id = create_film.json()["id"]

        with allure.step(f"Пытаемся обновить фильм {movie_id} с price=-100"):
            api_manager_admin.films_api.patch_movie(movie_id, {"price": -100}, expected_status=400)

    @allure.story("Частичное обновление фильма")
    @allure.title("PATCH с дублирующим именем")
    @allure.description("Проверяем, что при обновлении имени на уже существующее возвращается 409.")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.skip(reason="БАГ: сервер возвращает 404 вместо 409")
    @pytest.mark.regression
    @pytest.mark.api
    def test_patch_movie_duplicate_name(self, api_manager_admin, create_film, film_data):
        """Негатив: редактирование имени на уже существующее название фильма"""
        existing_name = create_film.json()["name"]

        with allure.step("Создаём второй фильм"):
            new_film_data = film_data.copy()
            new_film_data["name"] = faker.sentence(nb_words=4)
            second_response = api_manager_admin.films_api.create_movie(new_film_data)
            second_movie_id = second_response.json()["id"]

        with allure.step(f"Пытаемся обновить второй фильм, меняя имя на '{existing_name}'"):
            api_manager_admin.films_api.patch_movie(second_movie_id, {"name": existing_name}, expected_status=409)

        with allure.step("Удаляем второй фильм"):
            api_manager_admin.films_api.delete_movie(second_movie_id)

    @allure.story("Частичное обновление фильма")
    @allure.title("PATCH с пустым названием")
    @allure.description("Проверяем, что при обновлении с пустым name возвращается 400.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.skip(reason="БАГ: сервер возвращает 404 вместо 400")
    @pytest.mark.regression
    @pytest.mark.api
    def test_patch_movie_empty_name(self, api_manager_admin, create_film):
        """Негатив: редактирование с пустым названием"""
        movie_id = create_film.json()["id"]

        with allure.step(f"Пытаемся обновить фильм {movie_id} с name='' "):
            api_manager_admin.films_api.patch_movie(movie_id, {"name": ""}, expected_status=400)

    @allure.story("Частичное обновление фильма")
    @allure.title("PATCH с несуществующим жанром")
    @allure.description("Проверяем, что при обновлении с несуществующим genreId возвращается 400.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.skip(reason="БАГ: сервер возвращает 404 вместо 400")
    @pytest.mark.regression
    @pytest.mark.api
    def test_patch_movie_invalid_genre(self, api_manager_admin, create_film):
        """Негатив: редактирование с несуществующим жанром"""
        movie_id = create_film.json()["id"]

        with allure.step(f"Пытаемся обновить фильм {movie_id} с genreId=999"):
            api_manager_admin.films_api.patch_movie(movie_id, {"genreId": 999}, expected_status=400)

    @allure.story("Частичное обновление фильма")
    @allure.title("PATCH с несуществующей локацией")
    @allure.description("Проверяем, что при обновлении с location='MOON' возвращается 400.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_patch_movie_invalid_location(self, api_manager_admin, create_film):
        """Негатив: редактирование с несуществующей локацией"""
        movie_id = create_film.json()["id"]

        with allure.step(f"Пытаемся обновить фильм {movie_id} с location='MOON'"):
            api_manager_admin.films_api.patch_movie(movie_id, {"location": "MOON"}, expected_status=400)

    @allure.story("Частичное обновление фильма")
    @allure.title("PATCH с ID в виде строки")
    @allure.description("Проверяем, что при обновлении с строковым ID возвращается 404.")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    @pytest.mark.api
    def test_patch_movie_string_id(self, api_manager_admin):
        """Негатив: редактирование с ID в виде строки"""
        with allure.step("Пытаемся обновить фильм с ID 'abc'"):
            api_manager_admin.films_api.patch_movie("abc", {"name": "new"}, expected_status=404)

    @allure.story("Частичное обновление фильма")
    @allure.title("PATCH с ценой в виде строки")
    @allure.description("Проверяем, что при обновлении с price в виде строки возвращается 400.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_patch_movie_invalid_price_type(self, api_manager_admin, create_film):
        """Негатив: PATCH с ценой в виде строки"""
        movie_id = create_film.json()["id"]

        with allure.step(f"Пытаемся обновить фильм {movie_id} с price='сто рублей'"):
            api_manager_admin.films_api.patch_movie(movie_id, {"price": "сто рублей"}, expected_status=400)

    @allure.story("Частичное обновление фильма")
    @allure.title("PATCH с пустым телом")
    @allure.description("Проверяем, как сервер реагирует на PATCH с пустым телом.")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.skip(reason="БАГ: сервер возвращает 200 вместо 400")
    @pytest.mark.regression
    @pytest.mark.api
    def test_patch_movie_empty_body(self, api_manager_admin, create_film):
        """Негатив/Позитив: PATCH с пустым телом (должен вернуть 400)"""
        movie_id = create_film.json()["id"]

        with allure.step("Получаем текущие данные до PATCH"):
            get_before = api_manager_admin.films_api.get_movie(movie_id)
            original_name = get_before.json().get("name")
            original_price = get_before.json().get("price")

        with allure.step("Отправляем PATCH с пустым телом"):
            response = api_manager_admin.films_api.patch_movie(movie_id, {}, expected_status=400)

        if response.status_code == 200:
            with allure.step("Проверяем, что данные не изменились"):
                get_after = api_manager_admin.films_api.get_movie(movie_id)
                assert get_after.json().get("name") == original_name, "Имя изменилось без причины"
                assert get_after.json().get("price") == original_price, "Цена изменилась без причины"

    @allure.story("Частичное обновление фильма")
    @allure.title("PATCH с лишним полем")
    @allure.description("Проверяем, как сервер реагирует на лишние поля в PATCH запросе.")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.skip(reason="БАГ: сервер возвращает 404 вместо 400")
    @pytest.mark.regression
    @pytest.mark.api
    def test_patch_movie_extra_field(self, api_manager_admin, create_film):
        """Негатив/Позитив: PATCH с лишним полем (должен проигнорировать или вернуть ошибку)"""
        movie_id = create_film.json()["id"]

        patch_data = {
            "name": faker.sentence(nb_words=4),
            "extraField": "что-то лишнее",
            "anotherExtra": 12345
        }

        with allure.step(f"Отправляем PATCH с лишними полями extraField и anotherExtra"):
            response = api_manager_admin.films_api.patch_movie(movie_id, patch_data, expected_status=400)

        if response.status_code == 200:
            with allure.step("Проверяем, что лишние поля не добавились"):
                get_movie = api_manager_admin.films_api.get_movie(movie_id)
                assert get_movie.json().get("name") == patch_data["name"], "Имя не обновилось"
                assert get_movie.json().get("extraField") is None, "Добавилось лишнее поле"

    @allure.story("Частичное обновление фильма")
    @allure.title("PATCH только с лишним полем (без изменений)")
    @allure.description("Проверяем, как сервер реагирует на PATCH только с лишним полем.")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.skip(reason="БАГ: сервер возвращает 404 вместо 400")
    @pytest.mark.regression
    @pytest.mark.api
    def test_patch_movie_only_extra_field(self, api_manager_admin, create_film):
        """Негатив: PATCH только с лишним полем (без изменений)"""
        movie_id = create_film.json()["id"]

        with allure.step("Отправляем PATCH только с лишним полем extraField"):
            response = api_manager_admin.films_api.patch_movie(movie_id, {"extraField": "лишнее"}, expected_status=400)

        if response.status_code == 200:
            with allure.step("Проверяем, что лишнее поле не добавилось"):
                get_after = api_manager_admin.films_api.get_movie(movie_id)
                assert get_after.json().get("extraField") is None, "Добавилось лишнее поле"

    @allure.story("Частичное обновление фильма")
    @allure.title("PUT метод не поддерживается")
    @allure.description("Проверяем, что PUT метод не должен работать. Ожидаем 405.")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.skip(reason="БАГ: сервер возвращает 404 вместо 405")
    @pytest.mark.regression
    @pytest.mark.api
    def test_put_movie_not_allowed(self, api_manager_admin, create_film):
        """Негатив: PUT метод не должен работать (в документации его нет)"""
        movie_id = create_film.json()["id"]

        with allure.step(f"Отправляем PUT запрос на /movies/{movie_id}"):
            api_manager_admin.films_api.send_request("PUT", f"/movies/{movie_id}", data={"name": "new"},
                                                     expected_status=405)
