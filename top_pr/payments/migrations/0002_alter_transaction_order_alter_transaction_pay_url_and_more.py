# Generated by Django 4.0.4 on 2022-06-08 06:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('my_site', '0001_initial'),
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='my_site.order', verbose_name='Заказ'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='pay_url',
            field=models.URLField(blank=True, null=True, verbose_name='Адрес оплаты'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='sign',
            field=models.UUIDField(blank=True, null=True),
        ),
    ]
