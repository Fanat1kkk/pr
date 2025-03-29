from decimal import Decimal
import hashlib
import hmac
import ipaddress
from random import choice
from hashlib import sha1
import uuid

from django.conf import settings

from my_site.models import Client, Order
from .models import Transaction, ProviderPay

from yookassa import Payment, Configuration
from yookassa.payment import PaymentResponse
from yookassa.domain.models.confirmation.response.confirmation_redirect import ConfirmationRedirect
from requests import Session


def pay_variant():
    return [
        {
            'provider': 'YOOK',
            'name': 'Банковская карта',
            'img': 'master-card.svg'
        },
        {
            'provider': 'YOOK',
            'name': 'Система быстрых платежей',
            'img': 'sbp.svg'
        },
        {
            'provider': 'YOOK',
            'name': 'SberPay',
            'img': 'sber.svg'
        },
        {
            'provider': 'YOOK',
            'name': 'ЮMoney',
            'img': 'ymoney.svg'
        }
    ]

    
def pay_variant_profile():
    variants = pay_variant()
    variants.append({
        'provider': 'PRF',
        'name': 'Баланс',
        'img': 'wallet.svg'
    })
    return variants


class PayBaseProvider:
    name:str
    UNQ:str
    display_name:str
    currency:str = 'RUB' 
    secret:str = ''

    def _gen_tr_id(self):
        # Генерирует ID транзакции
        # Необходимо для платёжных систем
        # def valid(n):
        #     digits = list(map(int, str(n)))
        #     return digits[0] == digits[-1] and sum(digits) % 2 == 0

        # ndigits = 5
        # valid_numbers = list(filter(valid, range(10**(ndigits - 1), 10**ndigits)))
        # return choice(valid_numbers)
        return uuid.uuid4()

    def create_pay_profile(self, price: Decimal, client):
        unic_id = self._gen_tr_id()
        price = price
        sign = self.sign(price, unic_id)
        self.redirect = self._pay_url(price=price, unic_id=unic_id)
        print('redirect: ', self.redirect)
        Transaction.objects.create(client=client, unic_id=unic_id, sum=price, pay_type=Transaction.LK, pay_provider=self.name, sign=sign, pay_url=self.redirect)

    def create_pay(self, order: Order):
        unic_id = self._gen_tr_id()
        price = order.price
        sign = self.sign(price=price, unic_id=unic_id)
        self.redirect = self._pay_url(price, unic_id)
        Transaction.objects.create(order=order, unic_id=unic_id, sum=price, client=order.client, pay_provider=self.name, sign=sign, pay_url=self.redirect)

    def pay_status(self):
        pass

    def check_pay(self):
        pass

    def sign(self, *args, **qwargs):
        return 

    def _pay_url(self, *args, **qwargs):
        pass


# class PayFreeCassa(PayBaseProvider):
#     name = ProviderPay.FREC
#     url = 'https://pay.freekassa.ru/?'
#     secret = 'Тема57486'
#     secret2 = 'Ксюша57486'
#     shop_id = 18167

#     def create_pay_profile(self, price: Decimal, client):
#         unic_id = self._gen_tr_id()
#         price = price
#         sign1 = self.sign(price, unic_id)
#         sign2 = self.sign2(price, unic_id)
#         self.redirect = self._pay_url(price=price, unic_id=unic_id, email=client.email, sign=sign1)
#         Transaction.objects.create(unic_id=unic_id, sum=price, client=client, pay_type=Transaction.LK, pay_provider=self.name, sign=sign2, pay_url=self.redirect)

#     def create_pay(self, order: Order):
#         unic_id = self._gen_tr_id()
#         price = order.price
#         sign1 = self.sign(price, unic_id)
#         sign2 = self.sign2(price, unic_id)
#         self.redirect = self._pay_url(price=price, unic_id=unic_id, email=order.client.email, sign=sign1)
#         Transaction.objects.create(unic_id=unic_id, sum=price, order=order, client=order.client, pay_provider=self.name, sign=sign2, pay_url=self.redirect)
    
#     def pay_status(self, data: dict):
#         sign = data['SIGN']
#         unic_id = int(data['MERCHANT_ORDER_ID'])
#         try:
#             transaction = Transaction.objects.get(sign=sign, unic_id=unic_id)
#             transaction.paid()
#         except Transaction.DoesNotExist:
#             return 
        
#     def _pay_url(self, price:Decimal = None, sign = None, unic_id = None, email = None):
#         return f'{self.url}&m={self.shop_id}&oa={price}&currency={self.currency}&o={unic_id}&s={sign}&em={email}'

#     def sign(self, price: Decimal, unic_id: int):
#         s = '{shop_id}:{price}:{secret}:{currency}:{unic_id}'.format(shop_id=self.shop_id, price=price, 
#                                                                        secret=self.secret, currency=self.currency, unic_id=unic_id)

#         return md5(s.encode('utf-8')).hexdigest()
    
#     def sign2(self, price: Decimal, unic_id: int):
#         s = '{shop_id}:{price}:{secret}:{unic_id}'.format(shop_id=self.shop_id, price=price, 
#                                                                        secret=self.secret2, unic_id=unic_id)

#         return md5(s.encode('utf-8')).hexdigest()


class PayYoomoney(PayBaseProvider):
    name = ProviderPay.YOOM
    url = 'https://yoomoney.ru/quickpay/confirm.xml'
    secret = 'ViXiegKHV3Q/F+T861yz1JLO'
    shop_id = 18167
    wallet = '4100116591511963'
    
    def pay_status(self, data: dict):
        print('YOOMANY: ', data)
        if not self.test_secret(data=data):
            print('test secret: ', False)
            return False
        try:
            order_id = data.get('label', 1)
            order_id = 1 if order_id == '' else int(order_id) if order_id.isdigit() else 1
            transaction = Transaction.objects.get(unic_id=order_id)
            transaction.paid()
        except Transaction.DoesNotExist:
            print('not tr: ', order_id)
            return False

    def _pay_url(self, price:Decimal, unic_id) -> dict:
        data = {
            'receiver': self.wallet,
            'quickpay-form': 'shop',
            'targets': 'Оплата чегото в top-pr',
            'paymentType': 'AC',
            'sum': price,
            'formcomment': 'Оплата в top-pr.ru',
            'successURL': 'https://top-pr.ru/',
            'label': unic_id
        }

        with Session().post(self.url, data, allow_redirects=False) as resp:
            return resp.headers['Location']
        
    def test_secret(self, data: dict):

        notification_type = data['notification_type']
        operation_id = data['operation_id']
        amount = data['amount']
        currency = data['currency']
        datetime = data['datetime']
        sender = data['sender']
        codepro = data['codepro']
        notification_secret = self.secret
        label = data['label']
        sha1_hash = data['sha1_hash']

        s = sha1('{notification_type}&{operation_id}&{amount}&{currency}&{datetime}&{sender}&{codepro}&{notification_secret}&{label}'.format(
               notification_type = notification_type,
               operation_id = operation_id,
               amount = amount,
               currency = currency,
               datetime = datetime,
               sender = sender,
               codepro = codepro,
               notification_secret = notification_secret,
               label = label
           ).encode('utf-8')).hexdigest()
        
        if sha1_hash != s:
            print('sha1_hash: ', sha1_hash)
            print('s: ', s)

        return sha1_hash == s or False 


class PayYookassa(PayBaseProvider):
    name = ProviderPay.YOOM 
    ALLOWED_IPS = [
        "185.71.76.0/27",
        "185.71.77.0/27",
        "77.75.153.0/25",
        "77.75.156.11",
        "77.75.156.35",
        "77.75.154.128/25",
        "2a02:5180::/32",
    ]

    def is_valid_ip(self, ip):
        """Проверяет, входит ли IP в разрешенные диапазоны."""
        for allowed_ip in self.ALLOWED_IPS:
            if ipaddress.ip_address(ip) in ipaddress.ip_network(allowed_ip, strict=False):
                return True
        return False

    def create_pay_profile(self, price: Decimal, client):
        unic_id = uuid.uuid4()
        price = price
        payment = self._pay_url(price=price, client=client, unic_id=unic_id, comment='Пополнение https://top-pr.ru/')
        self.redirect = payment.confirmation.confirmation_url
        Transaction.objects.create(client=client, unic_id=unic_id, p_unic_id=payment.id, sum=price, pay_type=Transaction.LK, pay_provider=self.name, pay_url=self.redirect)
        
    def verify_yookassa_signature(self, request):
        return self.is_valid_ip(request.META.get('HTTP_X_FORWARDED_FOR', ''))

    def pay_status(self, data: dict):
        print('YOOKASSA: ', data)
        try:
            transaction_id = data['object']['id']
            transaction = Transaction.objects.get(p_unic_id=transaction_id)
            transaction.paid()
        except Transaction.DoesNotExist:
            print('not tr: ', transaction_id)
            return False

    def create_pay(self, order: Order):
        unic_id = self._gen_tr_id()
        price = order.price
        sign = self.sign(price=price, unic_id=unic_id)
        payment = self._pay_url(price, order.client, unic_id, comment=f'Полата заказа: № {order.order_id}')
        self.redirect = payment.confirmation.confirmation_url
        Transaction.objects.create(order=order, unic_id=unic_id, p_unic_id=payment.id, sum=price, client=order.client, pay_provider=self.name, sign=sign, pay_url=self.redirect)

    def _pay_url(self, price:Decimal, client, unic_id, comment) -> dict:

        payment: PaymentResponse = Payment.create({"amount": {
                                        "value": price,
                                        "currency": "RUB"
                                        },
                                        "confirmation": {
                                            "type": "redirect",
                                            "return_url": "https://top-pr.ru/profile/"
                                        },
                                        "capture": True,
                                        "description": comment,
                                        "receipt": {
                                            "customer": {
                                                "email": client.email,  # Обязательно добавь email или телефон покупателя
                                            },
                                            "items": [
                                                {
                                                    "description": comment,
                                                    "quantity": "1.00",
                                                    "amount": {
                                                        "value": price,
                                                        "currency": "RUB"
                                                    },
                                                    "vat_code": "1"  # 1 – без НДС (для самозанятых)
                                                }
                                            ]
                                        }
                                    }, unic_id)
        return payment


class PayProfileProvider(PayBaseProvider):
    name = ProviderPay.PRF
    url = 'http://127.0.0.1:8000/' if settings.DEBUG  else 'https://top-pr.ru/'
    

    def create_pay(self, order: Order):
        price = order.price
        unic_id = self._gen_tr_id()
        sign = self.sign(order.price, order.order_id, secret=self.secret)
        self.redirect = self._pay_url(order, sign)
        Transaction.objects.create(unic_id=unic_id, sum=price, order=order, client=order.client, pay_provider=self.name, sign=sign, pay_url=self.redirect)

    def pay_status(self):
        pass

    def check_pay(self):
        pass

    def sign(self, *args, **qwargs):
        return 

    def _pay_url(self, order:Order, sign):
        return f'{self.url}profile/'


class PayManager:

    def create_pay(self,pay_provider: str,  order: Order = None) -> str:
        if pay_provider == ProviderPay.YOOM:
            pay = PayYoomoney()
            pay.create_pay(order=order)
        
        elif pay_provider == ProviderPay.PRF:
            pay = PayProfileProvider()
            pay.create_pay(order=order)

        elif pay_provider == ProviderPay.YOOK:
            pay = PayYookassa()
            pay.create_pay(order=order)
        
        return pay.redirect

    def create_pay_profile(self, pay_provider: str, client: Client, price: Decimal):
        if pay_provider == ProviderPay.YOOM:
            pay = PayYoomoney()
            pay.create_pay_profile(client=client, price=price)
        
        elif pay_provider == ProviderPay.YOOK:
            pay = PayYookassa()
            pay.create_pay_profile(client=client, price=price)
        
        
        return pay.redirect
        

pm = PayManager()


    
