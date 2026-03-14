from django.db import models
from django.contrib.sessions.models import Session
from main.models import Product, ProductSize
from decimal import Decimal

class Cart(models.Model):
    session_key = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart {self.session_key}"
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all()) # Исправлено item -> items
    
    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())
    
    def add_product(self, product, product_size, quantity):
        # Исправлено имя метода и распаковка (created)
        quantity = int(quantity)
        cart_item, created = CartItem.objects.get_or_create(
            cart=self,
            product=product,
            product_size=product_size,
            defaults={'quantity': quantity}
        )
        # Если товар уже был в корзине (не создан только что), обновляем количество
        if not created:
            cart_item.quantity += int(quantity)
            cart_item.save()
            
        return cart_item
    
    def remove(self, item_id):
        try:
            item = self.items.get(id=item_id)
            item.delete()
            return True
        except CartItem.DoesNotExist:
            return False
        
    def update_item_quantity(self, quantity, item_id):
        try:
            item = self.items.get(id=item_id)
            quantity = int(quantity) #на случай ошибок юлять
            if quantity > 0:
                item.quantity = quantity
                item.save()
            else:
                item.delete()
            return True
        except (CartItem.DoesNotExist, ValueError ):
            return False
        
    def clear(self):
        self.items.all().delete()

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE) # product с маленькой, Product с большой
    product_size = models.ForeignKey(ProductSize, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = (('cart', 'product', 'product_size'),) # Исправлен синтаксис
        
    def __str__(self):
        return f"{self.product.name} ({self.product_size.size.name}) x {self.quantity}"
    
    @property
    def total_price(self):
        return self.product_size.price * self.quantity
