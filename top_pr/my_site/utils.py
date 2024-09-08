from decimal import Decimal
import secrets
import string
from random import randint


def generate_password():
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(randint(9, 14)))

def del_zero(num: Decimal):
    return num
    # num = str(num.quantize(Decimal('1.00')))
    # if num[-2:] == '00':
    #     return num[:-3]
    # elif num[-1:] == '0':
    #     return num[:-1]
    # return num
    

