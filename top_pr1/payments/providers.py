from decimal import Decimal
from random import choice
from hashlib import md5, sha1

from django.conf import settings

from my_site.models import Client, Order
from my_site.utils import del_zero
from .models import Transaction, ProviderPay

from requests import Session


class PayBaseProvider:
    name:str
    UNQ:str
    display_name:str
    currency:str = 'RUB' 
    secret:str = ''

    def _gen_tr_id(self):
        # Генерирует ID транзакции
        # Необходимо для платёжных систем
        def valid(n):
            digits = list(map(int, str(n)))
            return digits[0] == digits[-1] and sum(digits) % 2 == 0

        ndigits = 5
        valid_numbers = list(filter(valid, range(10**(ndigits - 1), 10**ndigits)))
        return choice(valid_numbers)

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


class PayFreeCassa(PayBaseProvider):
    name = ProviderPay.FREC
    url = 'https://pay.freekassa.ru/?'
    secret = 'Тема57486'
    secret2 = 'Ксюша57486'
    shop_id = 18167

    def create_pay_profile(self, price: Decimal, client):
        unic_id = self._gen_tr_id()
        price = price
        sign1 = self.sign(price, unic_id)
        sign2 = self.sign2(price, unic_id)
        self.redirect = self._pay_url(price=price, unic_id=unic_id, email=client.email, sign=sign1)
        Transaction.objects.create(unic_id=unic_id, sum=price, client=client, pay_type=Transaction.LK, pay_provider=self.name, sign=sign2, pay_url=self.redirect)

    def create_pay(self, order: Order):
        unic_id = self._gen_tr_id()
        price = order.price
        sign1 = self.sign(price, unic_id)
        sign2 = self.sign2(price, unic_id)
        self.redirect = self._pay_url(price=price, unic_id=unic_id, email=order.client.email, sign=sign1)
        Transaction.objects.create(unic_id=unic_id, sum=price, order=order, client=order.client, pay_provider=self.name, sign=sign2, pay_url=self.redirect)
    
    def pay_status(self, data: dict):
        sign = data['SIGN']
        unic_id = int(data['MERCHANT_ORDER_ID'])
        try:
            transaction = Transaction.objects.get(sign=sign, unic_id=unic_id)
            transaction.paid()
        except Transaction.DoesNotExist:
            return 
        
    def _pay_url(self, price:Decimal = None, sign = None, unic_id = None, email = None):
        return f'{self.url}&m={self.shop_id}&oa={price}&currency={self.currency}&o={unic_id}&s={sign}&em={email}'

    def sign(self, price: Decimal, unic_id: int):
        s = '{shop_id}:{price}:{secret}:{currency}:{unic_id}'.format(shop_id=self.shop_id, price=price, 
                                                                       secret=self.secret, currency=self.currency, unic_id=unic_id)

        return md5(s.encode('utf-8')).hexdigest()
    
    def sign2(self, price: Decimal, unic_id: int):
        s = '{shop_id}:{price}:{secret}:{unic_id}'.format(shop_id=self.shop_id, price=price, 
                                                                       secret=self.secret2, unic_id=unic_id)

        return md5(s.encode('utf-8')).hexdigest()


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
        return f'{self.url}orders/search?email={order.client.email}'



class PayManager:

    def create_pay(self,pay_provider: str,  order: Order = None) -> str:
        if pay_provider == ProviderPay.YOOM:
            pay = PayYoomoney()
            pay.create_pay(order=order)

        elif pay_provider == ProviderPay.FREC:
            pay = PayFreeCassa()
            pay.create_pay(order=order)
        
        elif pay_provider == ProviderPay.PRF:
            pay = PayProfileProvider()
            pay.create_pay(order=order)
        
        return pay.redirect

    def create_pay_profile(self, pay_provider: str, client: Client, price: Decimal):
        if pay_provider == ProviderPay.YOOM:
            pay = PayYoomoney()
            pay.create_pay_profile(client=client, price=price)


        elif pay_provider == ProviderPay.FREC:
            pay = PayFreeCassa()
            pay.create_pay_profile(client=client, price=price)
        
        
        return pay.redirect
        

pm = PayManager()


    
