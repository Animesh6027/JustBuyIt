from django import template
from store.models import SubCategory

register = template.Library()

@register.filter
def get_subcategories(categories, category_id):
    return SubCategory.objects.filter(category_id=category_id)

@register.filter
def mul(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''
