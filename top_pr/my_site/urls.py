from django.urls import path, re_path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('', view=views.index, name='index'),
    # re_path(r'^robots\.txt$', view=views.robots,),
    path('cat/<slug:cat_slug>/sub/<slug:sub_slug>/', view=views.get_tariffs),
    path('cat/<slug:category_slug>/', view=views.subcategories_with_services),
    path('promocode/<str:promocode>/', view=views.get_promocode),
    path('comment/<int:order_id>/', view=views.add_comment, name='comment'),
    path('create-order/<slug:tarif>/', view=views.create_order, name='create-order'),
    path('new-order/', view=views.new_order, name='new-order'),
    path('services/', view=views.services, name='services'),
    path('oferta/', view=views.oferta, name='oferta'),
    path('policy/', view=views.policy, name='policy'),
    path('services/<slug:social>/<slug:category>/', view=views.services_filter, name='filter-services'),
    path('categories/<slug:category_slug>/', view=views.categories),
    path('order-confirmation/<int:order_id>', view=views.order_confirmation, name='order-confirmation'),
    path('faq/', view=views.faq, name='faq'),
    path('pay-profile/', view=views.AJAX_profile, name='pay_profile'),
    path('order-pay/', view=views.order_pay, name='order-pay'),
    # path('calculate/', view=views.AJAX_calculate, name='calc'),
    path('checkedpay/', view=views.AJAX_checked_pay, name='checkedpay'),
    path('pay/', view=views.pay_test, name='pay'),
    path('orders/', view=views.table_orders, name='orders'),
    path('orders/search', view=views.search_orders, name='orders_search'),
    path('orders/sorting', view=views.sort_orders, name='orders_sirt'),
    path('order-cancel/', view=views.AJAX_order_cancel, name='order_cancel'),
    path('contacts/', view=views.contacts, name='contacts'),
    path('<slug:social>/<slug:tariff>/', view=views.service_tariff, name='service_tariff'),
    path('<slug:social>/', view=views.social, name='social'),
]