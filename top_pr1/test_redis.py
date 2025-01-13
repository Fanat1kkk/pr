from decimal import Decimal

def del_zero(num: Decimal) -> str:
    if isinstance(num, Decimal):
        # Убираем незначащие нули, не используя научную нотацию
        num = num.normalize()

        # Преобразуем число в строку с фиксированной точностью
        # Если у числа есть дробная часть, оставляем её
        # Если дробной части нет, выводим как целое
        return format(num, 'f').rstrip('0').rstrip('.')
    return num

print(del_zero(del_zero(11.000)))