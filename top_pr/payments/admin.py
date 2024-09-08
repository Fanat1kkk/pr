from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['unic_id', 'order', 'pay_provider', 'is_paid', 'date_create', 'date_paid']
