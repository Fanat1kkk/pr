from decimal import Decimal, ROUND_HALF_UP
import secrets
import string
from random import randint


def generate_password():
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(randint(9, 14)))

def del_zero(value: Decimal) -> str:
    if isinstance(value, Decimal):
        # Определяем максимальное количество знаков после запятой (например, 10)
        # .quantize() сохраняет точность и не переводит в научную нотацию
        value = value.quantize(Decimal('1.0000'))  # 4 знака после запятой, можно изменить

        # Преобразуем в строку
        result = format(value, 'f')

        # Убираем лишние нули в конце дробной части
        return result.rstrip('0').rstrip('.') if '.' in result else result
    return value
    

