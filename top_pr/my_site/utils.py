from decimal import Decimal


def del_zero(num: Decimal):
    return num
    # num = str(num.quantize(Decimal('1.00')))
    # if num[-2:] == '00':
    #     return num[:-3]
    # elif num[-1:] == '0':
    #     return num[:-1]
    # return num
    

