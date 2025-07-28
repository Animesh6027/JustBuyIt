from django.core.management.base import BaseCommand
from store.models import Product
from django.utils import timezone


class Command(BaseCommand):
    help = 'Update stock levels for all products'

    def add_arguments(self, parser):
        parser.add_argument(
            '--product-id',
            type=int,
            help='Update stock for specific product ID'
        )
        parser.add_argument(
            '--quantity',
            type=int,
            help='Set specific quantity for the product'
        )

    def handle(self, *args, **options):
        if options['product_id']:
            # Update specific product
            try:
                product = Product.objects.get(id=options['product_id'])
                if options['quantity'] is not None:
                    product.stock_quantity = options['quantity']
                else:
                    # Simulate stock update (you can modify this logic)
                    import random
                    product.stock_quantity = max(0, product.stock_quantity + random.randint(-5, 10))
                
                product.update_stock_status()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Updated stock for {product.name}: {product.stock_quantity} units'
                    )
                )
            except Product.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Product with ID {options["product_id"]} not found')
                )
        else:
            # Update all products
            products = Product.objects.all()
            updated_count = 0
            
            for product in products:
                # Simulate stock changes (you can modify this logic)
                import random
                old_quantity = product.stock_quantity
                product.stock_quantity = max(0, product.stock_quantity + random.randint(-3, 8))
                product.update_stock_status()
                
                if old_quantity != product.stock_quantity:
                    updated_count += 1
                    self.stdout.write(
                        f'{product.name}: {old_quantity} → {product.stock_quantity}'
                    )
            
            self.stdout.write(
                self.style.SUCCESS(f'Updated stock for {updated_count} products')
            ) 