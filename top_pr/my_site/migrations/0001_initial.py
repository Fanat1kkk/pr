# Generated by Django 4.0.4 on 2022-06-07 21:06

from django.conf import settings
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import my_site.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('balance', models.DecimalField(decimal_places=2, default=0, max_digits=8, verbose_name='Баланс')),
                ('date_last_active', models.DateTimeField(auto_now=True, verbose_name='Дата последней активности')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Клиент',
                'verbose_name_plural': 'Клиенты',
            },
            managers=[
                ('objects', my_site.models.ClientManager()),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cat_name', models.CharField(max_length=30, verbose_name='Название')),
                ('img', models.CharField(choices=[('TEL', 'telegram.svg'), ('VK', 'vk.svg'), ('TIK', 'tiktok.svg'), ('CLIN', 'c_link.svg'), ('STAR', 'c_star.svg'), ('EYE', 'eye.svg'), ('HEAR', 'heart.svg'), ('IGTV', 'igtv.svg'), ('LIKE', 'likee.svg'), ('REVO', 'record_voice.svg'), ('SAVE', 'save.svg'), ('SHOW', 'show.svg'), ('THUP', 'thumb-up.svg'), ('USER', 'user.svg'), ('USES', 'users.svg')], max_length=4, verbose_name='Картинка')),
            ],
            options={
                'verbose_name': 'Категория',
                'verbose_name_plural': 'Категории',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('order_id', models.IntegerField(primary_key=True, serialize=False, unique=True, verbose_name='ID заказа')),
                ('status', models.CharField(choices=[('INWOR', 'В работе'), ('NOPAY', 'Не оплачен'), ('BLOCK', 'Заблокирован'), ('COMPL', 'Выполнено'), ('CANC', 'Отменён')], default='NOPAY', max_length=5, verbose_name='Статус')),
                ('count', models.IntegerField(verbose_name='Количество')),
                ('end_count', models.IntegerField(default=0, verbose_name='Выполнено')),
                ('start_count', models.IntegerField(default=0, verbose_name='Кол-во до старта')),
                ('task_url', models.CharField(max_length=150, verbose_name='Ссылка')),
                ('date_create', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('date_edit', models.DateTimeField(auto_now=True, verbose_name='Дата изменения')),
                ('price', models.DecimalField(decimal_places=2, max_digits=8, verbose_name='Цена')),
                ('email', models.EmailField(max_length=60, null=True, verbose_name='Емаил')),
                ('is_paid', models.BooleanField(default=False, verbose_name='Оплачен')),
                ('client', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to=settings.AUTH_USER_MODEL, verbose_name='Клиент')),
            ],
            options={
                'verbose_name': 'Заказ',
                'verbose_name_plural': 'Заказы',
            },
        ),
        migrations.CreateModel(
            name='PromoCode',
            fields=[
                ('code', models.CharField(max_length=7, primary_key=True, serialize=False, unique=True, verbose_name='Код')),
                ('discount_percent', models.IntegerField(default=0, verbose_name='Процент скидки')),
                ('max_number_uses', models.IntegerField(default=1, verbose_name='Макс кол-во гошений')),
                ('number_uses', models.IntegerField(default=0, verbose_name='Кол-во гошений')),
                ('is_multiple', models.BooleanField(verbose_name='Многоразовый')),
                ('date_end', models.DateTimeField(null=True, verbose_name='Дата окончания')),
                ('date_create', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('date_edit', models.DateTimeField(auto_now=True, verbose_name='Дата изменения')),
            ],
        ),
        migrations.CreateModel(
            name='Provider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40, verbose_name='Название')),
                ('balance', models.DecimalField(decimal_places=2, default=0, max_digits=8, verbose_name='Баланс')),
                ('api_url', models.CharField(max_length=150)),
                ('is_active', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Провайдер',
                'verbose_name_plural': 'Провайдеры',
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, verbose_name='Название')),
                ('service_id', models.IntegerField(unique=True, verbose_name='Сервис ID')),
                ('min_count', models.IntegerField(verbose_name='Минимум')),
                ('max_count', models.IntegerField(verbose_name='Максимум')),
                ('price', models.DecimalField(decimal_places=2, max_digits=8, verbose_name='Цена за 1000 шт.')),
                ('percent', models.IntegerField(default=50, verbose_name='Процент накрутки')),
                ('provider_service_id', models.IntegerField(verbose_name='Сервис ID провайдера')),
                ('is_published', models.BooleanField(default=False, verbose_name='Активна?')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='services', to='my_site.category', verbose_name='Категория')),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='services', to='my_site.provider', verbose_name='Провайдер')),
            ],
            options={
                'verbose_name': 'Услуга',
                'verbose_name_plural': 'Услуги',
            },
        ),
        migrations.CreateModel(
            name='Subcategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=35, unique=True, verbose_name='Назвение')),
                ('img', models.CharField(blank=True, choices=[('TEL', 'telegram.svg'), ('VK', 'vk.svg'), ('TIK', 'tiktok.svg'), ('CLIN', 'c_link.svg'), ('STAR', 'c_star.svg'), ('EYE', 'eye.svg'), ('HEAR', 'heart.svg'), ('IGTV', 'igtv.svg'), ('LIKE', 'likee.svg'), ('REVO', 'record_voice.svg'), ('SAVE', 'save.svg'), ('SHOW', 'show.svg'), ('THUP', 'thumb-up.svg'), ('USER', 'user.svg'), ('USES', 'users.svg')], max_length=4, null=True, verbose_name='Картинка')),
            ],
            options={
                'verbose_name': 'Подкатегория',
                'verbose_name_plural': 'Подкотегории',
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('INWOR', 'В работе'), ('NOPAY', 'Не оплачен'), ('BLOCK', 'Заблокирован'), ('COMPL', 'Выполнено'), ('CANC', 'Отменён')], default='NOPAY', max_length=5, verbose_name='Статус')),
                ('count', models.IntegerField(verbose_name='Количество')),
                ('end_count', models.IntegerField(default=0, verbose_name='Выполнено')),
                ('start_count', models.IntegerField(default=0, verbose_name='Кол-во до старта')),
                ('task_url', models.CharField(max_length=150, verbose_name='Ссылка')),
                ('date_create', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('date_edit', models.DateTimeField(auto_now=True, verbose_name='Дата изменения')),
                ('provider_order_id', models.IntegerField(null=True, verbose_name='Провайдер ID заказа')),
                ('is_created', models.BooleanField(default=False)),
                ('is_error', models.BooleanField(default=False)),
                ('error_pr', models.TextField(blank=True, null=True, verbose_name='Ошибка от провайдера')),
                ('order', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='my_site.order', verbose_name='Заказы')),
                ('provider', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tasks', to='my_site.provider', verbose_name='Провайдер')),
                ('service', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='my_site.service', verbose_name='Сервис')),
            ],
            options={
                'verbose_name': 'Задача',
                'verbose_name_plural': 'Задачи',
            },
        ),
        migrations.AddField(
            model_name='service',
            name='sub_cat',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='services', to='my_site.subcategory', verbose_name='Подкатегория'),
        ),
        migrations.AddField(
            model_name='order',
            name='promocode',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='my_site.promocode', verbose_name='Промокод'),
        ),
        migrations.AddField(
            model_name='order',
            name='service',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='my_site.service', verbose_name='Сервис'),
        ),
        migrations.AddField(
            model_name='category',
            name='sub_cat',
            field=models.ManyToManyField(related_name='categories', to='my_site.subcategory'),
        ),
    ]
