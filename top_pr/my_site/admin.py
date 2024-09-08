from django.contrib import admin
from .models import *
from payments.models import Transaction


class BalanceTransactionInline(admin.TabularInline):
    model = BalanceTransaction
    extra = 0

class TasksInline(admin.TabularInline):
    model = Task
    exclude = ('task_url', 'is_created',)
    extra = 0

class TransactionInline(admin.TabularInline):
    model = Transaction
    exclude = ('date_paid',)
    extra = 0


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_percent']


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    
    list_display = ['username', 'email', 'balance']

    inlines = [
        BalanceTransactionInline,
    ]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    
    list_display = ['cat_name']


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    
    list_display = ['name', 'balance', 'is_active']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    
    list_display = ['name', 'full_name', 'price_d', 'price_per_one_d', 'order_complite', 'service_id', 'provider_service_id', 'provider', 'is_published']
    
    def price_d(self, obj: Service):
        return f'{obj.price} / {obj.price_per_one()*1000}'

    def price_per_one_d(self, obj: Service):
        return f'{obj.price/1000} / {obj.price_per_one()}'
    
    def order_complite(self, obj: Service):
        
        return obj.task_set.filter(status='COMPL').count()
    
    order_complite.short_description = 'Всего выполнено'
    price_per_one_d.short_description = 'Цена за 1'
    price_d.short_description = 'Цена за 1000'

@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):

    list_display = ['name', 'img']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['client', 'service', 'order_id', 'count', 'price', 'task_url', 'is_paid']
    inlines = [
        TasksInline,
        TransactionInline
    ]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):

    list_display = ['order_id', 'service', 'status']


@admin.register(CustomerReview)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['service', 'rating_speed', 'rating_acc']
    
    