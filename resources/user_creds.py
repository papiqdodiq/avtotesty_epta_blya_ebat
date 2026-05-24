import os
from dotenv import load_dotenv

# у меня пайтон .env не находит при тестах, поэтому без этого
# class SuperAdminCreds:
#     USERNAME = os.getenv('SUPER_ADMIN_USERNAME')
#     PASSWORD = os.getenv('SUPER_ADMIN_PASSWORD')
# class AdminCreds:
#     USERNAME = os.getenv('ADMIN_USERNAME')
#     PASSWORD = os.getenv('ADMIN_PASSWORD')

class SuperAdminCreds:
    USERNAME = 'api1@gmail.com'
    PASSWORD = 'asdqwe123Q'

class AdminCreds:
    USERNAME = 'abobik228@email.com'
    PASSWORD = 'aboba1488228ABOBA'