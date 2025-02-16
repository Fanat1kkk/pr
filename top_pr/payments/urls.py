from django.urls import path
from . import views

urlpatterns = [
    path('py-kassa-yo-yandex/', view=views.pay_yookassa),
    path('yoomaney', view=views.pay_yoommany)

]