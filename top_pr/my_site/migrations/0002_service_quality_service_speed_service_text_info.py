# Generated by Django 4.0.4 on 2022-06-13 21:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_site', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='quality',
            field=models.IntegerField(default=5, verbose_name='Качество'),
        ),
        migrations.AddField(
            model_name='service',
            name='speed',
            field=models.IntegerField(default=5, verbose_name='Скорость накрутки'),
        ),
        migrations.AddField(
            model_name='service',
            name='text_info',
            field=models.CharField(default='asfasf', max_length=250, verbose_name='Инфо'),
            preserve_default=False,
        ),
    ]
