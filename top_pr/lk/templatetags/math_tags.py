from decimal import Decimal
from django import template

from my_site.utils import del_zero

register = template.Library()

@register.filter
def subtract(value, arg):
    """Вычитает arg из value."""
    return value - arg

@register.filter
def subtractDecimal(value, arg):
    """Вычитает arg из value."""
    return del_zero(Decimal(value) - Decimal(arg))