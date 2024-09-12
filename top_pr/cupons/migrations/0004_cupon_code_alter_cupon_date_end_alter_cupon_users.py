# Generated by Django 4.0.4 on 2022-06-20 14:59

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cupons', '0003_alter_cupon_users'),
    ]

    operations = [
        migrations.AddField(
            model_name='cupon',
            name='code',
            field=models.CharField(default='sdf', max_length=7, verbose_name='Код'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='cupon',
            name='date_end',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Дата окончания'),
        ),
        migrations.AlterField(
            model_name='cupon',
            name='users',
            field=models.ManyToManyField(blank=True, related_name='cupons', to=settings.AUTH_USER_MODEL, verbose_name='Клиент'),
        ),
    ]
