from django.db import models
from django.utils import timezone

from my_site.models import Client

from .exceptions import CuponException


class Cupon(models.Model):
    users = models.ManyToManyField(
        to=Client, related_name='cupons', verbose_name='Клиент', blank=True)
    owner_id = models.IntegerField(verbose_name='ID владельца', null=True, blank=True, 
                                   help_text='4000+ID для кого предназначен купон')
    code = models.CharField(verbose_name='Код', max_length=7, unique=True)
    bonus = models.DecimalField(
        verbose_name='Бонус', max_digits=8, decimal_places=3)
    max_uses = models.IntegerField(
        verbose_name='Максимальное кол-во гошений', default=1)
    current_uses = models.IntegerField(
        verbose_name='Кол-во гошений', default=0)
    multi_use = models.BooleanField(verbose_name='Мнократное использование',
                                    help_text='Можно использовать много раз, разными клиентами')
    date_create = models.DateTimeField(
        verbose_name='Дата создания', auto_now_add=True)
    date_end = models.DateTimeField(
        verbose_name='Дата окончания', null=True, blank=True)
    date_use = models.DateTimeField(
        verbose_name='Дата последнего гошения', auto_now=True)


    def use(self, client: Client):
        self.checking(client)
        self._pre_use()
        self.users.add(client)
        self.save()
        client.add_balance(self.bonus, comment='Купон: {self.code}')

    def _pre_use(self):
        self.current_uses += 1

    def checking(self, client: Client):
        if self.date_end and self.date_end < timezone.now():
            # Если срок действия купона закончился
            raise CuponException('Срок действия купона окончен.')
        elif self.owner_id:
            # Если купон преднозначит конкретному пользователю
            if self.owner_id != client.get_id:
                # Если пытается погасить не тот пользователь
                raise CuponException('Купон преднозначен другому пользователю.')
            elif self.current_uses >= self.max_uses:
                # Если количство гошений максимально
                raise CuponException('Вы уже погасили данный купон')
        else:
            # Еслки купон не преднозначен для определённого пользователя
            if not self.multi_use and self.current_uses >= self.max_uses:
                # Если купон уже погашен
                raise CuponException('Купон уже погашен.')
            elif client in self.users.all():
                # Если купон многоразовый и данный юзер его уже гасил
                raise CuponException('Вы уже использовали данный купон.')
