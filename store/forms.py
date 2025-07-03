from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'subcategory', 'description', 'price', 'image']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-400'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-400'
            }),
            'subcategory': forms.Select(attrs={
                'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-400'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-400',
                'rows': 4
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-400'
            }),
        }
