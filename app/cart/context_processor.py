from .models import Cart

def cart_processor(request):
    cart = Cart(request)
    
    return {
        'cart': cart,
        'cart_total_items': len(cart),
        'cart_sumtotal': cart.get_total_price(), 
    }