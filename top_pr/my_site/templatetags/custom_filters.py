from django import template
from decimal import Decimal
from my_site.utils import del_zero

register = template.Library()

@register.filter
def format_decimal(value):
    return del_zero(value)