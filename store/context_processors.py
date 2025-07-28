from .models import Order, OrderItem
from django.db.models import Sum, Count


def cart_and_wishlist_count(request):
    """Add cart and wishlist counts to context"""
    cart_count = 0
    wishlist_count = 0
    
    if request.user.is_authenticated:
        cart = request.session.get('cart', {})
        cart_count = len(cart)
        
        from .models import Wishlist
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
    
    return {
        'cart_count': cart_count,
        'wishlist_count': wishlist_count,
    }


def order_statistics(request):
    """Add order statistics to context for buyers"""
    order_stats = {
        'total_orders': 0,
        'total_items_purchased': 0,
        'total_spent': 0,
        'recent_orders': []
    }
    
    if request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role == 'buyer':
        orders = Order.objects.filter(customer=request.user)
        
        # Total orders
        order_stats['total_orders'] = orders.count()
        
        # Total items purchased
        total_items = OrderItem.objects.filter(order__customer=request.user).aggregate(
            total=Sum('quantity')
        )['total'] or 0
        order_stats['total_items_purchased'] = total_items
        
        # Total spent
        total_spent = orders.aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        order_stats['total_spent'] = total_spent
        
        # Recent orders (last 3)
        order_stats['recent_orders'] = orders.order_by('-created_at')[:3]
    
    return {
        'order_stats': order_stats,
    }
