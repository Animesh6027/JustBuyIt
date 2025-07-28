from django.contrib import admin
from .models import Product, Category, SubCategory, Wishlist, Review, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    list_filter = ['category']
    search_fields = ['name', 'category__name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'supplier', 'stock_quantity', 'is_in_stock', 'created_at']
    list_filter = ['category', 'supplier', 'is_in_stock', 'created_at']
    search_fields = ['name', 'description', 'supplier__username']
    readonly_fields = ['created_at', 'last_stock_update']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'price', 'image', 'category', 'subcategory', 'supplier')
        }),
        ('Stock Management', {
            'fields': ('stock_quantity', 'low_stock_threshold', 'is_in_stock', 'last_stock_update')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'product__category']
    list_filter = ['product__category']
    search_fields = ['user__username', 'product__name']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'rating', 'created_at']
    list_filter = ['rating', 'created_at', 'product__category']
    search_fields = ['user__username', 'product__name', 'comment']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at', 'customer']
    search_fields = ['order_number', 'customer__username', 'shipping_address']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'customer', 'status', 'total_amount')
        }),
        ('Shipping Information', {
            'fields': ('shipping_address', 'phone_number', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price', 'total_price']
    list_filter = ['order__status', 'product__category']
    search_fields = ['order__order_number', 'product__name']
    readonly_fields = ['total_price']
