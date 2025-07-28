from django import forms
from .models import Product, Order, OrderItem


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image', 'category', 'subcategory', 'stock_quantity', 'low_stock_threshold']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:ring-2 focus:ring-indigo-400 focus:border-indigo-400 transition-all duration-200',
                'placeholder': 'Enter product name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:ring-2 focus:ring-indigo-400 focus:border-indigo-400 transition-all duration-200 resize-none',
                'rows': 4,
                'placeholder': 'Describe your product features, specifications, and benefits...'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:ring-2 focus:ring-indigo-400 focus:border-indigo-400 transition-all duration-200',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:ring-2 focus:ring-indigo-400 focus:border-indigo-400 transition-all duration-200'
            }),
            'subcategory': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:ring-2 focus:ring-indigo-400 focus:border-indigo-400 transition-all duration-200'
            }),
            'stock_quantity': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:ring-2 focus:ring-green-400 focus:border-green-400 transition-all duration-200',
                'placeholder': '0',
                'min': '0'
            }),
            'low_stock_threshold': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:ring-2 focus:ring-orange-400 focus:border-orange-400 transition-all duration-200',
                'placeholder': '10',
                'min': '0'
            }),
            'image': forms.FileInput(attrs={
                'class': 'hidden',
                'accept': 'image/*'
            })
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price and price < 0:
            raise forms.ValidationError("Price cannot be negative.")
        return price

    def clean_stock_quantity(self):
        stock_quantity = self.cleaned_data.get('stock_quantity')
        if stock_quantity is not None and stock_quantity < 0:
            raise forms.ValidationError("Stock quantity cannot be negative.")
        return stock_quantity

    def clean_low_stock_threshold(self):
        low_stock_threshold = self.cleaned_data.get('low_stock_threshold')
        if low_stock_threshold is not None and low_stock_threshold < 0:
            raise forms.ValidationError("Low stock threshold cannot be negative.")
        return low_stock_threshold

    def clean(self):
        cleaned_data = super().clean()
        stock_quantity = cleaned_data.get('stock_quantity')
        low_stock_threshold = cleaned_data.get('low_stock_threshold')
        
        if stock_quantity is not None and low_stock_threshold is not None:
            if low_stock_threshold > stock_quantity:
                raise forms.ValidationError("Low stock threshold cannot be greater than current stock quantity.")
        
        return cleaned_data


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['shipping_address', 'phone_number', 'notes']
        widgets = {
            'shipping_address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter your complete shipping address'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Enter your phone number'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Any special instructions or notes (optional)'}),
        }


class CheckoutForm(forms.Form):
    shipping_address = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3, 
            'placeholder': 'Enter your complete shipping address',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'
        }),
        max_length=500,
        help_text='Please provide your complete shipping address'
    )
    phone_number = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your phone number',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'
        }),
        max_length=15,
        help_text='Phone number for delivery updates'
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 2, 
            'placeholder': 'Any special instructions or notes (optional)',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'
        }),
        required=False,
        help_text='Optional notes for your order'
    )
