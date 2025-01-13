from django.urls import path, re_path
from . import views

urlpatterns = [
    # path('freecassa/', view=views.pay_freecassa),
    path('yoomaney', view=views.pay_yoommany),
    path('freecassa', view=views.pay_freecassa),

]