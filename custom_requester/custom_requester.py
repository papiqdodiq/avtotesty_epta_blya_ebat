import json
import logging
import os

class CustomRequester:
    """
    Кастомный реквестер для стандартизации и упрощения отправки HTTP-запросов.
    """
    base_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    def __init__(self, session, base_url):
        """
        Инициализация кастомного реквестера.
        :param session: Объект requests.Session.
        :param base_url: Базовый URL API.
        """
        self.session = session
        self.base_url = base_url
        self.headers = self.base_headers.copy()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def send_request(self, method, endpoint, data=None, params=None, expected_status=200, need_logging=True):
        """
        Универсальный метод для отправки запросов.
        :param method: HTTP метод (GET, POST, PUT, DELETE и т.д.).
        :param endpoint: Эндпоинт (например, "/login").
        :param data: Тело запроса (JSON-данные).
        :param params: Параметры запроса (номер страницы, размер страницы, локация).
        :param expected_status: Ожидаемый статус-код (по умолчанию 200).
        :param need_logging: Флаг для логирования (по умолчанию True).
        :return: Объект ответа requests.Response.
        """
        url = f"{self.base_url}{endpoint}"
        response = self.session.request(method, url, json=data, params=params, headers=self.headers)

        if need_logging:
            self.log_request_and_response(response)

        if response.status_code != expected_status and response.status_code not in expected_status:
            raise ValueError(f"Unexpected status code: {response.status_code}. Expected: {expected_status}")

        if "Content-Type" in response.headers:
            assert response.headers["Content-Type"] == "application/json; charset=utf-8", "Неверный Content-Type"

        return response

    def _update_session_headers(self, **kwargs):
        """
        Обновление заголовков сессии.
        :param session: Объект requests.Session, предоставленный API-классом.
        :param kwargs: Дополнительные заголовки.
        """
        self.headers.update(kwargs)  # Обновляем базовые заголовки (атрибут в этом классе)
        self.session.headers.update(self.headers)  # Обновляем заголовки в текущей сессии (в реальной HTTP-сессии
        # вне этого класса)
        # self.headers тут не изолирован от сессии, он влияет на саму сессию и если мы меняем хедеры в объекте,
        # то меняются и хедеры сессии, что будет влиять на все остальные запросы от этой сессии,
        # вне объекта этого класса.
        # Лучше, конечно, убрать обновление хедеров сессии и изолировать, но здесь это все равно просто мертвый код.

    def log_request_and_response(self, response):
        """
        Логирование запросов и ответов.
        :param response: Объект ответа requests.Response.
        """
        try:
            request = response.request
            GREEN = '\033[32m'
            RED = '\033[31m'
            RESET = '\033[0m'
            headers = " \\\n".join([f"-H '{header}: {value}'" for header, value in request.headers.items()])
            full_test_name = f"pytest {os.environ.get('PYTEST_CURRENT_TEST', '').replace(' (call)', '')}"

            body = ""
            if hasattr(request, 'body') and request.body is not None:
                if isinstance(request.body, bytes):
                    body = request.body.decode('utf-8')
                body = f"-d '{body}' \n" if body != '{}' else ''

            # Логируем запрос
            self.logger.info(f"\n{'=' * 40} REQUEST {'=' * 40}")
            self.logger.info(
                f"{GREEN}{full_test_name}{RESET}\n"
                f"curl -X {request.method} '{request.url}' \\\n"
                f"{headers} \\\n"
                f"{body}"
            )

            # Обрабатываем ответ
            response_status = response.status_code
            is_success = response.ok
            response_data = response.text

            # Попытка форматировать JSON
            try:
                response_data = json.dumps(json.loads(response.text), indent=4, ensure_ascii=False)
            except json.JSONDecodeError:
                pass  # Оставляем текст, если это не JSON

            # Логируем ответ
            self.logger.info(f"\n{'=' * 40} RESPONSE {'=' * 40}")
            if not is_success:
                self.logger.info(
                    f"\tSTATUS_CODE: {RED}{response_status}{RESET}\n"
                    f"\tDATA: {RED}{response_data}{RESET}"
                )
            else:
                self.logger.info(
                    f"\tSTATUS_CODE: {GREEN}{response_status}{RESET}\n"
                    f"\tDATA:\n{response_data}"
                )
            self.logger.info(f"{'=' * 80}\n")
        except Exception as e:
            self.logger.error(f"\nLogging failed: {type(e)} = {e}")