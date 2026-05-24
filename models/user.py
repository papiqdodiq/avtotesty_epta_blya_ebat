from pydantic import BaseModel, Field, field_validator, ValidationError
from venv import logger
from enum_constants.roles import Roles
from typing import Optional


class User(BaseModel):
    email: str
    fullName: str
    password: str = Field(..., min_length=8)
    passwordRepeat: str = Field(..., min_length=8)
    roles: list[Roles]
    banned: Optional[bool] = None
    verified: Optional[bool] = None

    @field_validator("email")
    def check_email(cls, value: str) -> str:
        if "@" not in value:
            raise ValueError("В поле почты должен быть символ @")
        return value


def test_user_data(register_data, create_user_data):
    user = User(**register_data) # Проверяем возможность конвертации данных и соответствия типов данных с помощью Pydantic
    assert user.email == register_data["email"] # Возможность дополнительных проверок
    logger.info(f"{user.email=} {user.fullName=} {user.password=} {user.roles=}") # а также возможность удобного взаимодействия

    # Пример конвертации первого объекта в json
    first_json_data = user.model_dump_json()
    logger.info(f"{first_json_data=}")
    # Ответ: INFO first_json_data='{"email":"kekrgm47las@gmail.com","fullName":"Carolyn Church","password":"Z*OK*&DX%nSjtT%V8Pj","passwordRepeat":"Z*OK*&DX%nSjtT%V8Pj","roles":["USER"],"banned":null,"verified":null}'
    # Суть: если мы не пишем exclude_unset=True, то в json будут поля, которые по факту пустые

    # Пример обратной конвертации в объект:
    new_data = User.model_validate_json(first_json_data)
    logger.info(f"{new_data=}")
    # User(email='...', fullName='...', ...)

    # Пример конвертации второго объекта в json
    second_user = User(**create_user_data)
    second_json_data = second_user.model_dump_json(exclude_unset=True)
    logger.info(f"{second_json_data=}")
    # Ответ: INFO second_json_data='{"email":"kekrgm47las@gmail.com","fullName":"Carolyn Church","password":"Z*OK*&DX%nSjtT%V8Pj","passwordRepeat":"Z*OK*&DX%nSjtT%V8Pj","roles":["USER"],"banned":false,"verified":true}'


def test_negative_email_and_password():
    negative_data = {
        "email": "email",
        "fullName": "John Doe",
        "password": "1234567",
        "passwordRepeat": "1234567",
        "roles": [Roles.USER.value],
        "verified": True,
        "banned": False
    }
    try:
        user = User(**negative_data)
        logger.info(f"{user.email=} {user.fullName=} {user.password=} {user.roles=}")
    except ValidationError as e:
        logger.info(f"Ошибка валидации: {e}")