from django.contrib import admin
from .models import Cupon

@admin.register(Cupon)
class CuponAdmin(admin.ModelAdmin):
    list_display = ['code', 'bonus', 'max_uses', 'current_uses', 'multi_use', 'date_create']
    fields = ('code', 'owner_id', 'bonus', 'max_uses', 'current_uses', 'multi_use', 'date_end',)