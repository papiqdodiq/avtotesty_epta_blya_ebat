import pytest
from db_models.accounts_transaction_template import AccountTransactionTemplate
from sqlalchemy.orm import Session
from utils.data_generator import DataGenerator
from db_models.movie import MovieDBModel


class TestFunctions:

    def test_delete_movie(self, api_manager_admin, db_session, db_helper):
        film = MovieDBModel(**DataGenerator.generate_film_data())
        db_session.add(film)
        db_session.commit()
        db_session.refresh(film)

        assert db_helper.get_movie_by_name(film.name)
        movie_id = film.id

        api_manager_admin.films_api.delete_movie(movie_id)
        assert db_helper.get_movie_by_name(film.name) is None

    @staticmethod
    def test_accounts_transaction_template(db_session: Session):
        # ============= Подготовка к тесту =============
        # Создаем новые записи в базе данных (чтоб точно быть уверенными что в базе присутствуют данные для тестирования)
        stan_balance = 1000
        bob_balance = 500
        stan = AccountTransactionTemplate(user=f"Stan_{DataGenerator.generate_random_string(10)}", balance=stan_balance)
        bob = AccountTransactionTemplate(user=f"Bob_{DataGenerator.generate_random_string(10)}", balance=bob_balance)

        # Добавляем записи в сессию
        db_session.add(stan)
        db_session.add(bob)
        # Фиксируем изменения в базе данных
        db_session.commit()

        def transfer_money(session, from_account, to_account, amount):
            # пример функции выполняющей транзакцию
            # представим что она написана на стороне тестируемого сервиса
            # и вызывая метод transfer_money, мы какбудтобы делем запрос в api_manager.movies_api.transfer_money
            """
            Переводит деньги с одного счета на другой.
            :param session: Сессия SQLAlchemy.
            :param from_account: ID счета, с которого списываются деньги.
            :param to_account: ID счета, на который зачисляются деньги.
            :param amount: Сумма перевода.
            """
            # Получаем счета
            from_account = session.query(AccountTransactionTemplate).filter_by(user=from_account).one()
            to_account = session.query(AccountTransactionTemplate).filter_by(user=to_account).one()

            # Проверяем, что на счете достаточно средств
            if from_account.balance < amount:
                raise ValueError("Недостаточно средств на счете")

            # Выполняем перевод
            from_account.balance -= amount
            to_account.balance += amount

            # Сохраняем изменения
            session.commit()

        # ============= Тест =============
        # Проверяем начальные балансы
        assert stan.balance == stan_balance
        assert bob.balance == bob_balance

        try:
            # Выполняем перевод 200 единиц от stan к bob
            value = 600
            transfer_money(db_session, from_account=bob.user, to_account=stan.user, amount=value)

            # Проверяем, что балансы изменились
            assert bob.balance == bob.balance - value
            assert stan.balance == stan.balance + value

        except Exception as e:
            # Если произошла ошибка, откатываем транзакцию
            db_session.rollback()  # откат всех введеных нами изменений
            pytest.fail(f"Ошибка при переводе денег: {e}")

        finally:
            # Удаляем данные для тестирования из базы
            db_session.delete(stan)
            db_session.delete(bob)
            # Фиксируем изменения в базе данных
            db_session.commit()

    def test_db_requests1(self, super_admin, db_helper, created_test_user): # создание через бд
        assert created_test_user == db_helper.get_user_by_id(created_test_user.id)
        assert db_helper.user_exists_by_email(created_test_user.email)

    def test_db_requests2(self, super_admin, db_helper, create_user_pydantic): # создание через запрос и пайдентик модель
        user_from_db = db_helper.get_user_by_id(create_user_pydantic["id"])
        assert create_user_pydantic["id"] == user_from_db.id
        assert db_helper.user_exists_by_email(create_user_pydantic["email"])