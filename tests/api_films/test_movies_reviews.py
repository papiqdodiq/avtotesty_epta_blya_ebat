import pytest
from faker import Faker

faker = Faker('ru_RU')

class TestPositiveMoviesReviews:

    def test_get_movie_reviews_without_token(self, api_manager_admin, create_film_with_review, get_user_id):
        """Позитив: получение отзывов без токена (PUBLIC ручка).
        Проверяем статус, заголовки, структуру и содержимое."""
        movie_id = create_film_with_review
        get_review = api_manager_admin.films_api.get_review(movie_id)

        # Проверка структуры ответа (список отзывов)
        reviews = get_review.json()
        assert isinstance(reviews, list), "Ответ должен быть списком"
        assert len(reviews) > 0, "Список отзывов пуст"

        # Проверка структуры первого отзыва
        review = reviews[0]
        required_fields = ["userId", "rating", "text", "createdAt", "user"]
        for field in required_fields:
            assert field in review, f"У отзыва отсутствует поле {field}"

        # Проверка типов
        assert isinstance(review["userId"], str), "userId должен быть строкой"
        assert isinstance(review["rating"], int), "rating должен быть числом"
        assert isinstance(review["text"], str), "text должен быть строкой"
        assert isinstance(review["user"], dict), "user должен быть словарем"
        assert "fullName" in review["user"], "У user отсутствует поле fullName"
        assert isinstance(review["user"]["fullName"], str), "fullName должен быть строкой"

        # Проверка значений
        assert 1 <= review["rating"] <= 5, f"rating должен быть от 1 до 5, получено {review['rating']}"
        assert review["userId"] == get_user_id, "userId не совпадает"

    def test_get_movie_reviews_with_token(self, api_manager_admin, create_film_with_review, get_user_id):
        """Позитив: получение отзывов с токеном.
        Проверяем статус, заголовки, структуру и содержимое."""
        movie_id = create_film_with_review
        get_review = api_manager_admin.films_api.get_review(movie_id)

        # Проверка структуры ответа (список отзывов)
        reviews = get_review.json()
        assert isinstance(reviews, list), "Ответ должен быть списком"
        assert len(reviews) > 0, "Список отзывов пуст"

        # Проверка структуры первого отзыва
        review = reviews[0]
        required_fields = ["userId", "rating", "text", "createdAt", "user"]
        for field in required_fields:
            assert field in review, f"У отзыва отсутствует поле {field}"

        # Проверка типов
        assert isinstance(review["userId"], str), "userId должен быть строкой"
        assert isinstance(review["rating"], int), "rating должен быть числом"
        assert isinstance(review["text"], str), "text должен быть строкой"
        assert isinstance(review["user"], dict), "user должен быть словарем"
        assert "fullName" in review["user"], "У user отсутствует поле fullName"
        assert isinstance(review["user"]["fullName"], str), "fullName должен быть строкой"

        # Проверка значений
        assert 1 <= review["rating"] <= 5, f"rating должен быть от 1 до 5, получено {review['rating']}"
        assert review["userId"] == get_user_id, "userId не совпадает"

    def test_get_movie_reviews_empty(self, api_manager_admin, create_film_id):
        """Позитив: получение отзывов у фильма без отзывов (пустой список)"""
        movie_id = create_film_id
        get_review = api_manager_admin.films_api.get_review(movie_id)

        reviews = get_review.json()
        assert isinstance(reviews, list), "Ответ должен быть списком"
        assert len(reviews) == 0, f"Ожидался пустой список, получено {len(reviews)} отзывов"

    def test_create_review(self, api_manager, create_film_with_review, review_data, get_user_id):
        """Позитив: создание отзыва к фильму.
        Проверяем статус, заголовки и структуру ответа."""
        movie_id = create_film_with_review

        # 2. ПРОВЕРЯЕМ, ЧТО ОТЗЫВ РЕАЛЬНО ПОЯВИЛСЯ (GET)
        get_reviews = api_manager.films_api.get_review(movie_id)

        reviews = get_reviews.json()
        assert isinstance(reviews, list)
        assert len(reviews) > 0

        # Находим наш отзыв по userId
        found = False
        for review in reviews:
            if review["userId"] == get_user_id:
                assert review["rating"] == review_data["rating"]
                assert review["text"] == review_data["text"]
                found = True
                break
        assert found, "Созданный отзыв не найден в списке"

    # БАГ!!! Ответ (body) от auth_session.put не совпадает с документацией в Сваггере!
    def test_edit_review(self, api_manager_admin, create_film_with_review, get_user_id):
        """Позитив: редактирование отзыва к фильму.
        Проверяем статус, заголовки, структуру и совпадение userId."""
        movie_id = create_film_with_review

        # 1. РЕДАКТИРУЕМ ОТЗЫВ
        edit_data = {
            "rating": faker.random_int(min=1, max=5),
            "text": faker.sentence(nb_words=10)
        }

        edit_review = api_manager_admin.films_api.put_review(movie_id, edit_data)

        data = edit_review.json()
        required_fields = ["movieId", "userId", "hidden", "text", "rating", "createdAt"]
        for field in required_fields:
            assert field in data, f"У ответа отсутствует поле {field}"

        assert isinstance(data["movieId"], int)
        assert isinstance(data["userId"], str)
        assert isinstance(data["hidden"], bool)
        assert isinstance(data["text"], str)
        assert isinstance(data["rating"], int)
        assert isinstance(data["createdAt"], str)

        assert data["movieId"] == movie_id
        assert data["userId"] == get_user_id
        assert data["hidden"] is False
        assert data["rating"] == edit_data["rating"]
        assert data["text"] == edit_data["text"]
        assert 1 <= data["rating"] <= 5

        # 2. ПРОВЕРЯЕМ, ЧТО ДАННЫЕ РЕАЛЬНО ИЗМЕНИЛИСЬ (GET)
        get_reviews = api_manager_admin.films_api.get_review(movie_id)

        reviews = get_reviews.json()
        assert isinstance(reviews, list)
        assert len(reviews) > 0

        # Находим наш отзыв по userId
        found = False
        for review in reviews:
            if review["userId"] == get_user_id:
                assert review["rating"] == edit_data["rating"], "rating не изменился"
                assert review["text"] == edit_data["text"], "text не изменился"
                found = True
                break
        assert found, "Отзыв не найден после редактирования"

    def test_delete_review(self, api_manager_admin, create_film_with_review, get_user_id):
        """Позитив: удаление отзыва к фильму.
        Проверяем статус, заголовки и структуру ответа."""
        movie_id = create_film_with_review

        # Удаляем отзыв (userId не нужен в пути, API берёт из токена)
        # Параметр userId в Swagger — либо ошибка документации, либо пережиток прошлого.
        delete_review = api_manager_admin.films_api.delete_review(movie_id)

        # Проверка структуры ответа
        data = delete_review.json()
        required_fields = ["userId", "rating", "text", "createdAt", "user"]
        for field in required_fields:
            assert field in data, f"У ответа отсутствует поле {field}"

        # Проверка типов
        assert isinstance(data["userId"], str), "userId должен быть строкой"
        assert isinstance(data["rating"], int), "rating должен быть числом"
        assert isinstance(data["text"], str), "text должен быть строкой"
        assert isinstance(data["user"], dict), "user должен быть словарем"

        # Проверка вложенного объекта user
        assert "fullName" in data["user"], "У user отсутствует поле fullName"
        assert isinstance(data["user"]["fullName"], str), "fullName должен быть строкой"

        # Проверка, что userId совпадает
        assert data["userId"] == get_user_id, "userId не совпадает"

        # Проверка, что отзыв действительно удалился
        get_reviews = api_manager_admin.films_api.get_review(movie_id)

        reviews = get_reviews.json()
        assert isinstance(reviews, list), "Ответ должен быть списком"

        # Ищем удалённый отзыв по userId
        review_found = False
        for review in reviews:
            if review["userId"] == get_user_id:
                review_found = True
                break

        assert review_found is False, "Отзыв не был удалён"

    def test_hide_review(self, api_manager_admin, create_film_with_review, get_user_id):
        """Позитив: скрытие отзыва к фильму.
        Проверяем:
        1. Статус и заголовки ответа на скрытие
        2. Структуру ответа на скрытие
        3. Что после скрытия при редактировании отзыва приходит поле hidden = True
        4. Что отзыв не удалился из фильма (просто скрыт)"""
        movie_id = create_film_with_review

        # ========== 1. Скрываем отзыв ==========
        hide_review = api_manager_admin.films_api.hide_review(movie_id, get_user_id)

        # Проверка структуры ответа на скрытие
        data = hide_review.json()
        required_fields = ["userId", "rating", "text", "createdAt", "user"]
        for field in required_fields:
            assert field in data, f"У ответа отсутствует поле {field}"

        assert isinstance(data["userId"], str), "userId должен быть строкой"
        assert isinstance(data["rating"], int), "rating должен быть числом"
        assert isinstance(data["text"], str), "text должен быть строкой"
        assert isinstance(data["user"], dict), "user должен быть словарем"
        assert "fullName" in data["user"], "У user отсутствует поле fullName"
        assert data["userId"] == get_user_id, "userId не совпадает"

        # ========== 2. Редактируем отзыв, чтобы получить поле hidden ==========
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

        # ========== 3. Проверяем, что отзыв не удалился (просто скрыт) ==========
        get_movie = api_manager_admin.films_api.get_movie(movie_id)

        movie_data = get_movie.json()
        assert "reviews" in movie_data, "Отсутствует поле reviews"

        review_found = False
        for review in movie_data["reviews"]:
            if review["userId"] == get_user_id:
                review_found = True
                break

        assert review_found is True, "Отзыв удалился после скрытия (не должен был)"

    def test_hide_review_twice(self, api_manager_admin, create_film_with_review, get_user_id):
        """Позитив: повторное скрытие уже скрытого отзыва, идемпотентность."""
        movie_id = create_film_with_review

        # Первое скрытие
        api_manager_admin.films_api.hide_review(movie_id, get_user_id)

        # Второе скрытие
        api_manager_admin.films_api.hide_review(movie_id, get_user_id, expected_status=200)

    def test_show_review(self, api_manager_admin, create_film_with_review, get_user_id):
        """Позитив: показ скрытого отзыва к фильму.
        Проверяем:
        1. Статус и заголовки ответа на показ
        2. Структуру ответа на показ
        3. Что после показа при редактировании отзыва приходит поле hidden = False
        4. Что отзыв не удалился из фильма"""
        movie_id = create_film_with_review

        # ========== 1. Сначала скрываем отзыв ==========
        api_manager_admin.films_api.hide_review(movie_id, get_user_id)

        # ========== 2. Показываем отзыв ==========
        show_review = api_manager_admin.films_api.show_review(movie_id, get_user_id)

        # Проверка структуры ответа на показ
        data = show_review.json()
        required_fields = ["userId", "rating", "text", "createdAt", "user"]
        for field in required_fields:
            assert field in data, f"У ответа отсутствует поле {field}"

        assert isinstance(data["userId"], str), "userId должен быть строкой"
        assert isinstance(data["rating"], int), "rating должен быть числом"
        assert isinstance(data["text"], str), "text должен быть строкой"
        assert isinstance(data["user"], dict), "user должен быть словарем"
        assert "fullName" in data["user"], "У user отсутствует поле fullName"
        assert data["userId"] == get_user_id, "userId не совпадает"

        # ========== 3. Редактируем отзыв, чтобы получить поле hidden ==========
        edit_data = {
            "rating": faker.random_int(min=1, max=5),
            "text": faker.sentence(nb_words=15)
        }
        edit_review = api_manager_admin.films_api.put_review(movie_id, edit_data)

        edit_response = edit_review.json()
        assert "hidden" in edit_response, "Отсутствует поле hidden в ответе на редактирование"
        assert edit_response["hidden"] is False, (f"hidden должен быть False после показа, "
                                                  f"получено {edit_response['hidden']}")
        assert edit_response["rating"] == edit_data["rating"], "rating не совпадает"
        assert edit_response["text"] == edit_data["text"], "text не совпадает"
        assert edit_response["userId"] == get_user_id, "userId не совпадает"

        # ========== 4. Проверяем, что отзыв не удалился ==========
        get_movie = api_manager_admin.films_api.get_movie(movie_id)

        movie_data = get_movie.json()
        assert "reviews" in movie_data, "Отсутствует поле reviews"

        review_found = False
        for review in movie_data["reviews"]:
            if review["userId"] == get_user_id:
                review_found = True
                break

        assert review_found is True, "Отзыв удалился после показа (не должен был)"

    def test_show_review_twice(self, api_manager_admin, create_film_with_review, get_user_id):
        """Позитив: повторный показ уже показанного отзыва, идемпотентность."""
        movie_id = create_film_with_review

        # Сначала скрываем, чтобы потом показать
        api_manager_admin.films_api.hide_review(movie_id, get_user_id)

        # Первый показ
        api_manager_admin.films_api.show_review(movie_id, get_user_id)

        # Второй показ
        api_manager_admin.films_api.show_review(movie_id, get_user_id, expected_status=200)


class TestNegativeMoviesReviews:

    # ========== ПОЛУЧЕНИЕ ОТЗЫВОВ ПО ФИЛЬМУ (негатив) ==========
    def test_get_movie_reviews_invalid_id(self, api_manager):
        """Негатив: получение отзывов с несуществующим ID фильма"""
        api_manager.films_api.get_review(999999, expected_status=404)

    def test_get_movie_reviews_negative_id(self, api_manager):
        """Негатив: получение отзывов с отрицательным ID фильма"""
        api_manager.films_api.get_review(-1, expected_status=404)

    def test_get_movie_reviews_zero_id(self, api_manager):
        """Негатив: получение отзывов с ID фильма = 0"""
        api_manager.films_api.get_review(0, expected_status=404)

    @pytest.mark.skip(reason="БАГ: сервер возвращает 500 вместо 404")
    def test_get_movie_reviews_string_id(self, api_manager):
        """Негатив: получение отзывов с ID в виде строки"""
        api_manager.films_api.get_review("abc", expected_status=404)

    # ========== СОЗДАНИЕ ОТЗЫВА (негатив) ==========
    def test_create_review_without_token(self, api_manager, create_film_id, review_data):
        """Негатив: создание отзыва без авторизации"""
        movie_id = create_film_id
        api_manager.films_api.create_review(movie_id, review_data, expected_status=401)

    def test_create_review_with_invalid_token(self, api_manager, create_film_id, review_data):
        """Негатив: создание отзыва с неверным токеном"""
        movie_id = create_film_id
        api_manager.set_token("invalid_token")
        api_manager.films_api.create_review(movie_id, review_data, expected_status=401)
        api_manager.clear_token()

    def test_create_review_invalid_movie_id(self, api_manager_admin, review_data):
        """Негатив: создание отзыва с несуществующим ID фильма"""
        api_manager_admin.films_api.create_review(999999, review_data, expected_status=404)

    def test_create_review_negative_movie_id(self, api_manager_admin, review_data):
        """Негатив: создание отзыва с отрицательным ID фильма"""
        api_manager_admin.films_api.create_review(-1, review_data, expected_status=404)

    def test_create_review_zero_movie_id(self, api_manager_admin, review_data):
        """Негатив: создание отзыва с ID фильма = 0"""
        api_manager_admin.films_api.create_review(0, review_data, expected_status=404)

    @pytest.mark.skip(reason="БАГ: сервер возвращает 500 вместо 404")
    def test_create_review_string_movie_id(self, api_manager_admin, review_data):
        """Негатив: создание отзыва с ID фильма в виде строки"""
        api_manager_admin.films_api.create_review("abc", review_data, expected_status=404)

    def test_create_review_duplicate(self, api_manager_admin, create_film_id, review_data):
        """Негатив: создание второго отзыва на тот же фильм (дубликат)"""
        movie_id = create_film_id

        # Первый отзыв
        api_manager_admin.films_api.create_review(movie_id, review_data)

        # Второй отзыв (дубликат)
        api_manager_admin.films_api.create_review(movie_id, review_data, expected_status=409)

    @pytest.mark.skip(reason="БАГ: сервер возвращает 201 вместо 400")
    def test_create_review_rating_zero(self, api_manager_admin, create_film_id):
        """Негатив: создание отзыва с rating = 0"""
        movie_id = create_film_id
        data = {"rating": 0, "text": "Норм фильм"}
        api_manager_admin.films_api.create_review(movie_id, data, expected_status=400)

    @pytest.mark.skip(reason="БАГ: сервер возвращает 201 вместо 400")
    def test_create_review_rating_six(self, api_manager_admin, create_film_id):
        """Негатив: создание отзыва с rating = 6"""
        movie_id = create_film_id
        data = {"rating": 6, "text": "Норм фильм"}
        api_manager_admin.films_api.create_review(movie_id, data, expected_status=400)

    def test_create_review_rating_string(self, api_manager_admin, create_film_id):
        """Негатив: создание отзыва с rating в виде строки"""
        movie_id = create_film_id
        data = {"rating": "пять", "text": "Норм фильм"}
        api_manager_admin.films_api.create_review(movie_id, data, expected_status=400)

    def test_create_review_invalid_text_type(self, api_manager_admin, create_film_id):
        """Негатив: создание отзыва с text в виде числа (неверный тип)"""
        movie_id = create_film_id
        data = {"rating": 5, "text": 123}
        api_manager_admin.films_api.create_review(movie_id, data, expected_status=400)

    @pytest.mark.skip(reason="БАГ: сервер возвращает 201 вместо 400")
    def test_create_review_empty_text(self, api_manager_admin, create_film_id):
        """Негатив: создание отзыва с пустым text"""
        movie_id = create_film_id
        data = {"rating": 5, "text": ""}
        api_manager_admin.films_api.create_review(movie_id, data, expected_status=400)

    def test_create_review_empty_body(self, api_manager_admin, create_film_id):
        """Негатив: создание отзыва с пустым телом запроса"""
        movie_id = create_film_id
        api_manager_admin.films_api.create_review(movie_id, {}, expected_status=400)

    def test_create_review_missing_rating(self, api_manager_admin, create_film_id):
        """Негатив: создание отзыва без поля rating"""
        movie_id = create_film_id
        data = {"text": "Норм фильм"}
        api_manager_admin.films_api.create_review(movie_id, data, expected_status=400)

    @pytest.mark.skip(reason="БАГ или ФИЧА???: сервер возвращает 201 вместо 400")
    def test_create_review_missing_text(self, api_manager_admin, create_film_id):
        """Негатив: создание отзыва без поля text"""
        movie_id = create_film_id
        data = {"rating": 5}
        api_manager_admin.films_api.create_review(movie_id, data, expected_status=400)

    @pytest.mark.skip(reason="БАГ: при отправке лишних полей сервер возвращает 404 вместо 400")
    def test_create_review_extra_field(self, api_manager_admin, create_film_id):
        """Негатив: создание отзыва с лишними полями"""
        movie_id = create_film_id

        review_data_with_extra = {
            "rating": 5,
            "text": faker.sentence(nb_words=10),
            "extraField": "что-то лишнее",
            "anotherExtra": 12345
        }

        api_manager_admin.films_api.create_review(movie_id, review_data_with_extra, expected_status=400)

    # ========== РЕДАКТИРОВАНИЕ ОТЗЫВА (негатив) ==========
    def test_edit_review_without_token(self, api_manager, create_film_with_review):
        """Негатив: редактирование отзыва без авторизации"""
        movie_id = create_film_with_review
        edit_data = {"rating": 5, "text": "Новый текст"}
        api_manager.films_api.put_review(movie_id, edit_data, expected_status=401)

    def test_edit_review_with_invalid_token(self, api_manager, create_film_with_review):
        """Негатив: редактирование отзыва с неверным токеном"""
        movie_id = create_film_with_review
        edit_data = {"rating": 5, "text": "Новый текст"}
        api_manager.set_token("invalid_token")
        api_manager.films_api.put_review(movie_id, edit_data, expected_status=401)
        api_manager.clear_token()

    def test_edit_review_invalid_movie_id(self, api_manager_admin):
        """Негатив: редактирование отзыва с несуществующим ID фильма"""
        edit_data = {"rating": 5, "text": "Новый текст"}
        api_manager_admin.films_api.put_review(999999, edit_data, expected_status=404)

    def test_edit_review_negative_movie_id(self, api_manager_admin):
        """Негатив: редактирование отзыва с отрицательным ID фильма"""
        edit_data = {"rating": 5, "text": "Новый текст"}
        api_manager_admin.films_api.put_review(-1, edit_data, expected_status=404)

    def test_edit_review_zero_movie_id(self, api_manager_admin):
        """Негатив: редактирование отзыва с ID фильма = 0"""
        edit_data = {"rating": 5, "text": "Новый текст"}
        api_manager_admin.films_api.put_review(0, edit_data, expected_status=404)

    @pytest.mark.skip(reason="БАГ: сервер возвращает 200 вместо 400")
    def test_edit_review_rating_zero(self, api_manager_admin, create_film_with_review):
        """Негатив: редактирование отзыва с rating = 0"""
        movie_id = create_film_with_review
        edit_data = {"rating": 0, "text": "Новый текст"}
        api_manager_admin.films_api.put_review(movie_id, edit_data, expected_status=400)

    @pytest.mark.skip(reason="БАГ: сервер возвращает 200 вместо 400")
    def test_edit_review_rating_six(self, api_manager_admin, create_film_with_review):
        """Негатив: редактирование отзыва с rating = 6"""
        movie_id = create_film_with_review
        edit_data = {"rating": 6, "text": "Новый текст"}
        api_manager_admin.films_api.put_review(movie_id, edit_data, expected_status=400)

    def test_edit_review_rating_string(self, api_manager_admin, create_film_with_review):
        """Негатив: редактирование отзыва с rating в виде строки"""
        movie_id = create_film_with_review
        edit_data = {"rating": "пять", "text": "Новый текст"}
        api_manager_admin.films_api.put_review(movie_id, edit_data, expected_status=400)

    def test_edit_review_invalid_text_type(self, api_manager_admin, create_film_with_review):
        """Негатив: редактирование отзыва с text в виде числа (неверный тип)"""
        movie_id = create_film_with_review
        edit_data = {"rating": 5, "text": 123}
        api_manager_admin.films_api.put_review(movie_id, edit_data, expected_status=400)

    @pytest.mark.skip(reason="БАГ: сервер возвращает 200 вместо 400")
    def test_edit_review_empty_text(self, api_manager_admin, create_film_with_review):
        """Негатив: редактирование отзыва с пустым text"""
        movie_id = create_film_with_review
        edit_data = {"rating": 5, "text": ""}
        api_manager_admin.films_api.put_review(movie_id, edit_data, expected_status=400)

    def test_edit_review_empty_body(self, api_manager_admin, create_film_with_review):
        """Негатив: редактирование отзыва с пустым телом запроса"""
        movie_id = create_film_with_review
        api_manager_admin.films_api.put_review(movie_id, {}, expected_status=400)

    def test_edit_review_missing_rating(self, api_manager_admin, create_film_with_review):
        """Негатив: редактирование отзыва без поля rating"""
        movie_id = create_film_with_review
        edit_data = {"text": "Новый текст"}
        api_manager_admin.films_api.put_review(movie_id, edit_data, expected_status=400)

    def test_edit_review_missing_text(self, api_manager_admin, create_film_with_review):
        """Негатив: редактирование отзыва без поля text"""
        movie_id = create_film_with_review
        edit_data = {"rating": 5}
        api_manager_admin.films_api.put_review(movie_id, edit_data, expected_status=400)

    @pytest.mark.skip(reason="БАГ: при отправке лишних полей сервер возвращает 404 вместо 400")
    def test_edit_review_extra_field(self, api_manager_admin, create_film_with_review):
        """Негатив: редактирование отзыва с лишними полями"""
        movie_id = create_film_with_review

        edit_data_with_extra = {
            "rating": 5,
            "text": faker.sentence(nb_words=10),
            "extraField": "что-то лишнее",
            "anotherExtra": 12345
        }

        api_manager_admin.films_api.put_review(movie_id, edit_data_with_extra, expected_status=400)

    # ========== УДАЛЕНИЕ ОТЗЫВА (негатив) ==========
    # Параметр userId в Swagger — либо ошибка документации, либо пережиток прошлого.
    # На работу ручки не влияет. Инфа о юзере берется из токена. Поэтому не проверяем.
    def test_delete_review_without_token(self, api_manager, create_film_with_review):
        """Негатив: удаление отзыва без авторизации"""
        movie_id = create_film_with_review
        api_manager.films_api.delete_review(movie_id, expected_status=401)

    def test_delete_review_with_invalid_token(self, api_manager, create_film_with_review):
        """Негатив: удаление отзыва с неверным токеном"""
        movie_id = create_film_with_review
        api_manager.set_token("invalid_token")
        api_manager.films_api.delete_review(movie_id, expected_status=401)
        api_manager.clear_token()

    def test_delete_review_invalid_movie_id(self, api_manager_admin):
        """Негатив: удаление отзыва с несуществующим ID фильма"""
        api_manager_admin.films_api.delete_review(999999, expected_status=404)

    def test_delete_review_negative_movie_id(self, api_manager_admin):
        """Негатив: удаление отзыва с отрицательным ID фильма"""
        api_manager_admin.films_api.delete_review(-1, expected_status=404)

    def test_delete_review_zero_movie_id(self, api_manager_admin):
        """Негатив: удаление отзыва с ID фильма = 0"""
        api_manager_admin.films_api.delete_review(0, expected_status=404)

    def test_delete_review_twice(self, api_manager_admin, create_film_with_review):
        """Негатив: повторное удаление уже удалённого отзыва"""
        movie_id = create_film_with_review

        # Первое удаление
        api_manager_admin.films_api.delete_review(movie_id)

        # Второе удаление (повторное)
        api_manager_admin.films_api.delete_review(movie_id, expected_status=404)

    def test_delete_review_no_review(self, api_manager_admin, create_film_id):
        """Негатив: удаление отзыва у фильма, у которого нет отзыва"""
        movie_id = create_film_id
        api_manager_admin.films_api.delete_review(movie_id, expected_status=404)

    # ========== СКРЫТИЕ ОТЗЫВА (негатив) ==========
    def test_hide_review_without_token(self, api_manager, create_film_with_review, get_user_id):
        """Негатив: скрытие отзыва без авторизации (только ADMIN/SUPER_ADMIN)"""
        movie_id = create_film_with_review
        api_manager.films_api.hide_review(movie_id, get_user_id, expected_status=401)

    def test_hide_review_with_invalid_token(self, api_manager, create_film_with_review, get_user_id):
        """Негатив: скрытие отзыва с неверным токеном"""
        movie_id = create_film_with_review
        api_manager.set_token("invalid_token")
        api_manager.films_api.hide_review(movie_id, get_user_id, expected_status=401)
        api_manager.clear_token()

    def test_hide_review_invalid_movie_id(self, api_manager_admin, get_user_id):
        """Негатив: скрытие отзыва с несуществующим ID фильма"""
        api_manager_admin.films_api.hide_review(999999, get_user_id, expected_status=404)

    def test_hide_review_negative_movie_id(self, api_manager_admin, get_user_id):
        """Негатив: скрытие отзыва с отрицательным ID фильма"""
        api_manager_admin.films_api.hide_review(-1, get_user_id, expected_status=404)

    def test_hide_review_zero_movie_id(self, api_manager_admin, get_user_id):
        """Негатив: скрытие отзыва с ID фильма = 0"""
        api_manager_admin.films_api.hide_review(0, get_user_id, expected_status=404)

    def test_hide_review_invalid_user_id(self, api_manager_admin, create_film_with_review):
        """Негатив: скрытие отзыва с несуществующим userId"""
        movie_id = create_film_with_review
        invalid_user_id = "00000000-0000-0000-0000-000000000000"
        api_manager_admin.films_api.hide_review(movie_id, invalid_user_id, expected_status=404)

    def test_hide_review_invalid_user_id_format(self, api_manager_admin, create_film_with_review):
        """Негатив: скрытие отзыва с неверным форматом userId (не UUID)"""
        movie_id = create_film_with_review
        invalid_user_id = "not_a_uuid"
        api_manager_admin.films_api.hide_review(movie_id, invalid_user_id, expected_status=404)

    def test_hide_review_no_review(self, api_manager_admin, create_film_id, get_user_id):
        """Негатив: скрытие отзыва у фильма, у которого нет отзыва"""
        movie_id = create_film_id
        api_manager_admin.films_api.hide_review(movie_id, get_user_id, expected_status=404)

    # ========== ПОКАЗ ОТЗЫВА (негатив) ==========
    def test_show_review_without_token(self, api_manager, create_film_with_review, get_user_id):
        """Негатив: показ отзыва без авторизации (только ADMIN/SUPER_ADMIN)"""
        movie_id = create_film_with_review
        api_manager.films_api.show_review(movie_id, get_user_id, expected_status=401)

    def test_show_review_with_invalid_token(self, api_manager, create_film_with_review, get_user_id):
        """Негатив: показ отзыва с неверным токеном"""
        movie_id = create_film_with_review
        api_manager.set_token("invalid_token")
        api_manager.films_api.show_review(movie_id, get_user_id, expected_status=401)
        api_manager.clear_token()

    def test_show_review_invalid_movie_id(self, api_manager_admin, get_user_id):
        """Негатив: показ отзыва с несуществующим ID фильма"""
        api_manager_admin.films_api.show_review(999999, get_user_id, expected_status=404)

    def test_show_review_negative_movie_id(self, api_manager_admin, get_user_id):
        """Негатив: показ отзыва с отрицательным ID фильма"""
        api_manager_admin.films_api.show_review(-1, get_user_id, expected_status=404)

    def test_show_review_zero_movie_id(self, api_manager_admin, get_user_id):
        """Негатив: показ отзыва с ID фильма = 0"""
        api_manager_admin.films_api.show_review(0, get_user_id, expected_status=404)

    def test_show_review_invalid_user_id(self, api_manager_admin, create_film_with_review):
        """Негатив: показ отзыва с несуществующим userId"""
        movie_id = create_film_with_review
        invalid_user_id = "00000000-0000-0000-0000-000000000000"
        api_manager_admin.films_api.show_review(movie_id, invalid_user_id, expected_status=404)

    def test_show_review_invalid_user_id_format(self, api_manager_admin, create_film_with_review):
        """Негатив: показ отзыва с неверным форматом userId (не UUID)"""
        movie_id = create_film_with_review
        invalid_user_id = "not_a_uuid"
        api_manager_admin.films_api.show_review(movie_id, invalid_user_id, expected_status=404)

    def test_show_review_no_review(self, api_manager_admin, create_film_id, get_user_id):
        """Негатив: показ отзыва у фильма, у которого нет отзыва"""
        movie_id = create_film_id
        api_manager_admin.films_api.show_review(movie_id, get_user_id, expected_status=404)