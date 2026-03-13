from decimal import Decimal
from django.shortcuts import get_object_or_404
from main.models import Product, ProductSize

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get("cart")
        if not cart:
            cart = self.session["cart"] = {}
        self.cart = cart
        
    def add(self, product,product_size, quantity=1, override_quantity=False):
        product_id = str(product.id)
        size_id = str(product_size.id)
        
        cart_key = f"{product_id}_{size_id}"
        
        if cart_key not in self.cart:
            self.cart[cart_key] = {
                'quantity': 0,
                'price' : str(product_size.price),
                'product_id' : product_id,
                'size_id' : size_id,
                'size_name' : product_size.size.name
            }
        if override_quantity:
            self.cart[cart_key]['quantity'] = int(quantity)
        else:
            self.cart[cart_key]['quantity'] += int(quantity)
            
        self.save()
            
    def save(self):
        self.session.modified = True
        
    def remove(self, cart_key):
        if cart_key in self.cart:
            del self.cart[cart_key]
            self.save()
        
    def update(self, product, product_size, quantity):
        cart_key = f"{product.id}_{product_size.id}"
        if quantity <=0:
            self.remove(cart_key)
        else:
            self.add(product, product_size, quantity, override_quantity=True)
            
    def __iter__(self):
        product_ids = [item['product_id'] for item in self.cart.values()]
        products = Product.objects.filter(id__in = product_ids)
        product_dict = {str(p.id): p for p in products}
        
        for cart_key, item in self.cart.items():
            item['product'] = product_dict.get(item['product_id'])
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            item['cart_key'] = cart_key
            yield item
            
        """for product in products:
            for cart_key, cart_item in cart.items():
                if cart_item['product_id'] == str(product.id):
                    cart_item['product'] = product
                    cart_item['total_price'] = Decimal(cart_item['price']) * cart
                    yield cart_item"""
                    
    def __len__(self):
        length = sum(item['quantity'] for item in self.cart.values())
        return length
    
    def get_total_price(self):
        total = sum(Decimal(item['price']) * item['quantity']
                    for item in self.cart.values())
        return total
    
    def clear(self):
        if 'cart' in self.session:
            del self.session['cart']
            self.save()
            
    def get_cart_items(self):
        items = [item for item in self]
        return items
    
    '''def get_cart_items(self):
        items = []
        for item in self:
            items.append({
                'product' : item['product'],
                'quantity' : item['quntity'],
                'size' : item['size'],
                'price' : Decimal(item['price']),
                'total_price' : item['total_price'],
                'cart_key': f"{item['product_id']}_{item['size']}"
            })'''