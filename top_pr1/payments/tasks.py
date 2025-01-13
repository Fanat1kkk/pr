from django.core.mail import send_mail
from django.conf import settings

from celery import shared_task

from my_site.utils import del_zero


@shared_task
def send_email_order_pay(transaction_id: int):
    from .models import Transaction
    print('send_email_order_pay')
    t = Transaction.objects.get(pk = transaction_id)
    order = t.order

    text = f'''
    Вы оформили {order.service.sub_cat.name} {order.service.category.cat_name}

    ID: {order.order_id}
    Цена: {del_zero(order.price)} руб.
    Ссылка: {order.task_url}
    Количество: {order.count}

    Тут вы можете следить за заказами: https://top-pr.ru/orders/search?email={order.client.email}

    В случаи отмены заказа все средства вернутся на баланс вашего аккаунта.

    Контакты: 
    Telegram - https://t.me/topprru
    ВКонтакте - https://vk.com/topprru
    '''

    send_mail(subject='Заказ оформлен', message=text, from_email=settings.EMAIL_HOST_USER, 
              recipient_list=[order.client.email])


@shared_task
def send_email_profile_pay(transaction_id: int):
    from .models import Transaction
    
    t = Transaction.objects.get(pk = transaction_id)
    order = t.order

    text = f'''

    Вы пополнили баланс на {del_zero(t.sum)}

    Контакты: 
    Telegram - https://t.me/topprru
    ВКонтакте - https://vk.com/topprru
    '''

    send_mail(subject='Пополнение баланса', message=text, from_email=settings.EMAIL_HOST_USER, 
              recipient_list=[order.client.email])