from custom_requester.custom_requester import CustomRequester

# - Класс наследуется от `CustomRequester`, получая доступ к методам (`send_request`).
class FilmsAPI(CustomRequester):
    """
    Класс для работы с фильмами.
    """

    # - Принимает `session`, которая передается в базовый класс.
    def __init__(self, session):
        super().__init__(session=session, base_url="https://api.dev-cinescope.coconutqa.ru/")
        # - При инициализации получает сессию и базовый URL API.

    # ========== методы для /movies ==========

    def get_billboard(self, billboard_params, expected_status=200):
        """
        Получение списка фильмов (афиши) с пагинацией и фильтрацией.

        :param billboard_params: Словарь с параметрами запроса (page, pageSize, minPrice, maxPrice, locations, published, genreId, createdAt).
        :param expected_status: Ожидаемый статус-код ответа.
        :return: Response объект requests.
        """
        return self.send_request(
            method="GET",
            endpoint="/movies",
            params=billboard_params,
            expected_status=expected_status
        )

    def create_movie(self, film_data, expected_status=201):
        """
        Создание нового фильма.

        :param film_data: Словарь с данными фильма (name, imageUrl, price, description, location, published, genreId).
        :param expected_status: Ожидаемый статус-код ответа.
        :return: Response объект requests.
        """
        return self.send_request(
            method="POST",
            endpoint="/movies",
            data=film_data,
            expected_status=expected_status
        )

    def get_movie(self, movie_id, expected_status=200):
        """
        Получение информации о фильме по его ID.

        :param movie_id: Идентификатор фильма (число).
        :param expected_status: Ожидаемый статус-код ответа.
        :return: Response объект requests.
        """
        return self.send_request(
            method="GET",
            endpoint=f"/movies/{movie_id}",
            expected_status=expected_status
        )

    def delete_movie(self, movie_id, expected_status=200):
        """
        Удаление фильма по его ID.

        :param movie_id: Идентификатор фильма (число).
        :param expected_status: Ожидаемый статус-код ответа.
        :return: Response объект requests.
        """
        return self.send_request(
            method="DELETE",
            endpoint=f"/movies/{movie_id}",
            expected_status=expected_status
        )

    def patch_movie(self, movie_id, film_data_patch, expected_status=200):
        """
        Частичное обновление данных фильма.

        :param movie_id: Идентификатор фильма (число).
        :param film_data_patch: Словарь с полями для обновления (name, location, price, и т.д.).
        :param expected_status: Ожидаемый статус-код ответа.
        :return: Response объект requests.
        """
        return self.send_request(
            method="PATCH",
            endpoint=f"/movies/{movie_id}",
            data=film_data_patch,
            expected_status=expected_status
        )

    # ========== методы для /movies/{id}/reviews ==========

    def create_review(self, movie_id, review_data, expected_status=201):
        """
        Создание отзыва к фильму.

        :param movie_id: Идентификатор фильма (число).
        :param review_data: Словарь с данными отзыва (rating, text).
        :param expected_status: Ожидаемый статус-код ответа.
        :return: Response объект requests.
        """
        return self.send_request(
            method="POST",
            endpoint=f"/movies/{movie_id}/reviews",
            data=review_data,
            expected_status=expected_status
        )

    def get_review(self, movie_id, expected_status=200):
        """
        Получение всех отзывов к фильму.

        :param movie_id: Идентификатор фильма (число).
        :param expected_status: Ожидаемый статус-код ответа.
        :return: Response объект requests (список отзывов).
        """
        return self.send_request(
            method="GET",
            endpoint=f"/movies/{movie_id}/reviews",
            expected_status=expected_status
        )

    def put_review(self, movie_id, edit_data, expected_status=200):
        """
        Полное обновление отзыва к фильму (замена).

        :param movie_id: Идентификатор фильма (число).
        :param edit_data: Словарь с новыми данными отзыва (rating, text).
        :param expected_status: Ожидаемый статус-код ответа.
        :return: Response объект requests.
        """
        return self.send_request(
            method="PUT",
            endpoint=f"/movies/{movie_id}/reviews",
            data=edit_data,
            expected_status=expected_status
        )

    def delete_review(self, movie_id, expected_status=200):
        """
        Удаление отзыва текущего пользователя к фильму.

        :param movie_id: Идентификатор фильма (число).
        :param expected_status: Ожидаемый статус-код ответа.
        :return: Response объект requests.
        """
        return self.send_request(
            method="DELETE",
            endpoint=f"/movies/{movie_id}/reviews",
            expected_status=expected_status
        )

    def hide_review(self, movie_id, user_id, expected_status=200):
        """
        Скрытие отзыва пользователя (только для ADMIN/SUPER_ADMIN).

        :param movie_id: Идентификатор фильма (число).
        :param user_id: Идентификатор пользователя (строка UUID).
        :param expected_status: Ожидаемый статус-код ответа.
        :return: Response объект requests.
        """
        return self.send_request(
            method="PATCH",
            endpoint=f"/movies/{movie_id}/reviews/hide/{user_id}",
            expected_status=expected_status
        )

    def show_review(self, movie_id, user_id, expected_status=200):
        """
        Показ скрытого отзыва пользователя (только для ADMIN/SUPER_ADMIN).

        :param movie_id: Идентификатор фильма (число).
        :param user_id: Идентификатор пользователя (строка UUID).
        :param expected_status: Ожидаемый статус-код ответа.
        :return: Response объект requests.
        """
        return self.send_request(
            method="PATCH",
            endpoint=f"/movies/{movie_id}/reviews/show/{user_id}",
            expected_status=expected_status
        )

    # ========== методы для /genres ==========

    def get_genres(self, expected_status=200):
        """
        Получение списка всех жанров.

        :param expected_status: Ожидаемый статус-код ответа.
        :return: Response объект requests (список жанров).
        """
        return self.send_request(
            method="GET",
            endpoint="/genres",
            expected_status=expected_status
        )

    def get_genre(self, genre_id, expected_status=200):
        """
        Получение жанра по его ID.

        :param genre_id: Идентификатор жанра (число).
        :param expected_status: Ожидаемый статус-код ответа.
        :return: Response объект requests.
        """
        return self.send_request(
            method="GET",
            endpoint=f"/genres/{genre_id}",
            expected_status=expected_status
        )

    def create_genres(self, genre_data, expected_status=201):
        """
        Создание нового жанра (только для SUPER_ADMIN).

        :param genre_data: Словарь с данными жанра (name).
        :param expected_status: Ожидаемый статус-код ответа.
        :return: Response объект requests.
        """
        return self.send_request(
            method="POST",
            endpoint="/genres",
            data=genre_data,
            expected_status=expected_status
        )

    def delete_genre(self, genre_id, expected_status=200):
        """
        Удаление жанра по его ID (только для SUPER_ADMIN).

        :param genre_id: Идентификатор жанра (число).
        :param expected_status: Ожидаемый статус-код ответа.
        :return: Response объект requests.
        """
        return self.send_request(
            method="DELETE",
            endpoint=f"/genres/{genre_id}",
            expected_status=expected_status
        )

    # ========== работа с токенами ==========

    def set_token(self, token):
        """
        Устанавливает токен авторизации для запросов FilmsAPI.
        Обновляет заголовок Authorization в сессии.

        :param token: Строка accessToken (без префикса "Bearer ").
        """
        self._update_session_headers(**{"Authorization": "Bearer " + token})

    def clear_token(self):
        """
        Сбрасывает токен авторизации для запросов FilmsAPI.
        Удаляет заголовок Authorization из сессии.
        """
        self._update_session_headers(**{"Authorization": None})