AUTH_URL = "https://auth.dev-cinescope.coconutqa.ru"

MOVIES_URL = "https://api.dev-cinescope.coconutqa.ru"

PAYMENT_URL = "https://payment.dev-cinescope.coconutqa.ru"

LOGIN_DATA = {
  "email": "api1@gmail.com",
  "password": "asdqwe123Q"
}

CURRENT_USER_ID = "734964ec-4d6a-4789-839f-75797141e73e"
# CURRENT_USER_ID менять ТОЛЬКО в зависимости от LOGIN_DATA, иначе сломаются фикстуры и тесты

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "*/*"
}

LOGIN_ENDPOINT = "login"
REGISTER_ENDPOINT = "register"

login_data_list = ["api1@gmail.com", "asdqwe123Q"] # общая константа для случаев, когда нужно залогиниться как админ,
# использовал везде в api_films
