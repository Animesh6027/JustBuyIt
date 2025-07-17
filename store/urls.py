from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add-product/', views.add_product, name='add_product'),
    path('products/', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('dashboard/', views.supplier_dashboard, name='supplier_dashboard'),
    path('dashboard/reviews/', views.supplier_reviews, name='supplier_reviews'),
    path('dashboard/analytics/', views.supplier_analytics, name='supplier_analytics'),
    path('product/<int:pk>/edit/', views.edit_product, name='edit_product'),
    path('product/<int:pk>/delete/', views.delete_product, name='delete_product'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<int:pk>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:pk>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('bulk-upload/', views.bulk_upload, name='bulk_upload'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('cart/increase/<int:pk>/', views.increase_cart_quantity, name='increase_cart_quantity'),
    path('cart/decrease/<int:pk>/', views.decrease_cart_quantity, name='decrease_cart_quantity'),
    path('product/<int:product_id>/review/', views.add_review, name='add_review'),
]
