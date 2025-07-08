from django.shortcuts import render, redirect
from .forms import ProductForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Review
from .models import Product, Category, SubCategory
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib import messages
from .models import Wishlist
import csv


@login_required
def add_product(request):
    if request.user.role != 'supplier':
        return HttpResponseForbidden("Only suppliers can upload products.")

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.supplier = request.user
            product.save()
            return redirect('home')  # or 'product_list'
    else:
        form = ProductForm()

    return render(request, 'store/add_product.html', {'form': form})


def home(request):
    return render(request, 'store/home.html')

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

    return render(request, 'store/product_list.html', {
        'products': products,
        'categories': categories,
        'selected_category': category_id,
        'selected_subcategory': subcategory_id,
        'search_query': search_query,  # 👈 pass back to template
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})


@login_required
def supplier_dashboard(request):
    if request.user.role != 'supplier':
        return redirect('product_list')

    products = Product.objects.filter(supplier=request.user).order_by('-created_at')
    return render(request, 'store/supplier_dashboard.html', {'products': products})


@login_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)

    # Prevent other users from editing
    if request.user != product.supplier:
        return redirect('product_list')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('supplier_dashboard')
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


