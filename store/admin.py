from django.contrib import admin
from .models import Category, SubCategory, Product
from .models import Review

admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Product)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created_at']
    list_filter = ['rating']
