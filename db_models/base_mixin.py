from sqlalchemy.orm import DeclarativeBase
from typing import Dict, Any


class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass


class ToDictMixin:
    """Миксин для преобразования модели в словарь"""

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование всех колонок в словарь"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns  # type: ignore
        }