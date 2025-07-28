from django.shortcuts import render, redirect
from .forms import ProductForm, CheckoutForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Review, Order, OrderItem
from .models import Product, Category, SubCategory
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib import messages
from .models import Wishlist
import csv
from django.core.mail import send_mail
from django.conf import settings
from accounts.models import CustomUser
from django.core.paginator import Paginator
from django.db import models


@login_required
def add_product(request):
    if request.user.role != 'supplier':
        return HttpResponseForbidden("Only suppliers can upload products.")

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.supplier = request.user
            
            # Update stock status based on quantity
            if product.stock_quantity <= 0:
                product.is_in_stock = False
            elif product.stock_quantity <= product.low_stock_threshold:
                product.is_in_stock = True  # Still in stock but low
            else:
                product.is_in_stock = True
            
            product.save()
            
            # Show success message with stock info
            if product.stock_quantity == 0:
                messages.success(request, f"✅ Product '{product.name}' added successfully! ⚠️ Stock: Out of stock")
            elif product.stock_quantity <= product.low_stock_threshold:
                messages.success(request, f"✅ Product '{product.name}' added successfully! ⚠️ Stock: Low ({product.stock_quantity} units)")
            else:
                messages.success(request, f"✅ Product '{product.name}' added successfully! 📦 Stock: {product.stock_quantity} units")
            
            return redirect('supplier_dashboard')
        else:
            messages.error(request, "❌ Please correct the errors below.")
    else:
        form = ProductForm()
    
    return render(request, 'store/add_product.html', {'form': form})


def home(request):
    trending_products = Product.objects.order_by('-created_at')[:8]
    
    # Get products for slideshow carousel (featured products)
    carousel_products = Product.objects.filter(is_in_stock=True).order_by('-created_at')[:6]
    
    return render(request, 'store/home.html', {
        'trending_products': trending_products,
        'carousel_products': carousel_products
    })

def product_list(request):
    category_id = request.GET.get('category')
    subcategory_id = request.GET.get('subcategory')
    search_query = request.GET.get('q', '')  # 👈 Get search query

    products = Product.objects.all().order_by('-created_at')
    categories = Category.objects.all()

    if category_id:
        products = products.filter(category_id=category_id)

    if subcategory_id:
        products = products.filter(subcategory_id=subcategory_id)

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )

    # Pagination: 9 products per page
    paginator = Paginator(products, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'store/product_list.html', {
        'products': products,
        'categories': categories,
        'selected_category': category_id,
        'selected_subcategory': subcategory_id,
        'search_query': search_query,  # 👈 pass back to template
        'page_obj': page_obj,  # 👈 pass page_obj for pagination
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})


@login_required
def supplier_dashboard(request):
    if request.user.role != 'supplier':
        return redirect('product_list')

    # Get supplier's products
    products = Product.objects.filter(supplier=request.user).order_by('-created_at')
    
    # Analytics data
    total_products = products.count()
    total_reviews = Review.objects.filter(product__supplier=request.user).count()
    avg_rating = Review.objects.filter(product__supplier=request.user).aggregate(
        avg=models.Avg('rating')
    )['avg'] or 0
    
    # Revenue calculation (assuming price as revenue for now)
    total_revenue = products.aggregate(
        total=models.Sum('price')
    )['total'] or 0
    
    # Recent activity
    recent_products = products[:5]
    recent_reviews = Review.objects.filter(product__supplier=request.user).order_by('-created_at')[:5]
    
    # Product performance (by review count)
    top_products = products.annotate(
        review_count=models.Count('reviews')
    ).order_by('-review_count')[:5]
    
    # Category distribution
    category_stats = products.values('category__name').annotate(
        count=models.Count('id')
    ).order_by('-count')
    
    # Monthly product creation trend
    from django.utils import timezone
    from datetime import timedelta
    import calendar
    
    # Get last 6 months
    months = []
    product_counts = []
    for i in range(6):
        date = timezone.now() - timedelta(days=30*i)
        month_name = calendar.month_name[date.month]
        count = products.filter(
            created_at__year=date.year,
            created_at__month=date.month
        ).count()
        months.append(month_name)
        product_counts.append(count)
    
    # Filter products if search query
    search_query = request.GET.get('q', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    # Category filter
    category_filter = request.GET.get('category', '')
    if category_filter:
        products = products.filter(category_id=category_filter)
    
    # Status filter (active/inactive - for future use)
    status_filter = request.GET.get('status', '')
    if status_filter == 'active':
        products = products.filter(active=True)  # Assuming active field exists
    elif status_filter == 'inactive':
        products = products.filter(active=False)
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all categories for filter dropdown
    all_categories = Category.objects.all()
    
    # Stock management data
    in_stock_count = products.filter(is_in_stock=True).count()
    low_stock_count = products.filter(stock_quantity__lte=models.F('low_stock_threshold')).exclude(stock_quantity=0).count()
    out_of_stock_count = products.filter(stock_quantity=0).count()
    low_stock_products = products.filter(stock_quantity__lte=models.F('low_stock_threshold')).exclude(stock_quantity=0).order_by('stock_quantity')[:5]
    
    return render(request, 'store/supplier_dashboard.html', {
        'products': page_obj,
        'total_products': total_products,
        'total_reviews': total_reviews,
        'avg_rating': round(avg_rating, 1),
        'total_revenue': total_revenue,
        'recent_products': recent_products,
        'recent_reviews': recent_reviews,
        'top_products': top_products,
        'category_stats': category_stats,
        'months': months,
        'product_counts': product_counts,
        'in_stock_count': in_stock_count,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'low_stock_products': low_stock_products,
        'search_query': search_query,
        'category_filter': category_filter,
        'status_filter': status_filter,
        'all_categories': all_categories,
        'page_obj': page_obj,
    })


@login_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)

    # Prevent other users from editing
    if request.user != product.supplier:
        return redirect('product_list')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            
            # Update stock status based on quantity
            if product.stock_quantity <= 0:
                product.is_in_stock = False
            elif product.stock_quantity <= product.low_stock_threshold:
                product.is_in_stock = True  # Still in stock but low
            else:
                product.is_in_stock = True
            
            product.save()
            
            # Show success message with stock info
            if product.stock_quantity == 0:
                messages.success(request, f"✅ Product '{product.name}' updated successfully! ⚠️ Stock: Out of stock")
            elif product.stock_quantity <= product.low_stock_threshold:
                messages.success(request, f"✅ Product '{product.name}' updated successfully! ⚠️ Stock: Low ({product.stock_quantity} units)")
            else:
                messages.success(request, f"✅ Product '{product.name}' updated successfully! 📦 Stock: {product.stock_quantity} units")
            
            return redirect('supplier_dashboard')
        else:
            messages.error(request, "❌ Please correct the errors below.")
    else:
        form = ProductForm(instance=product)

    return render(request, 'store/edit_product.html', {'form': form})


@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.user != product.supplier:
        return redirect('product_list')

    if request.method == 'POST':
        product.delete()
        return redirect('supplier_dashboard')

    return render(request, 'store/delete_product.html', {'product': product})


def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart = request.session.get('cart', {})

    # Use product ID as key and quantity as value
    if str(pk) in cart:
        cart[str(pk)] += 1
    else:
        cart[str(pk)] = 1

    request.session['cart'] = cart
    messages.success(request, f"{product.name} added to cart.")
    return redirect('product_list')


@login_required
def view_cart(request):
    if request.user.role != "buyer":
        return redirect('product_list')

    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for product_id, qty in cart.items():
        product = get_object_or_404(Product, pk=product_id)
        subtotal = product.price * qty
        total += subtotal
        cart_items.append({
            'product': product,
            'quantity': qty,
            'subtotal': subtotal,
        })

    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'total': total
    })


@login_required
def add_to_wishlist(request, pk):
    product = get_object_or_404(Product, pk=pk)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    messages.success(request, f"{product.name} added to your wishlist.")
    return redirect('product_list')


@login_required
def remove_from_wishlist(request, pk):
    Wishlist.objects.filter(user=request.user, product_id=pk).delete()
    messages.success(request, "Removed from wishlist.")
    return redirect('wishlist')


@login_required
def wishlist(request):
    items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'store/wishlist.html', {'wishlist_items': items})


def remove_from_cart(request, pk):
    cart = request.session.get('cart', {})
    pk_str = str(pk)

    if pk_str in cart:
        del cart[pk_str]
        request.session['cart'] = cart
        messages.success(request, "Item removed from cart.")

    return redirect('view_cart')

@login_required
def increase_cart_quantity(request, pk):
    cart = request.session.get('cart', {})
    pk_str = str(pk)
    if pk_str in cart:
        cart[pk_str] += 1
        request.session['cart'] = cart
    return redirect('view_cart')


@login_required
def decrease_cart_quantity(request, pk):
    cart = request.session.get('cart', {})
    pk_str = str(pk)
    if pk_str in cart:
        if cart[pk_str] > 1:
            cart[pk_str] -= 1
        else:
            del cart[pk_str]  # remove if quantity reaches zero
        request.session['cart'] = cart
    return redirect('view_cart')


def bulk_upload(request):
    if request.user.role != 'supplier':
        return redirect('product_list')

    if request.method == 'POST':
        csv_file = request.FILES['csv_file']
        decoded = csv_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded)

        for row in reader:
            try:
                category = Category.objects.get(name=row['category'])
                subcategory = SubCategory.objects.get(name=row['subcategory'], category=category)
                Product.objects.create(
                    name=row['name'],
                    description=row['description'],
                    price=row['price'],
                    category=category,
                    subcategory=subcategory,
                    supplier=request.user
                )
            except Exception as e:
                print("Error:", e)

        return redirect('supplier_dashboard')

    return render(request, 'store/bulk_upload.html')


def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        rating = request.POST['rating']
        comment = request.POST['comment']

        Review.objects.create(
            product=product,
            user=request.user,
            rating=rating,
            comment=comment
        )

    return redirect('product_detail', pk=product.id)


def about_view(request):
    # Real-time stats
    product_count = Product.objects.count()
    buyer_count = CustomUser.objects.filter(role='buyer').count()
    supplier_count = CustomUser.objects.filter(role='supplier').count()
    category_count = Category.objects.count()
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        message = request.POST.get('message', '').strip()
        if name and email and message:
            # Email sending code commented out for now
            # subject = f"New Contact Form Submission from {name}"
            # body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
            # send_mail(
            #     subject,
            #     body,
            #     settings.DEFAULT_FROM_EMAIL,
            #     ['animeshsingh6027@gmail.com'],
            #     fail_silently=False,
            # )
            messages.success(request, 'Thank you for contacting us! We will get back to you soon.')
            return redirect('about')
        else:
            messages.error(request, 'Please fill in all fields.')
    return render(request, 'about.html', {
        'product_count': product_count,
        'buyer_count': buyer_count,
        'supplier_count': supplier_count,
        'category_count': category_count,
    })


@login_required
def supplier_reviews(request):
    if request.user.role != 'supplier':
        return redirect('product_list')
    
    # Get all reviews for supplier's products
    reviews = Review.objects.filter(product__supplier=request.user).select_related('product', 'user').order_by('-created_at')
    
    # Filter by rating
    rating_filter = request.GET.get('rating', '')
    if rating_filter:
        reviews = reviews.filter(rating=rating_filter)
    
    # Filter by product
    product_filter = request.GET.get('product', '')
    if product_filter:
        reviews = reviews.filter(product_id=product_filter)
    
    # Search reviews
    search_query = request.GET.get('q', '')
    if search_query:
        reviews = reviews.filter(
            Q(comment__icontains=search_query) | 
            Q(product__name__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get supplier's products for filter
    supplier_products = Product.objects.filter(supplier=request.user)
    
    # Review statistics
    total_reviews = reviews.count()
    avg_rating = reviews.aggregate(avg=models.Avg('rating'))['avg'] or 0
    rating_distribution = reviews.values('rating').annotate(count=models.Count('id')).order_by('rating')
    
    return render(request, 'store/supplier_reviews.html', {
        'reviews': page_obj,
        'total_reviews': total_reviews,
        'avg_rating': round(avg_rating, 1),
        'rating_distribution': rating_distribution,
        'supplier_products': supplier_products,
        'rating_filter': rating_filter,
        'product_filter': product_filter,
        'search_query': search_query,
        'page_obj': page_obj,
    })


@login_required
def supplier_analytics(request):
    if request.user.role != 'supplier':
        return redirect('product_list')
    
    # Get supplier's products
    products = Product.objects.filter(supplier=request.user)
    
    # Sales analytics (assuming price as revenue for now)
    total_revenue = products.aggregate(total=models.Sum('price'))['total'] or 0
    avg_product_price = products.aggregate(avg=models.Avg('price'))['avg'] or 0
    
    # Review analytics
    reviews = Review.objects.filter(product__supplier=request.user)
    total_reviews = reviews.count()
    avg_rating = reviews.aggregate(avg=models.Avg('rating'))['avg'] or 0
    
    # Product performance
    top_products = products.annotate(
        review_count=models.Count('reviews'),
        avg_rating=models.Avg('reviews__rating')
    ).order_by('-review_count')[:10]
    
    # Category performance
    category_performance = products.values('category__name').annotate(
        product_count=models.Count('id'),
        total_value=models.Sum('price'),
        avg_rating=models.Avg('reviews__rating')
    ).order_by('-product_count')
    
    # Monthly trends
    from django.utils import timezone
    from datetime import timedelta
    import calendar
    
    months = []
    product_counts = []
    revenue_data = []
    
    for i in range(6):
        date = timezone.now() - timedelta(days=30*i)
        month_name = calendar.month_name[date.month]
        month_products = products.filter(
            created_at__year=date.year,
            created_at__month=date.month
        )
        count = month_products.count()
        revenue = month_products.aggregate(total=models.Sum('price'))['total'] or 0
        
        months.append(month_name)
        product_counts.append(count)
        revenue_data.append(revenue)
    
    # --- SCALE BAR HEIGHTS ---
    max_revenue = max(revenue_data) if revenue_data else 1
    max_count = max(product_counts) if product_counts else 1
    max_bar_height = 180  # px
    revenue_bar_heights = [int((val / max_revenue) * max_bar_height) if max_revenue else 0 for val in revenue_data]
    product_bar_heights = [int((val / max_count) * max_bar_height) if max_count else 0 for val in product_counts]
    
    return render(request, 'store/supplier_analytics.html', {
        'total_revenue': total_revenue,
        'avg_product_price': round(avg_product_price, 2),
        'total_reviews': total_reviews,
        'avg_rating': round(avg_rating, 1),
        'top_products': top_products,
        'category_performance': category_performance,
        'months': months,
        'product_counts': product_counts,
        'revenue_data': revenue_data,
        'revenue_bar_heights': revenue_bar_heights,
        'product_bar_heights': product_bar_heights,
    })


@login_required
def stock_management(request):
    if request.user.role != 'supplier':
        return redirect('product_list')
    
    products = Product.objects.filter(supplier=request.user).order_by('-last_stock_update')
    
    # Stock statistics
    total_products = products.count()
    in_stock_count = products.filter(is_in_stock=True).count()
    low_stock_count = products.filter(stock_quantity__lte=models.F('low_stock_threshold')).exclude(stock_quantity=0).count()
    out_of_stock_count = products.filter(stock_quantity=0).count()
    
    # Recent stock updates
    recent_updates = products.filter(last_stock_update__isnull=False).order_by('-last_stock_update')[:10]
    
    return render(request, 'store/stock_management.html', {
        'products': products,
        'total_products': total_products,
        'in_stock_count': in_stock_count,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'recent_updates': recent_updates,
    })


@login_required
def update_stock(request, product_id):
    if request.user.role != 'supplier':
        return redirect('product_list')
    
    product = get_object_or_404(Product, id=product_id, supplier=request.user)
    
    if request.method == 'POST':
        new_quantity = request.POST.get('stock_quantity')
        new_threshold = request.POST.get('low_stock_threshold')
        
        if new_quantity is not None:
            product.stock_quantity = int(new_quantity)
        if new_threshold is not None:
            product.low_stock_threshold = int(new_threshold)
        
        product.update_stock_status()
        messages.success(request, f'Stock updated for {product.name}')
        return redirect('stock_management')
    
    return render(request, 'store/update_stock.html', {'product': product})


@login_required
def bulk_stock_update(request):
    if request.user.role != 'supplier':
        return redirect('product_list')
    
    if request.method == 'POST':
        # Handle CSV upload for bulk stock update
        csv_file = request.FILES.get('csv_file')
        if csv_file:
            try:
                import csv
                from io import StringIO
                
                # Read CSV content
                content = csv_file.read().decode('utf-8')
                csv_data = csv.DictReader(StringIO(content))
                
                updated_count = 0
                for row in csv_data:
                    try:
                        product = Product.objects.get(
                            id=row['product_id'],
                            supplier=request.user
                        )
                        product.stock_quantity = int(row['stock_quantity'])
                        if 'low_stock_threshold' in row:
                            product.low_stock_threshold = int(row['low_stock_threshold'])
                        product.update_stock_status()
                        updated_count += 1
                    except (Product.DoesNotExist, ValueError, KeyError):
                        continue
                
                messages.success(request, f'Updated stock for {updated_count} products')
            except Exception as e:
                messages.error(request, f'Error processing CSV: {str(e)}')
    
    products = Product.objects.filter(supplier=request.user).order_by('name')
    return render(request, 'store/bulk_stock_update.html', {'products': products})


@login_required
def checkout(request):
    """Checkout page for creating orders from cart"""
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Get cart items from session
            cart_items = request.session.get('cart', {})
            if not cart_items:
                messages.error(request, 'Your cart is empty.')
                return redirect('view_cart')
            
            # Calculate total
            total_amount = 0
            order_items = []
            
            for product_id, quantity in cart_items.items():
                try:
                    product = Product.objects.get(id=product_id)
                    if product.is_out_of_stock():
                        messages.error(request, f'{product.name} is out of stock.')
                        return redirect('view_cart')
                    
                    if product.stock_quantity < quantity:
                        messages.error(request, f'Only {product.stock_quantity} units of {product.name} available.')
                        return redirect('view_cart')
                    
                    total_amount += product.price * quantity
                    order_items.append({
                        'product': product,
                        'quantity': quantity,
                        'price': product.price
                    })
                except Product.DoesNotExist:
                    messages.error(request, f'Product with ID {product_id} not found.')
                    return redirect('view_cart')
            
            # Create order
            order = Order.objects.create(
                customer=request.user,
                total_amount=total_amount,
                shipping_address=form.cleaned_data['shipping_address'],
                phone_number=form.cleaned_data['phone_number'],
                notes=form.cleaned_data['notes']
            )
            
            # Create order items
            for item_data in order_items:
                OrderItem.objects.create(
                    order=order,
                    product=item_data['product'],
                    quantity=item_data['quantity'],
                    price=item_data['price']
                )
                
                # Update stock
                product = item_data['product']
                product.stock_quantity -= item_data['quantity']
                product.update_stock_status()
            
            # Clear cart
            request.session['cart'] = {}
            
            messages.success(request, f'Order {order.order_number} placed successfully!')
            return redirect('order_detail', order_id=order.id)
    else:
        form = CheckoutForm()
    
    # Get cart items for display
    cart_items = []
    cart_data = request.session.get('cart', {})
    total = 0
    
    for product_id, quantity in cart_data.items():
        try:
            product = Product.objects.get(id=product_id)
            item_total = product.price * quantity
            total += item_total
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total': item_total
            })
        except Product.DoesNotExist:
            continue
    
    return render(request, 'store/checkout.html', {
        'form': form,
        'cart_items': cart_items,
        'total': total
    })


@login_required
def order_history(request):
    """Display user's order history"""
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'store/order_history.html', {
        'orders': page_obj
    })


@login_required
def order_detail(request, order_id):
    """Display detailed view of a specific order"""
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    return render(request, 'store/order_detail.html', {
        'order': order
    })


@login_required
def cancel_order(request, order_id):
    """Cancel an order (only if it's still pending)"""
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    if order.status == 'pending':
        order.status = 'cancelled'
        order.save()
        
        # Restore stock
        for item in order.items.all():
            product = item.product
            product.stock_quantity += item.quantity
            product.update_stock_status()
        
        messages.success(request, f'Order {order.order_number} has been cancelled.')
    else:
        messages.error(request, 'This order cannot be cancelled.')
    
    return redirect('order_detail', order_id=order.id)


