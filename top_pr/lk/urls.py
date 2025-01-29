from django.urls import path
from . import views

urlpatterns = [
    path('', view=views.profile, name='profile'),
    path('new-order/', view=views.new_order_profile, name='new-order-profile'),
    path('order/<int:order_id>', view=views.order_confirmation, name='order-confirm-profile'),
    path('pay-balance/', view=views.pay_balance, name='pay-balance'),
    path('info/<int:service_id>', view=views.service_info, name='service-info'),
    path('cancel-order/', view=views.order_cancel, name='cancel-order'),
    path('settings/', view=views.settings, name='settings'),
    path('history-pay/<int:page>', view=views.listing_history_pay, name='history-pay'),
]
