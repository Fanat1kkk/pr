import secrets
import string
from random import randint


def random_password():
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(randint(9, 14)))


print(random_password())