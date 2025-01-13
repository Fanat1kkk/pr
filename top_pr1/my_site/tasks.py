from django.core.mail import send_mail
from django.db.models import Q
from django.conf import settings

from .models import Task, Provider, Order
from .providers import pm

from celery import shared_task


@shared_task
def create_task_in_provider():
    # Бёрет задания из базы данных и создаёт их у провайдера
    tasks_in_work = Task.objects.filter(status=Task.WAITSTART, is_created=False, is_error=False, service__is_published = True)
    if len(tasks_in_work) > 0:
        pm.create_orders(tasks=tasks_in_work)


@shared_task
def cancel_order(order_id: int):
    # Отменет заказ у провайдера
    order = Order.objects.get(order_id=order_id)
    task = order.tasks.all()[0]
    r = pm.cancel_order(order.service.provider.name, task.provider_order_id)
    if 'error' in r:
        task.is_error_canceled = True
        task.error_canceled_msg = r['error']
        task.save()
        

@shared_task
def update_status_orders():
    '''Синхронизирует статусы заказов c провайдорами'''
    providers = Provider.objects.filter(is_active=True)
    # Тут хранятся только ID заказов для запроса к провайдеру {'provider_name': [3124, 45343, 6424]}
    providers_dict = dict()
    # Тут хранятся обьекты Task в которые необходимо внести изменения
    objects_db_tasks_dict = dict()

    tasks_in_work = 0
    for provider in providers:
        tasks = provider.tasks.filter(Q(status=Task.WAITSTART) | Q(status=Task.IN_WORCK) | Q(status=Task.WAITCANCEL), 
                                      is_created=True, is_error=False)
        if tasks.count() > 0:
            objects_db_tasks_dict.update({provider.name: tasks})
            providers_dict.update({provider.name: [task.provider_order_id for task in tasks]})
            tasks_in_work += tasks.count()
    # Если нет активных заданий
    if len(providers_dict) == 0:
        return
    data_providers = pm.update_orders_status(tasks=providers_dict)
    
    if len(data_providers) == 0:
        return
    for provider in data_providers:
        data_tasks = data_providers[provider]
        db_tasks = objects_db_tasks_dict[provider]
        for order_id in data_tasks:
            db_task: Task = db_tasks.get(provider_order_id=int(order_id))
            data_task = data_tasks[order_id]
            print('update_status_orders 5')
            db_task.update_task(data_task)


@shared_task
def send_email_register_user(email: str):
    text = f'''

    Вы успешно зарегистрировались на сайте {settings.BASE_URL}.
    
    Мы подготовили специально для вас промокод со скидкой 10% на первый заказ. Активировать его вы сможете при оформлении заказа.
    
    ВАШ ПРОМОКОД: reg10

    Контакты: 
    Telegram - https://t.me/topprru
    ВКонтакте - https://vk.com/topprru
    '''

    send_mail(subject=f'Регистрация на {settings.BASE_URL}', message=text, from_email=settings.EMAIL_HOST_USER, 
              recipient_list=[email])

@shared_task
def send_email(subject, message, recipient_list):
    send_mail(subject=subject, message=message, from_email=settings.EMAIL_HOST_USER, 
              recipient_list=recipient_list)
