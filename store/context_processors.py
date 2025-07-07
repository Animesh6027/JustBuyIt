from .models import Wishlist

def cart_and_wishlist_counts(request):
    cart = request.session.get('cart', {})
    cart_count = sum(cart.values())

    wishlist_count = 0
    if request.user.is_authenticated:
        wishlist_count = Wishlist.objects.filter(user=request.user).count()

    return {
        'cart_count': cart_count,
        'wishlist_count': wishlist_count
    }
