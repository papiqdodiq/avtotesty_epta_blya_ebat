# <a class="text-3xl" href="/">Cinescope</a>:
self.home_button = "a[href="/" and text()='Cinescope']"
# И для остальных получим что-то вроде:
self.all_movies_button = "a[href='/movies' and text()='Все фильмы']"
self.full_name_input = "input[name='fullName']"
self.email_input = "input[name='email']"
self.password_input = "input[name='password']"
self.repeat_password_input = "input[name='passwordRepeat']"
self.register_button = "button[data-qa-id='register_submit_button']"
self.sign_button = "a[href='/login' and text()='Войти']"

# Или же можем воспользоваться генератором (playwright codegen) как мы говорили выше:
# page.goto("https://dev-cinescope.coconutqa.ru/register")
# page.get_by_role("link", name="Cinescope").click()
# page.get_by_role("link", name="Все фильмы").click()
# page.get_by_role("textbox", name="Имя Фамилия Отчество").click()
# page.get_by_role("textbox", name="Email").click()
# page.get_by_role("textbox", name="Пароль", exact=True).click()
# page.get_by_role("textbox", name="Повторите пароль").click()
# page.get_by_role("link", name="Войти").click()
# page.goto("https://dev-cinescope.coconutqa.ru/login")
# page.get_by_role("textbox", name="Email").click()
# page.get_by_role("textbox", name="Пароль").click()
# page.get_by_role("button", name="Войти").click()
# В таком случае мы получим подобный код:
self.home_btn = page.get_by_role("link", name="Cinescope").click()
self.all_movies_button = page.get_by_role("link", name="Все фильмы").click()
self.full_name_input = page.get_by_role("textbox", name="Имя Фамилия Отчество").click()
self.email_input = page.get_by_role("textbox", name="Email").click()
self.password_input = page.get_by_role("textbox", name="Пароль", exact=True).click()
self.repeat_password_input = page.get_by_role("textbox", name="Повторите пароль").click()
self.register_button = page.get_by_role("button", name="Зарегистрироваться").click()
self.sign_button = page.get_by_role("link", name="Войти").click()