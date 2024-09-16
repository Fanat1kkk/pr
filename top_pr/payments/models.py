from random import choice

from django.db import models
from django.utils import timezone

from my_site.models import Order, Client

from .tasks import *


def gen_unic_id():
    # Генерирует ID заказа
    def valid(n):
        digits = list(map(int, str(n)))
        return digits[0] == digits[-1] and sum(digits) % 2 == 0

    ndigits = 5
    valid_numbers = list(filter(valid, range(10**(ndigits - 1), 10**ndigits)))
    return choice(valid_numbers)


class ProviderPay():
    FREC = 'FREC'
    YOOM = 'YOOM'
    PRF = 'PRF'

    PROVIDERS = [
        # (FREC, 'FreeCassa'),
        (YOOM, 'Yoommany'),
        (PRF, 'Баланс'),
    ]
                
class TransactionManager(models.Manager):
    
    def create(self, **kwargs):
        '''
        При создании ещё одной транзакции для данного заказа, всем остальным назначается is_active=False
        Тем самым обеспечивает всегда 1 активную трназакцию для заказа
        '''
        trn = super().create(**kwargs)
        for t in self.filter(order=trn.order, is_active=True):
            if t.pk != trn.pk:
                t.is_active = False
                t.save()
        return trn
            

class Transaction(models.Model):
    LK = 'LK'
    OR = 'OR'

    PAY_TYPE = [
        (LK, 'Профиль'),
        (OR, 'Заказ'),
    ]

    client = models.ForeignKey(to=Client, verbose_name='Клиент', related_name='transactions', on_delete=models.CASCADE, null=True)
    unic_id = models.IntegerField(verbose_name='ID транзакции', null=False, blank=False, unique=True, primary_key=True)
    order = models.ForeignKey(to=Order, verbose_name='Заказ', related_name='transactions', on_delete=models.CASCADE, null=True)
    sum = models.DecimalField(verbose_name='Цена', max_digits=8, decimal_places=2)
    pay_provider = models.CharField(verbose_name='Вариант оплаты', max_length=4, choices=ProviderPay.PROVIDERS)
    sign = models.UUIDField(null=True, blank=True)
    pay_url = models.URLField(verbose_name='Адрес оплаты', max_length=200, null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    # Оплата из баланса или оплата через платёжку
    pay_type = models.CharField(verbose_name='Тип оплаты', max_length=2, choices=PAY_TYPE, default=OR, null=True, blank=True,
                                help_text='Если оплата за заказ, то указывает откуда была оплата, платёжка или баланс.')
    # pay_purpose = models.CharField(verbose_name='Цель платежа', max_length=2, default=OR, choices=PAY_TYPE, null=True,
    #                                help_text='Цель платежа, пополнение баланса или оплата заказа')
    # У 1 зака может быть только 1 активная транзакция.
    # Указывает на то активна данная транзакция или нет. 
    is_active = models.BooleanField(default=True)
    date_create = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)
    date_paid = models.DateTimeField(verbose_name='Дата оплаты', null=True)

    # objects = TransactionManager()

    def paid(self):
        '''
        Изменяет статус транзакции на оплачен и добавляет заказ в работу
        '''
        self.is_paid = True
        self.date_paid = timezone.now()

        if self.pay_type == self.OR:
            self._paid_order()
        elif self.pay_type == self.LK:
            self._paid_profile_balance()

        self.save()

        # Отправка писем
        if self.pay_type == self.OR:
            send_email_order_pay.delay(self.pk)
        elif self.pay_type == self.LK:
            send_email_profile_pay.delay(self.pk)
    
    def _paid_profile_balance(self):
        '''
        Подверждения платежа для пополнения баланса
        '''
        self.client.add_balance(sum = self.sum, comment=f'Пополнение: {self.sum} р.')

    def _paid_order(self):
        '''
        Подверждения платежа за заказ
        '''
        self.order.add_in_worck()


    def pay_from_balance(self):
        '''
        Оплата заказа с баланса
        '''
        price = self.order.get_price()
        
        self.order.client.remove_balance(price, comment=f'Заказ: {self.order.order_id}')
        self.paid()

        