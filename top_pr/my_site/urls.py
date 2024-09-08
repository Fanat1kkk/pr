from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', view=views.index, name='index'),
    path('cat_id/<int:cat_id>/sub_id/<int:sub_id>', view=views.AJAX_get_services),
    path('comment/<int:order_id>', view=views.add_comment, name='comment'),
    path('new_order/', view=views.AJAX_order, name='new_order'),
    path('profile/', view=views.profile, name='profile'),
    path('faq/', view=views.faq, name='faq'),
    path('pay-profile/', view=views.AJAX_profile, name='pay_profile'),
    path('calculate/', view=views.AJAX_calculate, name='calc'),
    path('checkedpay/', view=views.AJAX_checked_pay, name='checkedpay'),
    path('pay/', view=views.pay_test, name='pay'),
    path('orders/', view=views.table_orders, name='orders'),
    path('orders/search', view=views.search_orders, name='orders_search'),
    path('orders/sorting', view=views.sort_orders, name='orders_sirt'),
    path('order-cancel/', view=views.AJAX_order_cancel, name='order_cancel'),
    # path('search/', view=views.search_orders, name='search'),
    path('login/', view=views.AjaxLoginView.as_view(), name='my_login'),
    path('signup/', view=views.AjaxSignupView.as_view(), name='my_signup'),
    # path('password/reset/', view=views.MyPasswordResetView.as_view(), name='account_reset_password'),
    path('password/reset/done/', view=views.PasswordResetDoneView.as_view(), name='account_reset_password_done'),
    re_path(r"^password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$", views.MyPasswordResetFromKeyView.as_view(), name="account_reset_password_from_key"),
    path("password/reset/key/done/", view=views.MyPasswordResetFromKeyDoneView.as_view(), name="account_reset_password_from_key_done"),
]
