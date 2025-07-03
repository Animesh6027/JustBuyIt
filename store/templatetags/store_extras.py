from django import template
from store.models import SubCategory

register = template.Library()

@register.filter
def get_subcategories(categories, category_id):
    return SubCategory.objects.filter(category_id=category_id)
