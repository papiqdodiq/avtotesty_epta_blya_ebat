import requests
import pytest
from constants import PAYMENT_URL, AUTH_URL
from faker import Faker

faker_ru = Faker('ru_RU')
faker_en = Faker('en_US')

class TestPositivePayment:

    def test_create_payment_success(self, auth_session, create_payment_data):
        """Позитив: успешное создание оплаты с корректными данными.
        Проверяем статус, заголовки и структуру ответа."""

        response = auth_session.post(f"{PAYMENT_URL}/create", json=create_payment_data)

        # Статус и заголовки
        assert response.status_code == 201, f"Ошибка при создании оплаты: {response.text}"
        assert response.headers.get("Content-Type") == "application/json; charset=utf-8", "Неверный Content-Type"

        # Проверка структуры ответа
        data = response.json()
        assert "status" in data, "У ответа отсутствует поле status"
        assert data["status"] == "SUCCESS", f"Статус должен быть SUCCESS, получено {data['status']}"

    def test_get_user_payments_success(self, auth_session, create_user, create_film_id, valid_card_data):
        """Позитив: ADMIN/SUPER_ADMIN получает платежи ДРУГОГО пользователя.
        Сначала создаём оплату для обычного пользователя, потом ADMIN смотрит его платежи."""

        other_user_id = create_user["id"]
        other_user_email = create_user["email"]
        other_user_password = "Test123456@"

        # 1. Логинимся как обычный пользователь (чтобы создать оплату)
        login_response = requests.post(f"{AUTH_URL}/login", json={
            "email": other_user_email,
            "password": other_user_password
        })
        assert login_response.status_code == 200
        user_token = login_response.json()["accessToken"]

        user_session = requests.Session()
        user_session.headers.update({"Authorization": f"Bearer {user_token}"})

        # 2. Обычный пользователь создаёт оплату
        payment_data = {
            "movieId": create_film_id,
            "amount": faker_ru.random_int(min=1, max=5),
            "card": valid_card_data
        }

        create_payment = user_session.post(f"{PAYMENT_URL}/create", json=payment_data)
        assert create_payment.status_code == 201

        # 3. ADMIN (auth_session) запрашивает платежи обычного пользователя
        response = auth_session.get(f"{PAYMENT_URL}/user/{other_user_id}")

        # Статус и заголовки
        assert response.status_code == 200, f"Ошибка при получении платежей: {response.text}"
        assert response.headers.get("Content-Type") == "application/json; charset=utf-8", "Неверный Content-Type"

        # Проверка структуры ответа (список платежей)
        payments = response.json()
        assert isinstance(payments, list), "Ответ должен быть списком"

        # Проверяем, что все платежи принадлежат другому пользователю
        for payment in payments:
            assert payment.get(
                "userId") == other_user_id, f"Платеж {payment.get('id')} принадлежит другому пользователю"

        # Проверяем, что созданная оплата есть в списке
        found = False
        for payment in payments:
            if payment.get("movieId") == create_film_id:
                found = True
                break
        assert found, "Созданная оплата не найдена в списке платежей пользователя"

    def test_get_my_payments_success(self, auth_session, create_film_id, valid_card_data):
        """Позитив: USER получает свои платежи.
        Сначала создаём оплату, потом получаем свои платежи."""

        # 1. Сначала узнаём свой userId (из токена)
        user_response = auth_session.get(f"{AUTH_URL}/user/me")
        assert user_response.status_code == 200
        current_user_id = user_response.json()["id"]

        # 2. Создаём оплату
        payment_data = {
            "movieId": create_film_id,
            "amount": faker_ru.random_int(min=1, max=5),
            "card": valid_card_data
        }

        create_payment = auth_session.post(f"{PAYMENT_URL}/create", json=payment_data)
        assert create_payment.status_code == 201

        # 3. Получаем свои платежи
        response = auth_session.get(f"{PAYMENT_URL}/user")

        # Статус и заголовки
        assert response.status_code == 200, f"Ошибка при получении платежей: {response.text}"
        assert response.headers.get("Content-Type") == "application/json; charset=utf-8", "Неверный Content-Type"

        # Проверка структуры ответа (список платежей)
        payments = response.json()
        assert isinstance(payments, list), "Ответ должен быть списком"

        # Проверяем, что все платежи принадлежат текущему пользователю
        for payment in payments:
            assert payment.get("userId") == current_user_id, f"Платеж {payment.get('id')} принадлежит другому пользователю"

        # Проверяем, что созданная оплата есть в списке
        found = False
        for payment in payments:
            if payment.get("movieId") == create_film_id:
                found = True
                break
        assert found, "Созданная оплата не найдена в списке платежей"

    def test_find_all_payments_default(self, auth_session):
        """Позитив: получение всех платежей с параметрами по умолчанию.
        Проверяем статус, структуру ответа, пагинацию."""

        response = auth_session.get(f"{PAYMENT_URL}/find-all")

        assert response.status_code == 200
        assert response.headers.get("Content-Type") == "application/json; charset=utf-8"

        data = response.json()
        required_fields = ["payments", "count", "page", "pageSize", "pageCount"]
        for field in required_fields:
            assert field in data, f"Отсутствует поле {field}"

        assert isinstance(data["payments"], list)
        assert isinstance(data["count"], int)
        assert isinstance(data["page"], int)
        assert isinstance(data["pageSize"], int)
        assert isinstance(data["pageCount"], int)

        # Пагинация
        assert data["page"] == 1
        assert data["pageSize"] == 10

    @pytest.mark.parametrize("status", ["SUCCESS", "INVALID_CARD", "ERROR"])
    def test_find_all_payments_filter_by_status(self, auth_session, status):
        """Позитив: фильтрация платежей по статусу."""

        response = auth_session.get(f"{PAYMENT_URL}/find-all", params={"status": status})

        assert response.status_code == 200
        data = response.json()

        # Проверяем, что все платежи имеют нужный статус
        for payment in data["payments"]:
            assert payment.get("status") == status, f"Платеж {payment.get('id')} имеет статус {payment.get('status')}, ожидался {status}"

    @pytest.mark.parametrize("order", ["asc", "desc"])
    def test_find_all_payments_sort_by_created_at(self, auth_session, order):
        """Позитив: сортировка платежей по дате создания (asc/desc)."""

        response = auth_session.get(f"{PAYMENT_URL}/find-all", params={"createdAt": order})

        assert response.status_code == 200
        data = response.json()
        payments = data["payments"]

        if len(payments) > 1:
            dates = [p["createdAt"] for p in payments]
            if order == "asc":
                assert dates == sorted(dates), "Даты не отсортированы по возрастанию"
            else:
                assert dates == sorted(dates, reverse=True), "Даты не отсортированы по убыванию"

    def test_find_all_payments_pagination(self, auth_session):
        """Позитив: проверка пагинации (page, pageSize)."""

        # Первая страница
        response1 = auth_session.get(f"{PAYMENT_URL}/find-all", params={"page": 1, "pageSize": 5})
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["page"] == 1
        assert data1["pageSize"] == 5
        assert len(data1["payments"]) <= 5

        # Вторая страница
        response2 = auth_session.get(f"{PAYMENT_URL}/find-all", params={"page": 2, "pageSize": 19})
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["page"] == 2
        assert data2["pageSize"] == 19

        # Проверяем, что страницы разные
        if data1["payments"] and data2["payments"]:
            assert data1["payments"][0]["id"] != data2["payments"][0]["id"], "Страницы совпадают"

class TestNegativePayment:

    # ========== СОЗДАНИЕ ОПЛАТЫ (негатив) ==========
    def test_create_payment_without_token(self, create_payment_data):
        """Негатив: создание оплаты без авторизации"""

        response = requests.post(f"{PAYMENT_URL}/create", json=create_payment_data)
        assert response.status_code == 401, "Оплата создалась без авторизации"

    def test_create_payment_invalid_movie_id(self, auth_session, valid_card_data):
        """Негатив: оплата несуществующего фильма"""

        payment_data = {
            "movieId": 999999,
            "amount": 1,
            "card": valid_card_data
        }

        response = auth_session.post(f"{PAYMENT_URL}/create", json=payment_data)
        assert response.status_code == 404, "Оплата несуществующего фильма не вызвала ошибку"

    def test_create_payment_invalid_card(self, auth_session, create_film_id):
        """Негатив: оплата с неверным номером карты"""

        payment_data = {
            "movieId": create_film_id,
            "amount": 1,
            "card": {
                "cardNumber": "0000000000000000",
                "cardHolder": faker_en.name(),
                "expirationDate": "12/28",
                "securityCode": 123
            }
        }

        response = auth_session.post(f"{PAYMENT_URL}/create", json=payment_data)
        assert response.status_code == 400, "Оплата с неверной картой не вызвала ошибку"

        # Проверяем, что ошибка именно INVALID_CARD
        data = response.json()
        assert data.get("error", {}).get("status") == "INVALID_CARD", "Статус ошибки должен быть INVALID_CARD"

    def test_create_payment_empty_body(self, auth_session):
        """Негатив: оплата с пустым телом запроса"""

        response = auth_session.post(f"{PAYMENT_URL}/create", json={})
        assert response.status_code == 400, "Оплата с пустым телом не вызвала ошибку"

    @pytest.mark.skip(reason="Нет способа симулировать 500/503 без моков или поддержки от разработчиков")
    def test_create_payment_internal_server_error(self, auth_session):
        pass

    @pytest.mark.skip(reason="Нет способа симулировать 500/503 без моков или поддержки от разработчиков")
    def test_create_payment_service_unavailable(self, auth_session):
        pass

    # ========== ПОЛУЧЕНИЕ ПЛАТЕЖЕЙ ДРУГОГО ПОЛЬЗОВАТЕЛЯ (негатив) ==========
    def test_get_user_payments_without_token(self, create_user):
        """Негатив: получение платежей пользователя без авторизации"""

        other_user_id = create_user["id"]
        response = requests.get(f"{PAYMENT_URL}/user/{other_user_id}")
        assert response.status_code == 401, "Платежи получены без авторизации"

    def test_get_user_payments_forbidden(self, auth_session, create_user):
        """Негатив: обычный пользователь пытается получить платежи ДРУГОГО пользователя"""

        # Создаём второго пользователя
        email2 = faker_en.email()
        full_name2 = faker_ru.name()

        user_data2 = {
            "email": email2,
            "fullName": full_name2,
            "password": "Test123456@",
            "verified": True,
            "banned": False
        }

        create_response = auth_session.post(f"{AUTH_URL}/user", json=user_data2)
        assert create_response.status_code == 201
        other_user_id = create_response.json()["id"]

        # Логинимся как первый обычный пользователь (create_user)
        login_response = requests.post(f"{AUTH_URL}/login", json={
            "email": create_user["email"],
            "password": "Test123456@"
        })
        assert login_response.status_code == 200
        user_token = login_response.json()["accessToken"]

        user_session = requests.Session()
        user_session.headers.update({"Authorization": f"Bearer {user_token}"})

        # Пытаемся получить платежи ДРУГОГО пользователя
        response = user_session.get(f"{PAYMENT_URL}/user/{other_user_id}")
        assert response.status_code == 403, "Обычный пользователь получил платежи другого пользователя"

        # Чистим второго пользователя
        auth_session.delete(f"{AUTH_URL}/user/{other_user_id}")

    def test_get_user_payments_not_found(self, auth_session):
        """Негатив: получение платежей несуществующего пользователя"""

        invalid_user_id = "00000000-0000-0000-0000-000000000000"
        response = auth_session.get(f"{PAYMENT_URL}/user/{invalid_user_id}")
        assert response.status_code == 404, "Платежи несуществующего пользователя не вызвали ошибку"

    # ========== ПОЛУЧЕНИЕ ПЛАТЕЖЕЙ ТЕКУЩЕГО ПОЛЬЗОВАТЕЛЯ (негатив) ==========
    def test_get_my_payments_without_token(self):
        """Негатив: получение своих платежей без авторизации"""

        response = requests.get(f"{PAYMENT_URL}/user")
        assert response.status_code == 401, "Платежи получены без авторизации"

    def test_get_my_payments_forbidden(self, auth_session, create_user):
        """Негатив: пользователь без ролей пытается получить свои платежи (403)"""

        user_id = create_user["id"]

        # 1. Удаляем у пользователя все роли
        update_data = {
            "verified": True,
            "banned": False,
            "roles": []  # пустой массив ролей
        }

        update_response = auth_session.patch(f"{AUTH_URL}/user/{user_id}", json=update_data)
        assert update_response.status_code == 200, "Не удалось обновить роли пользователя"

        # 2. Логинимся как пользователь без ролей
        login_response = requests.post(f"{AUTH_URL}/login", json={
            "email": create_user["email"],
            "password": "Test123456@"
        })
        assert login_response.status_code == 200
        user_token = login_response.json()["accessToken"]

        user_session = requests.Session()
        user_session.headers.update({"Authorization": f"Bearer {user_token}"})

        # 3. Пытаемся получить свои платежи
        response = user_session.get(f"{PAYMENT_URL}/user")
        assert response.status_code == 403, "Пользователь без ролей получил платежи"

    # ========== ПОЛУЧЕНИЕ ВСЕХ ПЛАТЕЖЕЙ (негатив) ==========
    def test_find_all_payments_without_token(self):
        """Негатив: получение платежей без авторизации"""

        response = requests.get(f"{PAYMENT_URL}/find-all")
        assert response.status_code == 401, "Платежи получены без авторизации"

    def test_find_all_payments_forbidden(self, create_user):
        """Негатив: обычный пользователь пытается получить все платежи (403)."""

        # Логинимся как обычный пользователь
        login_response = requests.post(f"{AUTH_URL}/login", json={
            "email": create_user["email"],
            "password": "Test123456@"
        })
        assert login_response.status_code == 200
        user_token = login_response.json()["accessToken"]

        user_session = requests.Session()
        user_session.headers.update({"Authorization": f"Bearer {user_token}"})

        response = user_session.get(f"{PAYMENT_URL}/find-all")
        assert response.status_code == 403, "Обычный пользователь получил все платежи"

    @pytest.mark.parametrize("invalid_params,expected_status", [
        ({"page": 0}, 400),
        ({"page": -1}, 400),
        ({"pageSize": 0}, 400),
        ({"pageSize": 21}, 400),
        ({"pageSize": -1}, 400),
        ({"status": "UNKNOWN"}, 400),
        ({"createdAt": "invalid"}, 400),
    ])
    def test_find_all_payments_invalid_params(self, auth_session, invalid_params, expected_status):
        """Негатив: неверные параметры запроса."""

        response = auth_session.get(f"{PAYMENT_URL}/find-all", params=invalid_params)
        assert response.status_code == expected_status, f"Параметры {invalid_params} не вызвали ошибку"