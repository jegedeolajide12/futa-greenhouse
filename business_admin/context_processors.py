from products.models import Order

def admin_order_badge(request):
    if request.user.is_authenticated and request.user.is_staff:
        pending_count = Order.objects.filter(status='pending').count()
        return {'pending_orders_count': pending_count}
    return {'pending_orders_count': 0}