import allure
import pytest
from faker import Faker

faker = Faker('ru_RU')

@allure.epic("Управление отзывами на фильмы")
@allure.feature("Позитивные сценарии работы с отзывами")
class TestPositiveMoviesReviews:

    @allure.story("Получение отзывов")
    @allure.title("Получение отзывов без токена (PUBLIC ручка)")
    @allure.description("""
    Проверяем, что публичный эндпоинт /movies/{id}/reviews доступен без авторизации.
    Ожидаем: статус 200, список отзывов не пуст, каждый отзыв имеет структуру с полями:
    userId, rating, text, createdAt, user (с fullName).
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.regression
    @pytest.mark.api
    def test_get_movie_reviews_without_token(self, api_manager_admin, create_film_with_review, get_user_id):
        """Позитив: получение отзывов без токена (PUBLIC ручка)."""
        movie_id = create_film_with_review

        with allure.step(f"Отправляем GET запрос на /movies/{movie_id}/reviews без токена"):
            get_review = api_manager_admin.films_api.get_review(movie_id)
            reviews = get_review.json()

        with allure.step("Проверяем, что ответ — список и не пустой"):
            assert isinstance(reviews, list), "Ответ должен быть списком"
            assert len(reviews) > 0, "Список отзывов пуст"

        with allure.step("Проверяем структуру первого отзыва"):
            review = reviews[0]
            required_fields = ["userId", "rating", "text", "createdAt", "user"]
            for field in required_fields:
                assert field in review, f"У отзыва отсутствует поле {field}"

        with allure.step("Проверяем типы данных"):
            assert isinstance(review["userId"], str), "userId должен быть строкой"
            assert isinstance(review["rating"], int), "rating должен быть числом"
            assert isinstance(review["text"], str), "text должен быть строкой"
            assert isinstance(review["user"], dict), "user должен быть словарем"
            assert "fullName" in review["user"], "У user отсутствует поле fullName"
            assert isinstance(review["user"]["fullName"], str), "fullName должен быть строкой"

        with allure.step("Проверяем значения"):
            assert 1 <= review["rating"] <= 5, f"rating должен быть от 1 до 5, получено {review['rating']}"
            assert review["userId"] == get_user_id, "userId не совпадает"

    @allure.story("Получение отзывов")
    @allure.title("Получение отзывов с токеном")
    @allure.description("Проверяем, что авторизованный пользователь может получить отзывы на фильм.")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.regression
    @pytest.mark.api
    def test_get_movie_reviews_with_token(self, api_manager_admin, create_film_with_review, get_user_id):
        """Позитив: получение отзывов с токеном."""
        movie_id = create_film_with_review

        with allure.step(f"Отправляем GET запрос на /movies/{movie_id}/reviews с токеном"):
            get_review = api_manager_admin.films_api.get_review(movie_id)
            reviews = get_review.json()

        with allure.step("Проверяем, что ответ — список и не пустой"):
            assert isinstance(reviews, list), "Ответ должен быть списком"
            assert len(reviews) > 0, "Список отзывов пуст"

        with allure.step("Проверяем структуру первого отзыва"):
            review = reviews[0]
            required_fields = ["userId", "rating", "text", "createdAt", "user"]
            for field in required_fields:
                assert field in review, f"У отзыва отсутствует поле {field}"

        with allure.step("Проверяем типы данных"):
            assert isinstance(review["userId"], str), "userId должен быть строкой"
            assert isinstance(review["rating"], int), "rating должен быть числом"
            assert isinstance(review["text"], str), "text должен быть строкой"
            assert isinstance(review["user"], dict), "user должен быть словарем"
            assert "fullName" in review["user"], "У user отсутствует поле fullName"
            assert isinstance(review["user"]["fullName"], str), "fullName должен быть строкой"

        with allure.step("Проверяем значения"):
            assert 1 <= review["rating"] <= 5, f"rating должен быть от 1 до 5, получено {review['rating']}"
            assert review["userId"] == get_user_id, "userId не совпадает"

    @allure.story("Получение отзывов")
    @allure.title("Получение отзывов у фильма без отзывов (пустой список)")
    @allure.description("Проверяем, что у фильма без отзывов возвращается пустой список.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_get_movie_reviews_empty(self, api_manager_admin, create_film):
        """Позитив: получение отзывов у фильма без отзывов (пустой список)"""
        movie_id = create_film.json()["id"]

        with allure.step(f"Отправляем GET запрос на /movies/{movie_id}/reviews"):
            get_review = api_manager_admin.films_api.get_review(movie_id)
            reviews = get_review.json()

        with allure.step("Проверяем, что ответ — пустой список"):
            assert isinstance(reviews, list), "Ответ должен быть списком"
            assert len(reviews) == 0, f"Ожидался пустой список, получено {len(reviews)} отзывов"

    @allure.story("Создание отзыва")
    @allure.title("Успешное создание отзыва к фильму")
    @allure.description("""
    Проверяем создание отзыва через API.
    Шаги:
    1. Создаём отзыв (фикстура create_film_with_review уже создала)
    2. Получаем список отзывов
    3. Находим созданный отзыв по userId и проверяем данные
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.regression
    @pytest.mark.api
    def test_create_review(self, api_manager, create_film_with_review, review_data, get_user_id):
        """Позитив: создание отзыва к фильму."""
        movie_id = create_film_with_review

        with allure.step(f"Получаем список отзывов для фильма {movie_id}"):
            get_reviews = api_manager.films_api.get_review(movie_id)
            reviews = get_reviews.json()
            assert isinstance(reviews, list)
            assert len(reviews) > 0

        with allure.step("Находим созданный отзыв по userId и проверяем данные"):
            found = False
            for review in reviews:
                if review["userId"] == get_user_id:
                    assert review["rating"] == review_data["rating"]
                    assert review["text"] == review_data["text"]
                    found = True
                    break
            assert found, "Созданный отзыв не найден в списке"

    @allure.story("Редактирование отзыва")
    @allure.title("Успешное редактирование отзыва к фильму")
    @allure.description("""
    Проверяем редактирование отзыва через PUT запрос.
    Шаги:
    1. Редактируем отзыв (меняем rating и text)
    2. Проверяем структуру ответа
    3. Получаем список отзывов и проверяем, что данные изменились
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_edit_review(self, api_manager_admin, create_film_with_review, get_user_id):
        """Позитив: редактирование отзыва к фильму."""
        movie_id = create_film_with_review

        edit_data = {
            "rating": faker.random_int(min=1, max=5),
            "text": faker.sentence(nb_words=10)
        }

        with allure.step(f"Отправляем PUT запрос на /movies/{movie_id}/reviews для редактирования отзыва"):
            edit_review = api_manager_admin.films_api.put_review(movie_id, edit_data)
            data = edit_review.json()

        with allure.step("Проверяем структуру ответа"):
            required_fields = ["userId", "hidden", "text", "rating", "createdAt", "user"]
            for field in required_fields:
                assert field in data, f"У ответа отсутствует поле {field}"

        with allure.step("Проверяем типы данных в ответе"):
            assert isinstance(data["user"], dict)
            assert isinstance(data["userId"], str)
            assert isinstance(data["hidden"], bool)
            assert isinstance(data["text"], str)
            assert isinstance(data["rating"], int)
            assert isinstance(data["createdAt"], str)

        with allure.step("Проверяем значения в ответе"):
            assert data["userId"] == get_user_id
            assert data["hidden"] is False
            assert data["rating"] == edit_data["rating"]
            assert data["text"] == edit_data["text"]
            assert 1 <= data["rating"] <= 5

        with allure.step("Получаем список отзывов и проверяем, что данные изменились"):
            get_reviews = api_manager_admin.films_api.get_review(movie_id)
            reviews = get_reviews.json()
            assert isinstance(reviews, list)
            assert len(reviews) > 0

            found = False
            for review in reviews:
                if review["userId"] == get_user_id:
                    assert review["rating"] == edit_data["rating"], "rating не изменился"
                    assert review["text"] == edit_data["text"], "text не изменился"
                    found = True
                    break
            assert found, "Отзыв не найден после редактирования"

    @allure.story("Удаление отзыва")
    @allure.title("Успешное удаление отзыва к фильму")
    @allure.description("""
    Проверяем удаление отзыва через API.
    Шаги:
    1. Удаляем отзыв
    2. Проверяем структуру ответа
    3. Проверяем, что отзыв больше не出现在 списке
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.regression
    @pytest.mark.api
    def test_delete_review(self, api_manager_admin, create_film_with_review, get_user_id):
        """Позитив: удаление отзыва к фильму."""
        movie_id = create_film_with_review

        with allure.step(f"Отправляем DELETE запрос на /movies/{movie_id}/reviews для удаления отзыва"):
            delete_review = api_manager_admin.films_api.delete_review(movie_id)
            data = delete_review.json()

        with allure.step("Проверяем структуру ответа"):
            required_fields = ["userId", "rating", "text", "createdAt", "user"]
            for field in required_fields:
                assert field in data, f"У ответа отсутствует поле {field}"

        with allure.step("Проверяем типы данных в ответе"):
            assert isinstance(data["userId"], str), "userId должен быть строкой"
            assert isinstance(data["rating"], int), "rating должен быть числом"
            assert isinstance(data["text"], str), "text должен быть строкой"
            assert isinstance(data["user"], dict), "user должен быть словарем"
            assert "fullName" in data["user"], "У user отсутствует поле fullName"
            assert isinstance(data["user"]["fullName"], str), "fullName должен быть строкой"

        with allure.step("Проверяем, что userId совпадает"):
            assert data["userId"] == get_user_id, "userId не совпадает"

        with allure.step("Проверяем, что отзыв действительно удалился"):
            get_reviews = api_manager_admin.films_api.get_review(movie_id)
            reviews = get_reviews.json()
            assert isinstance(reviews, list), "Ответ должен быть списком"

            review_found = False
            for review in reviews:
                if review["userId"] == get_user_id:
                    review_found = True
                    break
            assert review_found is False, "Отзыв не был удалён"

    @allure.story("Скрытие отзыва")
    @allure.title("Успешное скрытие отзыва к фильму")
    @allure.description("""
    Проверяем скрытие отзыва (только для ADMIN/SUPER_ADMIN).
    Шаги:
    1. Скрываем отзыв
    2. Проверяем структуру ответа
    3. Редактируем отзыв и проверяем, что поле hidden = True
    4. Проверяем, что отзыв не удалился из фильма
    """)
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_hide_review(self, api_manager_admin, create_film_with_review, get_user_id):
        """Позитив: скрытие отзыва к фильму."""
        movie_id = create_film_with_review

        with allure.step(f"Отправляем POST запрос на скрытие отзыва /movies/{movie_id}/reviews/{get_user_id}/hide"):
            hide_review = api_manager_admin.films_api.hide_review(movie_id, get_user_id)
            data = hide_review.json()

        with allure.step("Проверяем структуру ответа на скрытие"):
            required_fields = ["userId", "rating", "text", "createdAt", "user"]
            for field in required_fields:
                assert field in data, f"У ответа отсутствует поле {field}"

        with allure.step("Проверяем типы данных"):
            assert isinstance(data["userId"], str), "userId должен быть строкой"
            assert isinstance(data["rating"], int), "rating должен быть числом"
            assert isinstance(data["text"], str), "text должен быть строкой"
            assert isinstance(data["user"], dict), "user должен быть словарем"
            assert "fullName" in data["user"], "У user отсутствует поле fullName"
            assert data["userId"] == get_user_id, "userId не совпадает"

        with allure.step("Редактируем отзыв и проверяем поле hidden = True"):
            edit_data = {
                "rating": faker.random_int(min=1, max=5),
                "text": faker.sentence(nb_words=15)
            }
            edit_review = api_manager_admin.films_api.put_review(movie_id, edit_data)
            edit_response = edit_review.json()
            assert "hidden" in edit_response, "Отсутствует поле hidden в ответе на редактирование"
            assert edit_response["hidden"] is True, f"hidden должен быть True, получено {edit_response['hidden']}"
            assert edit_response["rating"] == edit_data["rating"], "rating не совпадает"
            assert edit_response["text"] == edit_data["text"], "text не совпадает"
            assert edit_response["userId"] == get_user_id, "userId не совпадает"

        with allure.step("Проверяем, что отзыв не удалился (просто скрыт)"):
            get_movie = api_manager_admin.films_api.get_movie(movie_id)
            movie_data = get_movie.json()
            assert "reviews" in movie_data, "Отсутствует поле reviews"

            review_found = False
            for review in movie_data["reviews"]:
                if review["userId"] == get_user_id:
                    review_found = True
                    break
            assert review_found is True, "Отзыв удалился после скрытия (не должен был)"

    @allure.story("Скрытие отзыва")
    @allure.title("Повторное скрытие уже скрытого отзыва (идемпотентность)")
    @allure.description("Проверяем, что повторное скрытие уже скрытого отзыва возвращает 200.")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    @pytest.mark.api
    def test_hide_review_twice(self, api_manager_admin, create_film_with_review, get_user_id):
        """Позитив: повторное скрытие уже скрытого отзыва, идемпотентность."""
        movie_id = create_film_with_review

        with allure.step("Первое скрытие отзыва"):
            api_manager_admin.films_api.hide_review(movie_id, get_user_id)

        with allure.step("Второе скрытие отзыва (ожидаем 200)"):
            api_manager_admin.films_api.hide_review(movie_id, get_user_id, expected_status=200)

    @allure.story("Показ отзыва")
    @allure.title("Успешный показ скрытого отзыва к фильму")
    @allure.description("""
    Проверяем показ ранее скрытого отзыва.
    Шаги:
    1. Скрываем отзыв
    2. Показываем отзыв
    3. Редактируем отзыв и проверяем, что поле hidden = False
    4. Проверяем, что отзыв не удалился
    """)
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_show_review(self, api_manager_admin, create_film_with_review, get_user_id):
        """Позитив: показ скрытого отзыва к фильму."""
        movie_id = create_film_with_review

        with allure.step("Сначала скрываем отзыв"):
            api_manager_admin.films_api.hide_review(movie_id, get_user_id)

        with allure.step(f"Отправляем POST запрос на показ отзыва /movies/{movie_id}/reviews/{get_user_id}/show"):
            show_review = api_manager_admin.films_api.show_review(movie_id, get_user_id)
            data = show_review.json()

        with allure.step("Проверяем структуру ответа на показ"):
            required_fields = ["userId", "rating", "text", "createdAt", "user"]
            for field in required_fields:
                assert field in data, f"У ответа отсутствует поле {field}"

        with allure.step("Проверяем типы данных"):
            assert isinstance(data["userId"], str), "userId должен быть строкой"
            assert isinstance(data["rating"], int), "rating должен быть числом"
            assert isinstance(data["text"], str), "text должен быть строкой"
            assert isinstance(data["user"], dict), "user должен быть словарем"
            assert "fullName" in data["user"], "У user отсутствует поле fullName"
            assert data["userId"] == get_user_id, "userId не совпадает"

        with allure.step("Редактируем отзыв и проверяем поле hidden = False"):
            edit_data = {
                "rating": faker.random_int(min=1, max=5),
                "text": faker.sentence(nb_words=15)
            }
            edit_review = api_manager_admin.films_api.put_review(movie_id, edit_data)
            edit_response = edit_review.json()
            assert "hidden" in edit_response, "Отсутствует поле hidden в ответе на редактирование"
            assert edit_response[
                       "hidden"] is False, f"hidden должен быть False после показа, получено {edit_response['hidden']}"
            assert edit_response["rating"] == edit_data["rating"], "rating не совпадает"
            assert edit_response["text"] == edit_data["text"], "text не совпадает"
            assert edit_response["userId"] == get_user_id, "userId не совпадает"

        with allure.step("Проверяем, что отзыв не удалился"):
            get_movie = api_manager_admin.films_api.get_movie(movie_id)
            movie_data = get_movie.json()
            assert "reviews" in movie_data, "Отсутствует поле reviews"

            review_found = False
            for review in movie_data["reviews"]:
                if review["userId"] == get_user_id:
                    review_found = True
                    break
            assert review_found is True, "Отзыв удалился после показа (не должен был)"

    @allure.story("Показ отзыва")
    @allure.title("Повторный показ уже показанного отзыва (идемпотентность)")
    @allure.description("Проверяем, что повторный показ уже показанного отзыва возвращает 200.")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    @pytest.mark.api
    def test_show_review_twice(self, api_manager_admin, create_film_with_review, get_user_id):
        """Позитив: повторный показ уже показанного отзыва, идемпотентность."""
        movie_id = create_film_with_review

        with allure.step("Сначала скрываем, чтобы потом показать"):
            api_manager_admin.films_api.hide_review(movie_id, get_user_id)

        with allure.step("Первый показ отзыва"):
            api_manager_admin.films_api.show_review(movie_id, get_user_id)

        with allure.step("Второй показ отзыва (ожидаем 200)"):
            api_manager_admin.films_api.show_review(movie_id, get_user_id, expected_status=200)


@allure.epic("Управление отзывами на фильмы")
@allure.feature("Негативные сценарии работы с отзывами")
class TestNegativeMoviesReviews:

    # ========== ПОЛУЧЕНИЕ ОТЗЫВОВ ПО ФИЛЬМУ (негатив) ==========
    @allure.story("Получение отзывов")
    @allure.title("Ошибка при получении отзывов с несуществующим ID фильма")
    @allure.description("Проверяем, что при несуществующем ID фильма возвращается 404.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_get_movie_reviews_invalid_id(self, api_manager):
        """Негатив: получение отзывов с несуществующим ID фильма"""
        with allure.step("Пытаемся получить отзывы для фильма с ID 999999"):
            api_manager.films_api.get_review(999999, expected_status=404)

    @allure.story("Получение отзывов")
    @allure.title("Ошибка при получении отзывов с отрицательным ID фильма")
    @allure.description("Проверяем, что при отрицательном ID фильма возвращается 404.")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    @pytest.mark.api
    def test_get_movie_reviews_negative_id(self, api_manager):
        """Негатив: получение отзывов с отрицательным ID фильма"""
        with allure.step("Пытаемся получить отзывы для фильма с ID -1"):
            api_manager.films_api.get_review(-1, expected_status=404)

    @allure.story("Получение отзывов")
    @allure.title("Ошибка при получении отзывов с ID фильма = 0")
    @allure.description("Проверяем, что при ID фильма = 0 возвращается 404.")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    @pytest.mark.api
    def test_get_movie_reviews_zero_id(self, api_manager):
        """Негатив: получение отзывов с ID фильма = 0"""
        with allure.step("Пытаемся получить отзывы для фильма с ID 0"):
            api_manager.films_api.get_review(0, expected_status=404)

    @allure.story("Получение отзывов")
    @allure.title("Ошибка при получении отзывов с ID в виде строки")
    @allure.description("Проверяем, что при строковом ID фильма возвращается 404.")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.skip(reason="БАГ: сервер возвращает 500 вместо 404")
    @pytest.mark.regression
    @pytest.mark.api
    def test_get_movie_reviews_string_id(self, api_manager):
        """Негатив: получение отзывов с ID в виде строки"""
        with allure.step("Пытаемся получить отзывы для фильма с ID 'abc'"):
            api_manager.films_api.get_review("abc", expected_status=404)

    # ========== СОЗДАНИЕ ОТЗЫВА (негатив) ==========
    @allure.story("Создание отзыва")
    @allure.title("Создание отзыва без авторизации")
    @allure.description("Проверяем, что без токена нельзя создать отзыв. Ожидаем 401.")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_create_review_without_token(self, api_manager, create_film, review_data):
        """Негатив: создание отзыва без авторизации"""
        movie_id = create_film.json()["id"]

        with allure.step(f"Пытаемся создать отзыв для фильма {movie_id} без токена"):
            api_manager.films_api.create_review(movie_id, review_data, expected_status=401)

    @allure.story("Создание отзыва")
    @allure.title("Создание отзыва с неверным токеном")
    @allure.description("Проверяем, что с невалидным токеном нельзя создать отзыв. Ожидаем 401.")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_create_review_with_invalid_token(self, api_manager, create_film, review_data):
        """Негатив: создание отзыва с неверным токеном"""
        movie_id = create_film.json()["id"]

        with allure.step("Устанавливаем неверный токен"):
            api_manager.set_token("invalid_token")

        with allure.step(f"Пытаемся создать отзыв для фильма {movie_id}"):
            api_manager.films_api.create_review(movie_id, review_data, expected_status=401)

        with allure.step("Чистим токен"):
            api_manager.clear_token()

    @allure.story("Создание отзыва")
    @allure.title("Создание отзыва с несуществующим ID фильма")
    @allure.description("Проверяем, что при несуществующем ID фильма возвращается 404.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_create_review_invalid_movie_id(self, api_manager_admin, review_data):
        """Негатив: создание отзыва с несуществующим ID фильма"""
        with allure.step("Пытаемся создать отзыв для фильма с ID 999999"):
            api_manager_admin.films_api.create_review(999999, review_data, expected_status=404)

    @allure.story("Создание отзыва")
    @allure.title("Создание отзыва с отрицательным ID фильма")
    @allure.description("Проверяем, что при отрицательном ID фильма возвращается 404.")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    @pytest.mark.api
    def test_create_review_negative_movie_id(self, api_manager_admin, review_data):
        """Негатив: создание отзыва с отрицательным ID фильма"""
        with allure.step("Пытаемся создать отзыв для фильма с ID -1"):
            api_manager_admin.films_api.create_review(-1, review_data, expected_status=404)

    @allure.story("Создание отзыва")
    @allure.title("Создание отзыва с ID фильма = 0")
    @allure.description("Проверяем, что при ID фильма = 0 возвращается 404.")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    @pytest.mark.api
    def test_create_review_zero_movie_id(self, api_manager_admin, review_data):
        """Негатив: создание отзыва с ID фильма = 0"""
        with allure.step("Пытаемся создать отзыв для фильма с ID 0"):
            api_manager_admin.films_api.create_review(0, review_data, expected_status=404)

    @allure.story("Создание отзыва")
    @allure.title("Создание отзыва с ID фильма в виде строки")
    @allure.description("Проверяем, что при строковом ID фильма возвращается 404.")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.skip(reason="БАГ: сервер возвращает 500 вместо 404")
    @pytest.mark.regression
    @pytest.mark.api
    def test_create_review_string_movie_id(self, api_manager_admin, review_data):
        """Негатив: создание отзыва с ID фильма в виде строки"""
        with allure.step("Пытаемся создать отзыв для фильма с ID 'abc'"):
            api_manager_admin.films_api.create_review("abc", review_data, expected_status=404)

    @allure.story("Создание отзыва")
    @allure.title("Создание дублирующего отзыва")
    @allure.description("Проверяем, что нельзя создать второй отзыв на тот же фильм. Ожидаем 409.")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_create_review_duplicate(self, api_manager_admin, create_film, review_data):
        """Негатив: создание второго отзыва на тот же фильм (дубликат)"""
        movie_id = create_film.json()["id"]

        with allure.step("Создаём первый отзыв"):
            api_manager_admin.films_api.create_review(movie_id, review_data)

        with allure.step("Пытаемся создать второй отзыв (дубликат)"):
            api_manager_admin.films_api.create_review(movie_id, review_data, expected_status=409)

    @allure.story("Создание отзыва")
    @allure.title("Создание отзыва с rating = 0")
    @allure.description("Проверяем, что при rating = 0 возвращается 400.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.skip(reason="БАГ: сервер возвращает 201 вместо 400")
    @pytest.mark.regression
    @pytest.mark.api
    def test_create_review_rating_zero(self, api_manager_admin, create_film):
        """Негатив: создание отзыва с rating = 0"""
        movie_id = create_film.json()["id"]
        data = {"rating": 0, "text": "Норм фильм"}

        with allure.step(f"Пытаемся создать отзыв с rating=0 для фильма {movie_id}"):
            api_manager_admin.films_api.create_review(movie_id, data, expected_status=400)

    @allure.story("Создание отзыва")
    @allure.title("Создание отзыва с rating = 6")
    @allure.description("Проверяем, что при rating = 6 возвращается 400.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.skip(reason="БАГ: сервер возвращает 201 вместо 400")
    @pytest.mark.regression
    @pytest.mark.api
    def test_create_review_rating_six(self, api_manager_admin, create_film):
        """Негатив: создание отзыва с rating = 6"""
        movie_id = create_film.json()["id"]
        data = {"rating": 6, "text": "Норм фильм"}

        with allure.step(f"Пытаемся создать отзыв с rating=6 для фильма {movie_id}"):
            api_manager_admin.films_api.create_review(movie_id, data, expected_status=400)

    @allure.story("Создание отзыва")
    @allure.title("Создание отзыва с rating в виде строки")
    @allure.description("Проверяем, что при rating в виде строки возвращается 400.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_create_review_rating_string(self, api_manager_admin, create_film):
        """Негатив: создание отзыва с rating в виде строки"""
        movie_id = create_film.json()["id"]
        data = {"rating": "пять", "text": "Норм фильм"}

        with allure.step(f"Пытаемся создать отзыв с rating='пять' для фильма {movie_id}"):
            api_manager_admin.films_api.create_review(movie_id, data, expected_status=400)

    @allure.story("Создание отзыва")
    @allure.title("Создание отзыва с text в виде числа")
    @allure.description("Проверяем, что при text в виде числа возвращается 400.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_create_review_invalid_text_type(self, api_manager_admin, create_film):
        """Негатив: создание отзыва с text в виде числа (неверный тип)"""
        movie_id = create_film.json()["id"]
        data = {"rating": 5, "text": 123}

        with allure.step(f"Пытаемся создать отзыв с text=123 для фильма {movie_id}"):
            api_manager_admin.films_api.create_review(movie_id, data, expected_status=400)

    @allure.story("Создание отзыва")
    @allure.title("Создание отзыва с пустым text")
    @allure.description("Проверяем, что при пустом text возвращается 400.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.skip(reason="БАГ: сервер возвращает 201 вместо 400")
    @pytest.mark.regression
    @pytest.mark.api
    def test_create_review_empty_text(self, api_manager_admin, create_film):
        """Негатив: создание отзыва с пустым text"""
        movie_id = create_film.json()["id"]
        data = {"rating": 5, "text": ""}

        with allure.step(f"Пытаемся создать отзыв с пустым text для фильма {movie_id}"):
            api_manager_admin.films_api.create_review(movie_id, data, expected_status=400)

    @allure.story("Создание отзыва")
    @allure.title("Создание отзыва с пустым телом запроса")
    @allure.description("Проверяем, что при пустом теле запроса возвращается 400.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_create_review_empty_body(self, api_manager_admin, create_film):
        """Негатив: создание отзыва с пустым телом запроса"""
        movie_id = create_film.json()["id"]

        with allure.step(f"Пытаемся создать отзыв с пустым телом для фильма {movie_id}"):
            api_manager_admin.films_api.create_review(movie_id, {}, expected_status=400)

    @allure.story("Создание отзыва")
    @allure.title("Создание отзыва без поля rating")
    @allure.description("Проверяем, что при отсутствии поля rating возвращается 400.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_create_review_missing_rating(self, api_manager_admin, create_film):
        """Негатив: создание отзыва без поля rating"""
        movie_id = create_film.json()["id"]
        data = {"text": "Норм фильм"}

        with allure.step(f"Пытаемся создать отзыв без поля rating для фильма {movie_id}"):
            api_manager_admin.films_api.create_review(movie_id, data, expected_status=400)

    @allure.story("Создание отзыва")
    @allure.title("Создание отзыва без поля text")
    @allure.description("Проверяем, что при отсутствии поля text возвращается 400.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.skip(reason="БАГ или ФИЧА???: сервер возвращает 201 вместо 400")
    @pytest.mark.regression
    @pytest.mark.api
    def test_create_review_missing_text(self, api_manager_admin, create_film):
        """Негатив: создание отзыва без поля text"""
        movie_id = create_film.json()["id"]
        data = {"rating": 5}

        with allure.step(f"Пытаемся создать отзыв без поля text для фильма {movie_id}"):
            api_manager_admin.films_api.create_review(movie_id, data, expected_status=400)

    @allure.story("Создание отзыва")
    @allure.title("Создание отзыва с лишними полями")
    @allure.description("Проверяем, как сервер реагирует на лишние поля в запросе.")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.skip(reason="БАГ: при отправке лишних полей сервер возвращает 404 вместо 400")
    @pytest.mark.regression
    @pytest.mark.api
    def test_create_review_extra_field(self, api_manager_admin, create_film):
        """Негатив: создание отзыва с лишними полями"""
        movie_id = create_film.json()["id"]
        review_data_with_extra = {
            "rating": 5,
            "text": faker.sentence(nb_words=10),
            "extraField": "что-то лишнее",
            "anotherExtra": 12345
        }

        with allure.step(f"Пытаемся создать отзыв с лишними полями для фильма {movie_id}"):
            api_manager_admin.films_api.create_review(movie_id, review_data_with_extra, expected_status=400)

    # ========== РЕДАКТИРОВАНИЕ ОТЗЫВА (негатив) ==========
    @allure.story("Редактирование отзыва")
    @allure.title("Редактирование отзыва без авторизации")
    @allure.description("Проверяем, что без токена нельзя редактировать отзыв. Ожидаем 401.")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_edit_review_without_token(self, api_manager, create_film_with_review):
        """Негатив: редактирование отзыва без авторизации"""
        movie_id = create_film_with_review
        edit_data = {"rating": 5, "text": "Новый текст"}

        with allure.step(f"Пытаемся редактировать отзыв для фильма {movie_id} без токена"):
            api_manager.films_api.put_review(movie_id, edit_data, expected_status=401)

    @allure.story("Редактирование отзыва")
    @allure.title("Редактирование отзыва с неверным токеном")
    @allure.description("Проверяем, что с невалидным токеном нельзя редактировать отзыв. Ожидаем 401.")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_edit_review_with_invalid_token(self, api_manager, create_film_with_review):
        """Негатив: редактирование отзыва с неверным токеном"""
        movie_id = create_film_with_review
        edit_data = {"rating": 5, "text": "Новый текст"}

        with allure.step("Устанавливаем неверный токен"):
            api_manager.set_token("invalid_token")

        with allure.step(f"Пытаемся редактировать отзыв для фильма {movie_id}"):
            api_manager.films_api.put_review(movie_id, edit_data, expected_status=401)

        with allure.step("Чистим токен"):
            api_manager.clear_token()

    @allure.story("Редактирование отзыва")
    @allure.title("Редактирование отзыва с несуществующим ID фильма")
    @allure.description("Проверяем, что при несуществующем ID фильма возвращается 404.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_edit_review_invalid_movie_id(self, api_manager_admin):
        """Негатив: редактирование отзыва с несуществующим ID фильма"""
        edit_data = {"rating": 5, "text": "Новый текст"}

        with allure.step("Пытаемся редактировать отзыв для фильма с ID 999999"):
            api_manager_admin.films_api.put_review(999999, edit_data, expected_status=404)

    @allure.story("Редактирование отзыва")
    @allure.title("Редактирование отзыва с отрицательным ID фильма")
    @allure.description("Проверяем, что при отрицательном ID фильма возвращается 404.")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    @pytest.mark.api
    def test_edit_review_negative_movie_id(self, api_manager_admin):
        """Негатив: редактирование отзыва с отрицательным ID фильма"""
        edit_data = {"rating": 5, "text": "Новый текст"}

        with allure.step("Пытаемся редактировать отзыв для фильма с ID -1"):
            api_manager_admin.films_api.put_review(-1, edit_data, expected_status=404)

    @allure.story("Редактирование отзыва")
    @allure.title("Редактирование отзыва с ID фильма = 0")
    @allure.description("Проверяем, что при ID фильма = 0 возвращается 404.")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    @pytest.mark.api
    def test_edit_review_zero_movie_id(self, api_manager_admin):
        """Негатив: редактирование отзыва с ID фильма = 0"""
        edit_data = {"rating": 5, "text": "Новый текст"}

        with allure.step("Пытаемся редактировать отзыв для фильма с ID 0"):
            api_manager_admin.films_api.put_review(0, edit_data, expected_status=404)

    @allure.story("Редактирование отзыва")
    @allure.title("Редактирование отзыва с rating = 0")
    @allure.description("Проверяем, что при rating = 0 возвращается 400.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.skip(reason="БАГ: сервер возвращает 200 вместо 400")
    @pytest.mark.regression
    @pytest.mark.api
    def test_edit_review_rating_zero(self, api_manager_admin, create_film_with_review):
        """Негатив: редактирование отзыва с rating = 0"""
        movie_id = create_film_with_review
        edit_data = {"rating": 0, "text": "Новый текст"}

        with allure.step(f"Пытаемся редактировать отзыв с rating=0 для фильма {movie_id}"):
            api_manager_admin.films_api.put_review(movie_id, edit_data, expected_status=400)

    @allure.story("Редактирование отзыва")
    @allure.title("Редактирование отзыва с rating = 6")
    @allure.description("Проверяем, что при rating = 6 возвращается 400.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.skip(reason="БАГ: сервер возвращает 200 вместо 400")
    @pytest.mark.regression
    @pytest.mark.api
    def test_edit_review_rating_six(self, api_manager_admin, create_film_with_review):
        """Негатив: редактирование отзыва с rating = 6"""
        movie_id = create_film_with_review
        edit_data = {"rating": 6, "text": "Новый текст"}

        with allure.step(f"Пытаемся редактировать отзыв с rating=6 для фильма {movie_id}"):
            api_manager_admin.films_api.put_review(movie_id, edit_data, expected_status=400)

    @allure.story("Редактирование отзыва")
    @allure.title("Редактирование отзыва с rating в виде строки")
    @allure.description("Проверяем, что при rating в виде строки возвращается 400.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_edit_review_rating_string(self, api_manager_admin, create_film_with_review):
        """Негатив: редактирование отзыва с rating в виде строки"""
        movie_id = create_film_with_review
        edit_data = {"rating": "пять", "text": "Новый текст"}

        with allure.step(f"Пытаемся редактировать отзыв с rating='пять' для фильма {movie_id}"):
            api_manager_admin.films_api.put_review(movie_id, edit_data, expected_status=400)

    @allure.story("Редактирование отзыва")
    @allure.title("Редактирование отзыва с text в виде числа")
    @allure.description("Проверяем, что при text в виде числа возвращается 400.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_edit_review_invalid_text_type(self, api_manager_admin, create_film_with_review):
        """Негатив: редактирование отзыва с text в виде числа (неверный тип)"""
        movie_id = create_film_with_review
        edit_data = {"rating": 5, "text": 123}

        with allure.step(f"Пытаемся редактировать отзыв с text=123 для фильма {movie_id}"):
            api_manager_admin.films_api.put_review(movie_id, edit_data, expected_status=400)

    @allure.story("Редактирование отзыва")
    @allure.title("Редактирование отзыва с пустым text")
    @allure.description("Проверяем, что при пустом text возвращается 400.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.skip(reason="БАГ: сервер возвращает 200 вместо 400")
    @pytest.mark.regression
    @pytest.mark.api
    def test_edit_review_empty_text(self, api_manager_admin, create_film_with_review):
        """Негатив: редактирование отзыва с пустым text"""
        movie_id = create_film_with_review
        edit_data = {"rating": 5, "text": ""}

        with allure.step(f"Пытаемся редактировать отзыв с пустым text для фильма {movie_id}"):
            api_manager_admin.films_api.put_review(movie_id, edit_data, expected_status=400)

    @allure.story("Редактирование отзыва")
    @allure.title("Редактирование отзыва с пустым телом запроса")
    @allure.description("Проверяем, что при пустом теле запроса возвращается 400.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_edit_review_empty_body(self, api_manager_admin, create_film_with_review):
        """Негатив: редактирование отзыва с пустым телом запроса"""
        movie_id = create_film_with_review

        with allure.step(f"Пытаемся редактировать отзыв с пустым телом для фильма {movie_id}"):
            api_manager_admin.films_api.put_review(movie_id, {}, expected_status=400)

    @allure.story("Редактирование отзыва")
    @allure.title("Редактирование отзыва без поля rating")
    @allure.description("Проверяем, что при отсутствии поля rating возвращается 400.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_edit_review_missing_rating(self, api_manager_admin, create_film_with_review):
        """Негатив: редактирование отзыва без поля rating"""
        movie_id = create_film_with_review
        edit_data = {"text": "Новый текст"}

        with allure.step(f"Пытаемся редактировать отзыв без поля rating для фильма {movie_id}"):
            api_manager_admin.films_api.put_review(movie_id, edit_data, expected_status=400)

    @allure.story("Редактирование отзыва")
    @allure.title("Редактирование отзыва без поля text")
    @allure.description("Проверяем, что при отсутствии поля text возвращается 400.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_edit_review_missing_text(self, api_manager_admin, create_film_with_review):
        """Негатив: редактирование отзыва без поля text"""
        movie_id = create_film_with_review
        edit_data = {"rating": 5}

        with allure.step(f"Пытаемся редактировать отзыв без поля text для фильма {movie_id}"):
            api_manager_admin.films_api.put_review(movie_id, edit_data, expected_status=400)

    @allure.story("Редактирование отзыва")
    @allure.title("Редактирование отзыва с лишними полями")
    @allure.description("Проверяем, как сервер реагирует на лишние поля в PUT запросе.")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.skip(reason="БАГ: при отправке лишних полей сервер возвращает 404 вместо 400")
    @pytest.mark.regression
    @pytest.mark.api
    def test_edit_review_extra_field(self, api_manager_admin, create_film_with_review):
        """Негатив: редактирование отзыва с лишними полями"""
        movie_id = create_film_with_review
        edit_data_with_extra = {
            "rating": 5,
            "text": faker.sentence(nb_words=10),
            "extraField": "что-то лишнее",
            "anotherExtra": 12345
        }

        with allure.step(f"Пытаемся редактировать отзыв с лишними полями для фильма {movie_id}"):
            api_manager_admin.films_api.put_review(movie_id, edit_data_with_extra, expected_status=400)

    # ========== УДАЛЕНИЕ ОТЗЫВА (негатив) ==========
    # Параметр userId в Swagger — либо ошибка документации, либо пережиток прошлого.
    # На работу ручки не влияет. Инфа о юзере берется из токена. Поэтому не проверяем.
    @allure.story("Удаление отзыва")
    @allure.title("Удаление отзыва без авторизации")
    @allure.description("Проверяем, что без токена нельзя удалить отзыв. Ожидаем 401.")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_delete_review_without_token(self, api_manager, create_film_with_review):
        """Негатив: удаление отзыва без авторизации"""
        movie_id = create_film_with_review

        with allure.step(f"Пытаемся удалить отзыв для фильма {movie_id} без токена"):
            api_manager.films_api.delete_review(movie_id, expected_status=401)

    @allure.story("Удаление отзыва")
    @allure.title("Удаление отзыва с неверным токеном")
    @allure.description("Проверяем, что с невалидным токеном нельзя удалить отзыв. Ожидаем 401.")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_delete_review_with_invalid_token(self, api_manager, create_film_with_review):
        """Негатив: удаление отзыва с неверным токеном"""
        movie_id = create_film_with_review

        with allure.step("Устанавливаем неверный токен"):
            api_manager.set_token("invalid_token")

        with allure.step(f"Пытаемся удалить отзыв для фильма {movie_id}"):
            api_manager.films_api.delete_review(movie_id, expected_status=401)

        with allure.step("Чистим токен"):
            api_manager.clear_token()

    @allure.story("Удаление отзыва")
    @allure.title("Удаление отзыва с несуществующим ID фильма")
    @allure.description("Проверяем, что при несуществующем ID фильма возвращается 404.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_delete_review_invalid_movie_id(self, api_manager_admin):
        """Негатив: удаление отзыва с несуществующим ID фильма"""
        with allure.step("Пытаемся удалить отзыв для фильма с ID 999999"):
            api_manager_admin.films_api.delete_review(999999, expected_status=404)

    @allure.story("Удаление отзыва")
    @allure.title("Удаление отзыва с отрицательным ID фильма")
    @allure.description("Проверяем, что при отрицательном ID фильма возвращается 404.")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    @pytest.mark.api
    def test_delete_review_negative_movie_id(self, api_manager_admin):
        """Негатив: удаление отзыва с отрицательным ID фильма"""
        with allure.step("Пытаемся удалить отзыв для фильма с ID -1"):
            api_manager_admin.films_api.delete_review(-1, expected_status=404)

    @allure.story("Удаление отзыва")
    @allure.title("Удаление отзыва с ID фильма = 0")
    @allure.description("Проверяем, что при ID фильма = 0 возвращается 404.")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    @pytest.mark.api
    def test_delete_review_zero_movie_id(self, api_manager_admin):
        """Негатив: удаление отзыва с ID фильма = 0"""
        with allure.step("Пытаемся удалить отзыв для фильма с ID 0"):
            api_manager_admin.films_api.delete_review(0, expected_status=404)

    @allure.story("Удаление отзыва")
    @allure.title("Повторное удаление уже удалённого отзыва")
    @allure.description("Проверяем, что при повторном удалении возвращается 404.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_delete_review_twice(self, api_manager_admin, create_film_with_review):
        """Негатив: повторное удаление уже удалённого отзыва"""
        movie_id = create_film_with_review

        with allure.step("Первое удаление отзыва"):
            api_manager_admin.films_api.delete_review(movie_id)

        with allure.step("Пытаемся удалить отзыв повторно"):
            api_manager_admin.films_api.delete_review(movie_id, expected_status=404)

    @allure.story("Удаление отзыва")
    @allure.title("Удаление отзыва у фильма без отзыва")
    @allure.description("Проверяем, что при удалении отзыва у фильма без отзыва возвращается 404.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_delete_review_no_review(self, api_manager_admin, create_film):
        """Негатив: удаление отзыва у фильма, у которого нет отзыва"""
        movie_id = create_film.json()["id"]

        with allure.step(f"Пытаемся удалить отзыв у фильма {movie_id}, у которого нет отзыва"):
            api_manager_admin.films_api.delete_review(movie_id, expected_status=404)

    # ========== СКРЫТИЕ ОТЗЫВА (негатив) ==========
    @allure.story("Скрытие отзыва")
    @allure.title("Скрытие отзыва без авторизации (только ADMIN/SUPER_ADMIN)")
    @allure.description("Проверяем, что без токена нельзя скрыть отзыв. Ожидаем 401.")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_hide_review_without_token(self, api_manager, create_film_with_review, get_user_id):
        """Негатив: скрытие отзыва без авторизации (только ADMIN/SUPER_ADMIN)"""
        movie_id = create_film_with_review

        with allure.step(f"Пытаемся скрыть отзыв для фильма {movie_id} без токена"):
            api_manager.films_api.hide_review(movie_id, get_user_id, expected_status=401)

    @allure.story("Скрытие отзыва")
    @allure.title("Скрытие отзыва с неверным токеном")
    @allure.description("Проверяем, что с невалидным токеном нельзя скрыть отзыв. Ожидаем 401.")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_hide_review_with_invalid_token(self, api_manager, create_film_with_review, get_user_id):
        """Негатив: скрытие отзыва с неверным токеном"""
        movie_id = create_film_with_review

        with allure.step("Устанавливаем неверный токен"):
            api_manager.set_token("invalid_token")

        with allure.step(f"Пытаемся скрыть отзыв для фильма {movie_id}"):
            api_manager.films_api.hide_review(movie_id, get_user_id, expected_status=401)

        with allure.step("Чистим токен"):
            api_manager.clear_token()

    @allure.story("Скрытие отзыва")
    @allure.title("Скрытие отзыва с несуществующим ID фильма")
    @allure.description("Проверяем, что при несуществующем ID фильма возвращается 404.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_hide_review_invalid_movie_id(self, api_manager_admin, get_user_id):
        """Негатив: скрытие отзыва с несуществующим ID фильма"""
        with allure.step("Пытаемся скрыть отзыв для фильма с ID 999999"):
            api_manager_admin.films_api.hide_review(999999, get_user_id, expected_status=404)

    @allure.story("Скрытие отзыва")
    @allure.title("Скрытие отзыва с отрицательным ID фильма")
    @allure.description("Проверяем, что при отрицательном ID фильма возвращается 404.")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    @pytest.mark.api
    def test_hide_review_negative_movie_id(self, api_manager_admin, get_user_id):
        """Негатив: скрытие отзыва с отрицательным ID фильма"""
        with allure.step("Пытаемся скрыть отзыв для фильма с ID -1"):
            api_manager_admin.films_api.hide_review(-1, get_user_id, expected_status=404)

    @allure.story("Скрытие отзыва")
    @allure.title("Скрытие отзыва с ID фильма = 0")
    @allure.description("Проверяем, что при ID фильма = 0 возвращается 404.")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    @pytest.mark.api
    def test_hide_review_zero_movie_id(self, api_manager_admin, get_user_id):
        """Негатив: скрытие отзыва с ID фильма = 0"""
        with allure.step("Пытаемся скрыть отзыв для фильма с ID 0"):
            api_manager_admin.films_api.hide_review(0, get_user_id, expected_status=404)

    @allure.story("Скрытие отзыва")
    @allure.title("Скрытие отзыва с несуществующим userId")
    @allure.description("Проверяем, что при несуществующем userId возвращается 404.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_hide_review_invalid_user_id(self, api_manager_admin, create_film_with_review):
        """Негатив: скрытие отзыва с несуществующим userId"""
        movie_id = create_film_with_review
        invalid_user_id = "00000000-0000-0000-0000-000000000000"

        with allure.step(f"Пытаемся скрыть отзыв с userId={invalid_user_id} для фильма {movie_id}"):
            api_manager_admin.films_api.hide_review(movie_id, invalid_user_id, expected_status=404)

    @allure.story("Скрытие отзыва")
    @allure.title("Скрытие отзыва с неверным форматом userId")
    @allure.description("Проверяем, что при неверном формате userId возвращается 404.")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    @pytest.mark.api
    def test_hide_review_invalid_user_id_format(self, api_manager_admin, create_film_with_review):
        """Негатив: скрытие отзыва с неверным форматом userId (не UUID)"""
        movie_id = create_film_with_review
        invalid_user_id = "not_a_uuid"

        with allure.step(f"Пытаемся скрыть отзыв с userId='{invalid_user_id}' для фильма {movie_id}"):
            api_manager_admin.films_api.hide_review(movie_id, invalid_user_id, expected_status=404)

    @allure.story("Скрытие отзыва")
    @allure.title("Скрытие отзыва у фильма без отзыва")
    @allure.description("Проверяем, что при скрытии отзыва у фильма без отзыва возвращается 404.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_hide_review_no_review(self, api_manager_admin, create_film, get_user_id):
        """Негатив: скрытие отзыва у фильма, у которого нет отзыва"""
        movie_id = create_film.json()["id"]

        with allure.step(f"Пытаемся скрыть отзыв у фильма {movie_id}, у которого нет отзыва"):
            api_manager_admin.films_api.hide_review(movie_id, get_user_id, expected_status=404)

    # ========== ПОКАЗ ОТЗЫВА (негатив) ==========
    @allure.story("Показ отзыва")
    @allure.title("Показ отзыва без авторизации (только ADMIN/SUPER_ADMIN)")
    @allure.description("Проверяем, что без токена нельзя показать отзыв. Ожидаем 401.")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_show_review_without_token(self, api_manager, create_film_with_review, get_user_id):
        """Негатив: показ отзыва без авторизации (только ADMIN/SUPER_ADMIN)"""
        movie_id = create_film_with_review

        with allure.step(f"Пытаемся показать отзыв для фильма {movie_id} без токена"):
            api_manager.films_api.show_review(movie_id, get_user_id, expected_status=401)

    @allure.story("Показ отзыва")
    @allure.title("Показ отзыва с неверным токеном")
    @allure.description("Проверяем, что с невалидным токеном нельзя показать отзыв. Ожидаем 401.")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_show_review_with_invalid_token(self, api_manager, create_film_with_review, get_user_id):
        """Негатив: показ отзыва с неверным токеном"""
        movie_id = create_film_with_review

        with allure.step("Устанавливаем неверный токен"):
            api_manager.set_token("invalid_token")

        with allure.step(f"Пытаемся показать отзыв для фильма {movie_id}"):
            api_manager.films_api.show_review(movie_id, get_user_id, expected_status=401)

        with allure.step("Чистим токен"):
            api_manager.clear_token()

    @allure.story("Показ отзыва")
    @allure.title("Показ отзыва с несуществующим ID фильма")
    @allure.description("Проверяем, что при несуществующем ID фильма возвращается 404.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_show_review_invalid_movie_id(self, api_manager_admin, get_user_id):
        """Негатив: показ отзыва с несуществующим ID фильма"""
        with allure.step("Пытаемся показать отзыв для фильма с ID 999999"):
            api_manager_admin.films_api.show_review(999999, get_user_id, expected_status=404)

    @allure.story("Показ отзыва")
    @allure.title("Показ отзыва с отрицательным ID фильма")
    @allure.description("Проверяем, что при отрицательном ID фильма возвращается 404.")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    @pytest.mark.api
    def test_show_review_negative_movie_id(self, api_manager_admin, get_user_id):
        """Негатив: показ отзыва с отрицательным ID фильма"""
        with allure.step("Пытаемся показать отзыв для фильма с ID -1"):
            api_manager_admin.films_api.show_review(-1, get_user_id, expected_status=404)

    @allure.story("Показ отзыва")
    @allure.title("Показ отзыва с ID фильма = 0")
    @allure.description("Проверяем, что при ID фильма = 0 возвращается 404.")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    @pytest.mark.api
    def test_show_review_zero_movie_id(self, api_manager_admin, get_user_id):
        """Негатив: показ отзыва с ID фильма = 0"""
        with allure.step("Пытаемся показать отзыв для фильма с ID 0"):
            api_manager_admin.films_api.show_review(0, get_user_id, expected_status=404)

    @allure.story("Показ отзыва")
    @allure.title("Показ отзыва с несуществующим userId")
    @allure.description("Проверяем, что при несуществующем userId возвращается 404.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_show_review_invalid_user_id(self, api_manager_admin, create_film_with_review):
        """Негатив: показ отзыва с несуществующим userId"""
        movie_id = create_film_with_review
        invalid_user_id = "00000000-0000-0000-0000-000000000000"

        with allure.step(f"Пытаемся показать отзыв с userId={invalid_user_id} для фильма {movie_id}"):
            api_manager_admin.films_api.show_review(movie_id, invalid_user_id, expected_status=404)

    @allure.story("Показ отзыва")
    @allure.title("Показ отзыва с неверным форматом userId")
    @allure.description("Проверяем, что при неверном формате userId возвращается 404.")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    @pytest.mark.api
    def test_show_review_invalid_user_id_format(self, api_manager_admin, create_film_with_review):
        """Негатив: показ отзыва с неверным форматом userId (не UUID)"""
        movie_id = create_film_with_review
        invalid_user_id = "not_a_uuid"

        with allure.step(f"Пытаемся показать отзыв с userId='{invalid_user_id}' для фильма {movie_id}"):
            api_manager_admin.films_api.show_review(movie_id, invalid_user_id, expected_status=404)

    @allure.story("Показ отзыва")
    @allure.title("Показ отзыва у фильма без отзыва")
    @allure.description("Проверяем, что при показе отзыва у фильма без отзыва возвращается 404.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_show_review_no_review(self, api_manager_admin, create_film, get_user_id):
        """Негатив: показ отзыва у фильма, у которого нет отзыва"""
        movie_id = create_film.json()["id"]

        with allure.step(f"Пытаемся показать отзыв у фильма {movie_id}, у которого нет отзыва"):
            api_manager_admin.films_api.show_review(movie_id, get_user_id, expected_status=404)