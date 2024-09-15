
import random
from decimal import Decimal, ROUND_HALF_UP

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ObjectDoesNotExist

from allauth.utils import generate_unique_username
from allauth.account.models import EmailAddress
from ckeditor.fields import RichTextField

from .utils import del_zero, generate_password
from .exceptions import BalanceException


SUBCATEGORIES = (
    ('SUB', 'Подписчики'),
    ('UCH', 'Участники чата'),
    ('VIWS', 'Просмотры'),
    ('REA', 'Реакции'),
    ('LIK', 'Лайки'),
    ('SHA', 'Поделиться'),
    ('COM', 'Комментарии'),
    ('REP', 'Репосты'),
)

IMG_LINKS = (
    ('TEL', 'telegram.svg'),
    ('VK', 'vk.svg'),
    ('TIK', 'tiktok.svg'),
    ('YOTB', 'youtube.svg'),
    ('TWIT', 'twitter.svg'),
    ('OK', 'ok.svg'),
    ('INST', 'instagram.svg'),
    ('CLIN', 'c_link.svg'),
    ('STAR', 'c_star.svg'),
    ('EYE', 'eye.svg'),
    ('HEAR', 'heart.svg'),
    ('IGTV', 'igtv.svg'),
    ('LIKE', 'likee.svg'),
    ('REVO', 'record_voice.svg'),
    ('SAVE', 'save.svg'),
    ('SHOW', 'show.svg'),
    ('THUP', 'thumb-up.svg'),
    ('USER', 'user.svg'),
    ('USES', 'users.svg'),
)

class BalanceTransaction(models.Model):
    R = 'R'
    A = 'A'
    OPERATIONS = [
        (R, 'Снятие'),
        (A, 'Поступлениу'),
    ]
    client = models.ForeignKey(to='Client', related_name='balansh', on_delete=models.CASCADE)
    sum = models.DecimalField(verbose_name='Баланс', max_digits=8, decimal_places=2, default=0)
    operation = models.CharField(verbose_name='Операция', choices=OPERATIONS, default=A, max_length=1)
    comment = models.CharField(verbose_name='Комментарий', max_length=60, null=True, blank=True)


class ClientManager(UserManager):

    def get_or_creat_user_from_email(self, email, **kwargs) -> models.Model:
        try: 
            email = EmailAddress.objects.get(email__iexact=email)
            return email.user
        except EmailAddress.DoesNotExist:
            try:
                user = self.get(email=email)
            except self.model.DoesNotExist:
                username = generate_unique_username([email, 'username', 'user'])
                password = generate_password()
                user: Client = self.model(username=username, password=password, email=email, **kwargs)
                user.set_password(password)
                user.save()
                EmailAddress.objects.create(user=user, email=email, primary=True)

                from .tasks import send_email
                text = f'''
                Поздравляем с оформлением вашего первого заказа на {settings.BASE_URL}!
                
                Мы создали для вас аккаунт для того чтоб вам было удобнее пользоваться нашим сервисом.
                Так-же специально для вас мы подготовили промокод 10% на следующий заказ - reg10

                Ваш пароль: {password}
                Ваш промокод: reg10

                В случаи не выполнения заказа по какой либо из причин, средства будут начислены на ваш баланс.

                Наши контакты:
                Telegram - https://t.me/topprru
                ВКонтакте - https://vk.com/topprru
                '''
                send_email.delay(f'Ваш пароль {settings.BASE_URL}', text, 
                                  recipient_list=[email])
                
        return user


class Client(AbstractUser):
    balance = models.DecimalField(verbose_name='Баланс', max_digits=8, decimal_places=2, default=0)
    date_last_active = models.DateTimeField(verbose_name='Дата последней активности', auto_now=True)

    objects: ClientManager = ClientManager()

    @property
    def get_id(self):
        return self.pk + 4000

    def add_balance(self, sum: Decimal, comment: str = None,  save: bool=True):
        self.balance += sum

        BalanceTransaction.objects.create(client=self, sum=sum, operation=BalanceTransaction.A, comment=comment)

        if save:
            self.save()
        

    def remove_balance(self, sum: Decimal, comment: str = None, save: bool=True):
        print(self.username, '\n', self.email)
        print('self.balance: ', self.balance , '\n', 'sum: ', sum)
        if self.balance < sum:
            raise BalanceException('Не достаточно средст на балансе')
        self.balance -= sum

        BalanceTransaction.objects.create(client=self, sum=sum, operation=BalanceTransaction.R, comment=comment)

        if save:
            self.save()

    @property
    def get_balance(self):
        return del_zero(self.balance)
    

    def email_verified(self):
        pass

    def __str__(self) -> str:
        return self.email

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'


class Category(models.Model):
    cat_name = models.CharField(verbose_name='Название', max_length=30)
    sub_cat = models.ManyToManyField('Subcategory', related_name='categories')
    img = models.CharField(verbose_name='Картинка', max_length=4, choices=IMG_LINKS)

    def __str__(self) -> str:
        return self.cat_name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Provider(models.Model):
    name = models.CharField(verbose_name='Название', max_length=40)
    balance = models.DecimalField(verbose_name='Баланс', max_digits=8, decimal_places=2, default=0)
    api_url = models.CharField(max_length=150)
    is_active = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Провайдер'
        verbose_name_plural = 'Провайдеры'


class CustomerReview(models.Model):
    CHOISES_RATING = [
        ('1', '1',),
        ('2', '2',),
        ('3', '3',),
        ('4', '4',),
        ('5', '5',)
    ]
    client = models.ForeignKey(to=Client, related_name='review', verbose_name='Отзыв', on_delete=models.CASCADE)
    order = models.OneToOneField(to='Order', related_name='review', verbose_name='Заказ', on_delete=models.CASCADE)
    service = models.ForeignKey(to='Service', related_name='review', verbose_name='Услуга', on_delete=models.CASCADE)
    rating_speed = models.CharField(verbose_name='Скорость накрутки', default=CHOISES_RATING[4], max_length=1)
    rating_acc = models.CharField(verbose_name='Качество аккаунтов', default=CHOISES_RATING[4], max_length=1)
    comment = models.CharField(verbose_name='Комментарий', null=True, blank=True, max_length=150)
    
    class Meta:
        verbose_name='Отзыв'
        verbose_name_plural = 'Отзывы'


class Service(models.Model):

    name = models.CharField(verbose_name='Название', max_length=30)
    category = models.ForeignKey(Category, verbose_name='Категория', related_name='services', on_delete=models.CASCADE)
    sub_cat = models.ForeignKey('Subcategory', verbose_name='Подкатегория', related_name='services', on_delete=models.CASCADE)
    service_id = models.IntegerField(verbose_name='Сервис ID', null=False, unique=True)
    min_count = models.IntegerField(verbose_name='Минимум')
    max_count = models.IntegerField(verbose_name='Максимум')
    #Скорость накрутки
    speed = models.IntegerField(verbose_name='Скорость накрутки', default=5)
    #Оценка качества
    quality = models.IntegerField(verbose_name='Качество', default=5)
    text_info = RichTextField(verbose_name='Инфо', null=True, blank=True)
    # Цена за 1000 штук
    price = models.DecimalField(verbose_name='Цена за 1000 шт.', max_digits=8, decimal_places=2)
    percent = models.IntegerField(verbose_name='Процент накрутки', default=50)
    provider = models.ForeignKey(Provider, verbose_name='Провайдер', related_name='services', on_delete=models.CASCADE)
    provider_service_id = models.IntegerField(verbose_name='Сервис ID провайдера', null=False)
    is_published = models.BooleanField(verbose_name='Активна?', default=False)
    is_cancellation = models.BooleanField(verbose_name='Есть отмена?', default=False)
    
    def price_per_one(self) -> Decimal:
        '''
        Возвращает цену за 1 штуку с учетом накрученных процентов
        '''
        r = (Decimal('1') + Decimal(self.percent) / Decimal('100')) * (self.price / Decimal('1000'))
        return r.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)

    def full_name(self):
        return f'{self.sub_cat.name} {self.category.cat_name}'

    def __str__(self) -> str:
        return f'{self.name} {self.category}'
    
    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'


class Subcategory(models.Model):
    name = models.CharField(verbose_name='Назвение', max_length=35, unique=True)
    img = models.CharField(verbose_name='Картинка', max_length=4, choices=IMG_LINKS, null=True, blank=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Подкатегория'
        verbose_name_plural = 'Подкотегории'


class PromoCode(models.Model):
    code = models.CharField(verbose_name='Код', unique=True, primary_key=True, max_length=7)
    discount_percent = models.IntegerField(verbose_name='Процент скидки', default=0)
    max_number_uses = models.IntegerField(verbose_name='Макс кол-во гошений', default=1)
    number_uses = models.IntegerField(verbose_name='Кол-во гошений', blank=False, default=0)
    is_multiple = models.BooleanField(verbose_name='Многоразовый')
    date_end = models.DateTimeField(verbose_name='Дата окончания', null=True)
    date_create = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)
    date_edit = models.DateTimeField(verbose_name='Дата изменения', auto_now=True)

    def activate(self):
        if self.is_active():
            self.number_uses += 1
            self.save()

    def is_active(self):
        # Првоеряет актуальный ли промокод
        if not self.is_multiple:
            # Если не многоразовый
            if self.max_number_uses <= self.number_uses:
                return False
        
        if self.date_end < timezone.now():
            return False
        
        return True

    def calc(self, price: Decimal) -> Decimal:
        if not self.is_active():
            return price
        price -= ((Decimal(str(self.discount_percent)) / Decimal('100')) * price)
        return price.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)

    def __str__(self) -> str:
        return f'Скидка {self.discount_percent}%'


class ABSOrderTask(models.Model):
    IN_WORCK = 'INWOR'
    NO_PAY = 'NOPAY'
    BLOCK = 'BLOCK'
    CANC = 'CANC'
    COMPLITE = 'COMPL'
    # Ожидает старта
    WAITSTART = 'WST'
    # Ожидает отмены
    WAITCANCEL = 'WCL'
    # Выполнен частично
    PARTIAL = 'PART'
    # Для теста
    FAIL = 'FAIL'

    '''
    likehub: 
        Pending - Ожидание
        Cancellation process - ОТМЕНЯЕТСЯ
    '''


    STATUS = [
        (IN_WORCK, 'В работе'),
        (NO_PAY, 'Не оплачен'),
        (BLOCK, 'Заблокирован'),
        (COMPLITE, 'Выполнено'),
        (CANC, 'Отменён'),
        (WAITSTART, 'Ожидает'),
        (WAITCANCEL, 'Отменяется'),
        (PARTIAL, 'Частично'),
        (FAIL, 'Ошибка')
    ]

    order_id = models.IntegerField(verbose_name='ID заказа', null=False, blank=False, unique=True, primary_key=True)
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, verbose_name='Сервис')
    status = models.CharField(verbose_name='Статус', choices=STATUS, default=NO_PAY, max_length=5)
    count = models.IntegerField(verbose_name='Количество', null=False)
    end_count = models.IntegerField(verbose_name='Выполнено', default=0)
    start_count = models.IntegerField(verbose_name='Кол-во до старта', default=0)
    task_url = models.CharField(verbose_name='Ссылка', max_length=150, null=False)
    date_create = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)
    date_edit = models.DateTimeField(verbose_name='Дата изменения', auto_now=True)

    class Meta:
        abstract = True


class Order(ABSOrderTask):

    client = models.ForeignKey(verbose_name='Клиент', to=Client, on_delete=models.SET_NULL, null=True, related_name='orders')
    promocode = models.ForeignKey(verbose_name='Промокод', to='PromoCode', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    price = models.DecimalField(verbose_name='Цена', max_digits=8, decimal_places=2)
    email = models.EmailField(verbose_name='Емаил', max_length=60, null=True, blank=False)
    is_paid = models.BooleanField(verbose_name='Оплачен', default=False)

    def add_in_worck(self) -> bool:
        ''' 
        Метода запукает заказ в работу.
        Создаёт Task для текущего заказа.
        Должен вызываться только после подтверждённой оплаты
        '''
        if self.status == self.WAITSTART:
            return True
            
        self.is_paid = True
        self.status = self.WAITSTART

        Task.create_task(order=self)

        self.save()
        
        return True


    def set_status(self, task_status: ABSOrderTask, save: bool = False):
        'Изменяет статус заказа в зависимости от статуса Task'
        if task_status == self.WAITSTART:
            self.status == self.IN_WORCK
        else:
            self.status = task_status

        if save:
            self.save()

        # if update_tasks:
        #     for task in self.tasks:
        #         task.status = status
        #         task.save()
        
        # self.status = status
        # self.save()

    def gen_order_id(self):
        # Генерирует ID заказа
        def valid(n):
            digits = list(map(int, str(n)))
            return digits[0] == digits[-1] and sum(digits) % 2 == 0

        ndigits = 5
        valid_numbers = list(filter(valid, range(10**(ndigits - 1), 10**ndigits)))
        return random.choice(valid_numbers)

    def calc_price(self, save=True) -> Decimal:
        # Цена за 1 штуку с учётом накрученных процентов и промокодом
        price_per_one = self.service.price_per_one()
        price = price_per_one * Decimal(str(self.count))
        # Если активный промокод
        if self.promocode:
            price = self.promocode.calc(price)
            
        print('-'*10)
        print(f'self.price: {self.price}\nprice: {price}')
        print('-'*10)
        # Запись в БД если цена изменилась
        if self.price != price:
            self.price = price
            if save:
                self.save()

        return price

    def get_price(self) -> Decimal:
        price = self.calc_price(save=False)
        return price

    def get_price_per_one(self) -> Decimal:
        price = self.get_price()
        return price/self.count

    def get_price_end_count(self) -> Decimal:
        price = self.get_price_per_one()
        return price*self.end_count

    def get_price_end_count_from_display(self) -> Decimal:
        return del_zero(self.get_price_end_count())

    def to_dict(self) -> dict:
        return {
            'order_id': self.order_id,
            'service': f'{self.service.name} {self.service.category.cat_name}',
            'count': self.count,
            'task_url': self.task_url,
            'email': self.email
        }

    @property
    def transaction(self):
        '''
        Возвращает активную транзацию
        '''
        try:
            return self.transactions.last()
        except ObjectDoesNotExist:
            return
    
    def __str__(self) -> None:
        return f'Заказ {self.order_id}'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-date_create']


class Task(ABSOrderTask):

    order: Order = models.ForeignKey(Order, related_name='tasks', verbose_name='Заказы', on_delete=models.CASCADE, null=True)
    provider = models.ForeignKey(Provider, on_delete=models.SET_NULL, null=True, related_name='tasks', verbose_name='Провайдер')
    # ID заказа у провайдера
    provider_order_id = models.IntegerField(verbose_name='Провайдер ID заказа', null=True)
    # Создано ли задание у правайдера
    is_created = models.BooleanField(default=False)
    # Ошибка которую вернул провайдер
    is_error = models.BooleanField(default=False)
    # Ошибка которую вернул провайдер
    error_pr = models.TextField(verbose_name='Ошибка от провайдера', null= True, blank=True)

    # Была ли ошибка при отмене заказа
    is_error_canceled = models.BooleanField(default=False)
    error_canceled_msg = models.CharField(verbose_name='Ошибка от провайдера', null= True, blank=True, max_length=150)

    @classmethod
    def create_task(cls, order: Order) -> 'Task':
        task = cls.objects.create(order=order, 
                                  order_id=order.order_id,
                                  status = order.status,
                                  service = order.service,
                                  count = order.count,
                                  provider = order.service.provider,
                                  task_url = order.task_url)
        return task

    def _set_status(self, status: ABSOrderTask, save: bool = False, order_save: bool = False):
        self.status = status
        self.order.set_status(task_status=status, save=order_save)
        if save:
            self.save()

    def provider_error(self, error_text: str) -> None:
        ''' Изменяет статус задания, если провайдер вернул ошибку '''
        self.error_pr = error_text
        self.is_error = True
        self.save()
        self.order.set_status(self.CANC, save=True)

    def provider_ok(self, order_id: int) -> None:
        self.provider_order_id = order_id
        self.is_created = True
        self.save()

    def return_balance(self):
        '''
        Возвращает на баланс клиента деньги за оставшиеся не выполненое кол-во
        '''
        remains = self.count - self.end_count
        price = self.order.get_price_per_one()
        print('Возврат: ', price*remains)
        self.order.client.add_balance(price*remains, comment=f'Возврат заказ: {self.order.order_id}')


    def update_task(self, data_from_provider: dict):
        print('data: ', data_from_provider)
        flag_save_task = False
        flag_save_order = False

        # Обновление Task
        if self.start_count == 0:
            flag_save_task = True
            self.start_count =  data_from_provider['start_count']

        if self.count-self.end_count != data_from_provider['remains']:
            flag_save_task = True
            self.end_count = self.count - data_from_provider['remains']
            flag_save_order = True
            self.order.end_count = self.end_count

        if self.status != data_from_provider['status']:
            flag_save_task = True
            flag_save_order = True
            self._set_status(status=data_from_provider['status'])
            # Если статус изменился на CANCEL or BLOCK or PARTIAL и задание не закончено на бланс возвращаются средства за остаток
            if (self.status == self.BLOCK or self.status == self.CANC or self.status == self.PARTIAL) and ((self.count - self.end_count) > 0):
                self.return_balance()

        # Обновление Order
        if self.order.start_count == 0:
            flag_save_order = True
            self.order.start_count = self.start_count

        # Запись в БД
        if flag_save_task:
            self.save()
        if flag_save_order:
            self.order.save()

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
