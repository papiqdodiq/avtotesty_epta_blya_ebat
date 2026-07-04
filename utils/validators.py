from uuid import UUID
from datetime import datetime


def is_valid_uuid(uuid_string):
    """
    Проверяет, является ли строка валидным UUID.

    :param uuid_string: Строка для проверки.
    :return: True если валидный UUID, иначе False.
    """
    try:
        UUID(uuid_string)
        return True
    except (ValueError, AttributeError, TypeError):
        return False


def assert_valid_uuid(uuid_string, field_name="id"):
    """
    Проверяет UUID и выдаёт понятную ошибку.

    :param uuid_string: Строка для проверки.
    :param field_name: Название поля для сообщения об ошибке.
    """
    assert is_valid_uuid(uuid_string), f"{field_name} '{uuid_string}' не является валидным UUID"


def is_valid_iso_datetime(date_string):
    """
    Проверяет, является ли строка валидной датой в формате ISO 8601.

    :param date_string: Строка с датой.
    :return: True если валидная, иначе False.
    """
    try:
        datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return True
    except (ValueError, AttributeError, TypeError):
        return False


def assert_valid_iso_datetime(date_string, field_name="createdAt"):
    """
    Проверяет ISO дату и выдаёт понятную ошибку.

    :param date_string: Строка с датой.
    :param field_name: Название поля для сообщения об ошибке.
    """
    assert is_valid_iso_datetime(date_string), f"{field_name} '{date_string}' не в формате ISO 8601"


def assert_datetime_in_range(date_string, before_request, after_request, field_name="createdAt"):
    """
    Проверяет, что дата находится в допустимом интервале.

    :param date_string: Строка с датой.
    :param before_request: Время до запроса.
    :param after_request: Время после запроса (+10 секунд).
    :param field_name: Название поля для сообщения об ошибке.
    """
    created_at = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
    assert before_request <= created_at <= after_request, \
        f"{field_name} {created_at} не в интервале [{before_request}, {after_request}]"
