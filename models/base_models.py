from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
import datetime
from enum_constants.roles import Roles
from utils.validators import assert_valid_uuid

class TestUser(BaseModel):
    email: str = Field(pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", description="Email пользователя")
    fullName: str
    password: str
    passwordRepeat: str = Field(..., min_length=1, max_length=20, description="passwordRepeat должен полностью совпадать с полем password")
    roles: list[Roles] = [Roles.USER]
    verified: Optional[bool] = None
    banned: Optional[bool] = None

    @field_validator("passwordRepeat")
    def check_password_repeat(cls, value: str, info) -> str:
        # Проверяем, совпадение паролей
        if "password" in info.data and value != info.data["password"]:
            # info.data это поля, которые уже прошли проверку
            raise ValueError("Пароли не совпадают")
        return value

    # Добавляем кастомный JSON-сериализатор для Enum (для корректного model_dump_json и model_dump)
    class Config:
        use_enum_values = True
        # use_enum_values = True - для model_dump() и model_dump_json()
        json_encoders = {
            Roles: lambda v: v.value  # Преобразуем Enum в строку
        }
        # json_encoders - ТОЛЬКО для model_dump_json() (устаревший механизм)

class CreateUserData(BaseModel):
    email: str = Field(pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", description="Email пользователя")
    fullName: str
    password: str
    verified: bool
    banned: bool

    class Config:
        use_enum_values = True

class CreateUserResponse(BaseModel):
    id: str
    email: str = Field(pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", description="Email пользователя")
    fullName: str
    roles: List[Roles]
    verified: bool
    banned: bool
    createdAt: str = Field(description="Дата и время создания пользователя в формате ISO 8601")

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str) -> str:
        """Валидатор для проверки идентификатора (формата UUID)."""
        assert_valid_uuid(value)
        return value

    @field_validator("createdAt")
    @classmethod
    def validate_created_at(cls, value: str) -> str:
        """Валидатор для проверки формата даты и времени (ISO 8601)."""
        try:
            datetime.datetime.fromisoformat(value)
        except ValueError:
            raise ValueError("Некорректный формат даты и времени. Ожидается формат ISO 8601.")
        return value

    class Config:
        use_enum_values = True

class PatchUserResponse(BaseModel):
    email: str = Field(pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", description="Email пользователя")
    fullName: str
    verified: bool
    banned: bool
    roles: List[Roles]
    createdAt: str = Field(description="Дата и время создания пользователя в формате ISO 8601")

    @field_validator("createdAt")
    @classmethod
    def validate_created_at(cls, value: str) -> str:
        """Валидатор для проверки формата даты и времени (ISO 8601)."""
        try:
            datetime.datetime.fromisoformat(value)
        except ValueError:
            raise ValueError("Некорректный формат даты и времени. Ожидается формат ISO 8601.")
        return value

    class Config:
        use_enum_values = True

class RegisterUserResponse(BaseModel):
    id: str
    email: str = Field(pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", description="Email пользователя")
    fullName: str = Field(min_length=1, max_length=100, description="Полное имя пользователя")
    verified: bool
    banned: bool
    roles: List[Roles]
    createdAt: str = Field(description="Дата и время создания пользователя в формате ISO 8601")

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str) -> str:
        """Валидатор для проверки идентификатора (формата UUID)."""
        assert_valid_uuid(value)
        return value

    @field_validator("createdAt")
    @classmethod
    def validate_created_at(cls, value: str) -> str:
        """Валидатор для проверки формата даты и времени (ISO 8601)."""
        try:
            datetime.datetime.fromisoformat(value)
        except ValueError:
            raise ValueError("Некорректный формат даты и времени. Ожидается формат ISO 8601.")
        return value

    # Добавляем кастомный JSON-сериализатор для Enum (для корректного model_dump_json и model_dump)
    class Config:
        use_enum_values = True

class UserInfo(BaseModel):
    """Модель для вложенного объекта user"""
    id: str
    email: str = Field(pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", description="Email пользователя")
    fullName: str
    roles: List[Roles]

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str) -> str:
        """Валидатор для проверки идентификатора (формата UUID)."""
        assert_valid_uuid(value)
        return value

    class Config:
        use_enum_values = True

class LoginUserResponse(BaseModel):
    """Модель для полного ответа при логине"""
    user: UserInfo
    accessToken: str
    refreshToken: str
    expiresIn: int

    @field_validator("accessToken")
    @classmethod
    def validate_access_token(cls, value: str) -> str:
        assert len(value) > 0, "accessToken не должен быть пустым"
        return value

    @field_validator("refreshToken")
    @classmethod
    def validate_refresh_token(cls, value: str) -> str:
        assert len(value) > 0, "refreshToken не должен быть пустым"
        return value

    @field_validator("expiresIn")
    @classmethod
    def validate_expires_in(cls, value: int) -> int:
        assert value > 0, "expiresIn должен быть больше 0"
        return value

    # Добавляем кастомный JSON-сериализатор для Enum (для корректного model_dump_json и model_dump)
    class Config:
        use_enum_values = True
