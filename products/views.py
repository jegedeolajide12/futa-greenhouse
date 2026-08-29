import json

from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST, require_GET
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.templatetags.static import static
from .models import CartItem, Order, OrderItem, Product, BulkPricing, Cart


def get_cart(request):
    """
    Retrieve the active cart for the current user or session.
    """
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        return cart
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
        return cart

def save_cart(request, cart):
    request.session['cart'] = cart

@require_POST
def cart_add(request):
    data = json.loads(request.body)
    product_id = int(data.get('product_id'))
    quantity = int(data.get('quantity', 1))

    product = get_object_or_404(Product, id=product_id, is_available=True)

    cart = get_cart(request)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if created:
        cart_item.quantity = quantity
    else:
        cart_item.quantity += quantity
    cart_item.save()

    total_items = cart.get_item_count()
    return JsonResponse({'success': True, 'cart_count': total_items})

@require_GET
def cart_items(request):
    cart = get_cart(request)
    items = []
    total = 0
    for item in cart.items.select_related('product'):
        price = float(item.product.discount_price if item.product.discount_price and item.product.discount_price < item.product.price else item.product.price)
        subtotal = price * item.quantity
        items.append({
            'id': str(item.product.id),
            'name': item.product.name,
            'quantity': item.quantity,
            'price': price,
            'unit': item.product.get_unit_display(),
            'image': item.product.featured_image.url if item.product.featured_image else None,
            'slug': item.product.slug,
            'subtotal': subtotal,
        })
        total += subtotal

    return JsonResponse({
        'items': items,
        'total': total,
        'count': cart.get_item_count(),
        'empty': items == [],
    })

@require_POST
def cart_remove(request):
    data = json.loads(request.body)
    product_id = int(data.get('product_id'))

    cart = get_cart(request)
    cart_item = CartItem.objects.filter(cart=cart, product_id=product_id).first()
    if cart_item:
        cart_item.delete()

    total_items = cart.get_item_count()
    return JsonResponse({'success': True, 'cart_count': total_items})

def clear_cart(cart):
    """Delete all items in a cart."""
    cart.items.all().delete()


@require_POST
def place_order(request):
    data = json.loads(request.body)

    required = ['full_name', 'email', 'phone', 'address', 'city', 'state']
    for field in required:
        if not data.get(field):
            return JsonResponse({'error': f'Missing field: {field}'}, status=400)

    cart = get_cart(request)
    if not cart.items.exists():
        return JsonResponse({'error': 'Cart is empty'}, status=400)

    subtotal = cart.get_total()
    delivery_fee = 500
    total = subtotal + delivery_fee

    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        full_name=data['full_name'],
        email=data['email'],
        phone=data['phone'],
        address=data['address'],
        city=data['city'],
        state=data['state'],
        delivery_notes=data.get('delivery_notes', ''),
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        total=total,
        payment_method='cod',  # Cash on Delivery
        status='pending',
    )

    for item in cart.items.select_related('product'):
        OrderItem.objects.create(
            order=order,
            product=item.product,
            product_name=item.product.name,
            product_price=item.product.price,
            quantity=item.quantity,
            unit=item.product.get_unit_display(),
        )

    cart.items.all().delete()  # Clear cart

    return JsonResponse({
        'success': True,
        'order_id': order.id,
        'total': float(total),
        'message': 'Order placed! You will pay on delivery.'
    })



class ShopPageView(TemplateView):
    template_name = "products/shop.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products_qs = Product.objects.filter(is_available=True)
        product_list = []

        for p in products_qs:
            # ----- Price logic (fixed) -----
            if p.discount_price and p.discount_price < p.price:
                current_price = float(p.discount_price)
                original_price = float(p.price)
                discount_percent = int(((original_price - current_price) / original_price) * 100)
                discount_label = f"-{discount_percent}%"
            else:
                current_price = float(p.price)
                original_price = None          # No discount, so no old price
                discount_label = None

            # ----- Image URL (unchanged) -----
            if p.featured_image and p.featured_image.name:
                image_url = p.featured_image.url
            else:
                cat_map = {'habanero': 'haba', 'bell': 'bell'}
                filename = f"{p.color}-{cat_map.get(p.category, p.category)}.webp"
                image_url = static(f'images/{filename}')

            # ----- Unit label (unchanged) -----
            unit_label = '1kg' if p.unit == 'kg' else 'piece' if p.unit == 'piece' else p.get_unit_display()

            # ----- Stock status (unchanged) -----
            stock_status = 'in' if p.stock > 0 else 'pre'
            stock_label = 'In Stock' if p.stock > 0 else 'Pre-Order'

            # ----- Variant (unchanged) -----
            variant = p.get_grade_display() if p.grade else ''

            # ----- Build product dict -----
            product_dict = {
                'id': p.id,
                'slug': p.slug,   
                'name': p.name,
                'variant': variant,
                'price': current_price,           # Always a number
                'oldPrice': original_price,       # Only set when discounted
                'unit': unit_label,
                'image': image_url,
                'badge': p.get_grade_display(),
                'discount': discount_label,       # e.g., "-25%"
                'type': p.category.slug,
                'color': p.color,
                'stock': stock_status,
                'stockLabel': stock_label,
            }
            product_list.append(product_dict)

        context['product_data'] = product_list
        return context
    


class HarvestPageView(TemplateView):
    template_name = "pages/harvest.html"

class BulkOrderPageView(TemplateView):
    template_name = "products/bulk_order.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get all active bulk pricings, prefetch product info
        bulk_prices = BulkPricing.objects.filter(is_active=True).select_related('product')
        context['bulk_prices'] = bulk_prices
        # Optionally group by product category if needed

        # Add to get_context_data
        context['products'] = Product.objects.filter(is_available=True)
        return context

class ProductDetailPageView(TemplateView):
    template_name = "products/product.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = kwargs.get('slug')
        
        # Get the product or 404
        product = get_object_or_404(Product, slug=slug, is_available=True)
        
        # Build product dict (same shape as shop view)
        # ----- Price logic -----
        if product.discount_price and product.discount_price < product.price:
            current_price = float(product.discount_price)
            original_price = float(product.price)
            discount_percent = int(((original_price - current_price) / original_price) * 100)
            discount_label = f"-{discount_percent}%"
            badge_type = 'sale'
        else:
            current_price = float(product.price)
            original_price = None
            discount_label = None
            badge_type = None

        # ----- Image URL -----
        if product.featured_image and product.featured_image.name:
            image_url = product.featured_image.url
        else:
            cat_map = {'habanero': 'haba', 'bell': 'bell'}
            filename = f"{product.color}-{cat_map.get(product.category, product.category)}.webp"
            image_url = static(f'images/{filename}')

        # ----- Unit label -----
        unit_label = '1kg' if product.unit == 'kg' else 'piece' if product.unit == 'piece' else product.get_unit_display()

        # ----- Stock status -----
        stock_status = 'in' if product.stock > 0 else 'pre'
        stock_label = 'In Stock' if product.stock > 0 else 'Pre-Order'

        # ----- Variant (grade) -----
        variant = product.get_grade_display() if product.grade else ''

        # ----- Build the product dict (exactly like shop) -----
        product_dict = {
            'id': product.id,
            'name': product.name,
            'slug': product.slug,
            'variant': variant,
            'price': current_price,
            'oldPrice': original_price,
            'unit': unit_label,
            'image': image_url,
            'badge': product.get_grade_display(),
            'discount': discount_label,
            'type': product.category,
            'color': product.color,
            'stock': stock_status,
            'stockLabel': stock_label,
            'description': product.description,
            'grade': product.grade,
        }
        context['product'] = product_dict

        # ----- Related products (same category, exclude current) -----
        related_qs = Product.objects.filter(
            category=product.category,
            is_available=True
        ).exclude(id=product.id)[:4]  # limit to 4

        related_list = []
        for p in related_qs:
            # Simple price for related (no discount logic needed, but we can keep it simple)
            price_float = float(p.discount_price) if p.discount_price and p.discount_price < p.price else float(p.price)
            # Image
            if p.featured_image and p.featured_image.name:
                img_url = p.featured_image.url
            else:
                cat_map = {'habanero': 'haba', 'bell': 'bell'}
                filename = f"{p.color}-{cat_map.get(p.category, p.category)}.webp"
                img_url = static(f'images/{filename}')
            related_list.append({
                'slug': p.slug,
                'name': p.name,
                'price': price_float,
                'unit': p.get_unit_display(),
                'image': img_url,
            })
        context['related_products'] = related_list

        return context



@require_POST
def cart_update(request):
    data = json.loads(request.body)
    product_id = int(data.get('product_id'))
    new_quantity = int(data.get('quantity', 0))

    cart = get_cart(request)
    cart_item = CartItem.objects.filter(cart=cart, product_id=product_id).first()
    if cart_item:
        if new_quantity <= 0:
            cart_item.delete()
        else:
            cart_item.quantity = new_quantity
            cart_item.save()

    total_items = cart.get_item_count()
    return JsonResponse({'success': True, 'cart_count': total_items})


class CartPageView(TemplateView):
    template_name = "products/cart.html"

class CheckoutPageView(LoginRequiredMixin, TemplateView):
    template_name = "products/checkout.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = get_cart(self.request)
        items = []
        total = 0
        for item in cart.items.select_related('product'):
            price = float(item.product.discount_price if item.product.discount_price and item.product.discount_price < item.product.price else item.product.price)
            subtotal = price * item.quantity
            items.append({
                'id': item.product.id,
                'name': item.product.name,
                'quantity': item.quantity,
                'price': price,
                'unit': item.product.get_unit_display(),
                'image': item.product.featured_image.url if item.product.featured_image else None,
                'subtotal': subtotal,
            })
            total += subtotal

        context['cart_items'] = items
        context['cart_total'] = total
        context['delivery'] = 500
        context['grand_total'] = total + 500

        # ---- Fetch last order for logged-in user ----
        if self.request.user.is_authenticated:
            last_order = Order.objects.filter(user=self.request.user).order_by('-created_at').first()
            context['last_order'] = last_order
        else:
            context['last_order'] = None

        return context

class OrdersPageView(TemplateView):
    template_name = "products/orders.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_authenticated:
            orders = Order.objects.filter(user=user).order_by('-created_at')
            order_data = []

            for order in orders:
                items = [
                    {
                        'name': item.product_name,
                        'qty': item.quantity,
                        'price': float(item.product_price),
                    }
                    for item in order.items.all()
                ]

                # Format a friendly order ID
                order_id = f"ORD-{order.id:04d}"

                # Delivery estimate (example: 3 days after order)
                delivery_date = (order.created_at + timezone.timedelta(days=3)).strftime('%Y-%m-%d')

                order_data.append({
                    'id': order_id,
                    'date': order.created_at.strftime('%Y-%m-%d'),
                    'status': order.status,
                    'statusLabel': order.get_status_display(),
                    'items': items,
                    'total': float(order.total),
                    'deliveryDate': delivery_date,
                    'deliveryTime': '10:00 AM - 2:00 PM',  # placeholder
                    'deliveryAddress': order.address,
                })

            context['orders_data'] = order_data
        else:
            context['orders_data'] = []   # empty for anonymous

        return context