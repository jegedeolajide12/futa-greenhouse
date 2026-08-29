from decimal import Decimal
import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from products.models import Order, OrderItem, Product, Category


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "business_admin/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        prev_month_start = (month_start - timedelta(days=1)).replace(day=1)

        # ---------- CURRENT MONTH ----------
        orders_current = Order.objects.filter(created_at__gte=month_start).count()
        revenue_current = Order.objects.filter(created_at__gte=month_start).aggregate(total=Sum('total'))['total'] or 0
        customers_current = Order.objects.filter(created_at__gte=month_start).values('email').distinct().count()
        products_current = Product.objects.filter(is_available=True).count()

        # ---------- PREVIOUS MONTH ----------
        orders_prev = Order.objects.filter(created_at__gte=prev_month_start, created_at__lt=month_start).count()
        revenue_prev = Order.objects.filter(created_at__gte=prev_month_start, created_at__lt=month_start).aggregate(total=Sum('total'))['total'] or 0
        customers_prev = Order.objects.filter(created_at__gte=prev_month_start, created_at__lt=month_start).values('email').distinct().count()
        products_prev = Product.objects.filter(is_available=True, created_at__lt=month_start).count()

        # ---------- COMPUTE CHANGES ----------
        def calc_change(current, previous):
            if previous == 0:
                return 0.0, 'up' if current > 0 else 'down' if current < 0 else 'none'
            change = ((current - previous) / previous) * 100
            return round(change, 1), 'up' if change >= 0 else 'down'

        orders_change, orders_dir = calc_change(orders_current, orders_prev)
        revenue_change, revenue_dir = calc_change(float(revenue_current), float(revenue_prev))
        customers_change, customers_dir = calc_change(customers_current, customers_prev)

        products_change = products_current - products_prev
        products_dir = 'up' if products_change >= 0 else 'down'
        products_change_abs = abs(products_change)

        # ---------- RECENT ORDERS (latest 5) ----------
        recent_orders = Order.objects.select_related('user').order_by('-created_at')[:5]
        recent_orders_data = []
        for order in recent_orders:
            items = order.items.all()
            products_summary = ", ".join([
                f"{item.product_name} ×{item.quantity}" for item in items[:3]
            ])
            if items.count() > 3:
                products_summary += f" +{items.count() - 3} more"
            recent_orders_data.append({
                'id': order.id,  # actual DB id
                'order_id': f"ORD-{order.id:04d}",
                'customer': order.full_name,
                'products': products_summary,
                'total': float(order.total),
                'status': order.status,
                'date': order.created_at.strftime('%Y-%m-%d'),
            })

        # ---------- INVENTORY (first 5 products) ----------
        inventory = Product.objects.filter(is_available=True).order_by('name')[:5]
        inventory_data = []
        for p in inventory:
            stock_display = f"{p.stock}{p.unit}"
            if p.stock <= 0:
                status_class = 'out-of-stock'
                status_label = 'Out of Stock'
            elif p.stock <= 10:
                status_class = 'low-stock'
                status_label = 'Low Stock'
            else:
                status_class = 'in-stock'
                status_label = 'In Stock'
            inventory_data.append({
                'id': p.id,
                'name': p.name,
                'variant': p.get_grade_display() if p.grade else '',
                'price': float(p.price),
                'stock': p.stock,
                'stock_display': stock_display,
                'is_available': p.is_available,
                'status_class': status_class,
                'status_label': status_label,
            })

        # ---------- CHART: Weekly Revenue ----------
        week_dates = [now - timedelta(days=i) for i in range(6, -1, -1)]
        week_labels = [d.strftime('%a') for d in week_dates]
        week_revenue = []
        for day in week_dates:
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            rev = Order.objects.filter(
                created_at__gte=day_start,
                created_at__lt=day_end
            ).aggregate(total=Sum('total'))['total'] or 0
            week_revenue.append(float(rev))

        # ---------- CHART: Order Status Counts ----------
        status_counts = Order.objects.values('status').annotate(count=Count('id'))
        status_map = {
            'pending': 'Pending',
            'paid': 'Paid',
            'shipped': 'Shipped',
            'delivered': 'Delivered',
            'cancelled': 'Cancelled',
        }
        status_labels = [status_map.get(s['status'], s['status']) for s in status_counts]
        status_data = [s['count'] for s in status_counts]

        # ---------- BUILD FINAL CONTEXT ----------
        context.update({
            'total_orders': orders_current,
            'revenue_this_month': revenue_current,
            'total_customers': customers_current,
            'products_available': products_current,
            'orders_change': abs(orders_change),
            'orders_dir': orders_dir,
            'revenue_change': abs(revenue_change),
            'revenue_dir': revenue_dir,
            'customers_change': abs(customers_change),
            'customers_dir': customers_dir,
            'products_change': products_change_abs,
            'products_dir': products_dir,
            'recent_orders': recent_orders_data,
            'inventory': inventory_data,
            'week_labels': week_labels,
            'week_revenue': week_revenue,
            'status_labels': status_labels,
            'status_data': status_data,
        })

        return context


@require_POST
@login_required
def admin_update(request):
    try:
        data = json.loads(request.body)
        obj_id = data.get('id')
        obj_type = data.get('type')

        if obj_type == 'order':
            obj = Order.objects.get(id=obj_id)
            obj.status = data.get('status')
            obj.save()
        elif obj_type == 'product':
            obj = Product.objects.get(id=obj_id)
            if 'price' in data:
                obj.price = data['price']
            if 'stock' in data:
                obj.stock = data['stock']
            if 'is_available' in data:
                obj.is_available = data['is_available']
            if 'discount_price' in data:
                obj.discount_price = data['discount_price'] if data['discount_price'] else None
            obj.save()
        else:
            return JsonResponse({'error': 'Invalid type'}, status=400)

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
@require_POST
@login_required
def admin_delete_order(request):
    try:
        data = json.loads(request.body)
        order_id = data.get('id')
        order = Order.objects.get(id=order_id)
        order.delete()
        return JsonResponse({'success': True})
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_POST
@login_required
def admin_delete_product(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('id')
        product = Product.objects.get(id=product_id)
        product.delete()
        return JsonResponse({'success': True})
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)



class OrdersAdminView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "business_admin/orders.html"
    context_object_name = "orders"
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset().select_related('user')

        # Search by customer name, email, or order ID
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search) |
                Q(email__icontains=search) |
                Q(id__icontains=search)
            )

        # Filter by status
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(status=status)

        # Filter by date range
        date_from = self.request.GET.get('date_from', '')
        date_to = self.request.GET.get('date_to', '')
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass current filters back to template for form persistence
        context['current_filters'] = {
            'search': self.request.GET.get('search', ''),
            'status': self.request.GET.get('status', ''),
            'date_from': self.request.GET.get('date_from', ''),
            'date_to': self.request.GET.get('date_to', ''),
        }
        return context



class ProductsAdminView(LoginRequiredMixin, ListView):
    model = Product
    template_name = "business_admin/products.html"
    context_object_name = "products"
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
        category = self.request.GET.get('category', '')
        if category:
            queryset = queryset.filter(category=category)
        color = self.request.GET.get('color', '')
        if color:
            queryset = queryset.filter(color=color)
        grade = self.request.GET.get('grade', '')
        if grade:
            queryset = queryset.filter(grade=grade)
        is_available = self.request.GET.get('is_available', '')
        if is_available:
            queryset = queryset.filter(is_available=(is_available == 'true'))
        return queryset.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_filters'] = {
            'search': self.request.GET.get('search', ''),
            'category': self.request.GET.get('category', ''),
            'color': self.request.GET.get('color', ''),
            'grade': self.request.GET.get('grade', ''),
            'is_available': self.request.GET.get('is_available', ''),
        }
        context['category_choices'] = Product.CategoryChoices.choices
        context['color_choices'] = Product.ColorChoices.choices
        context['grade_choices'] = Product.GradeChoices.choices
        context['unit_choices'] = Product.UnitChoices.choices
        context['is_ajax'] = self.request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        return context

@require_POST
@login_required
def admin_add_product(request):
    try:
        data = json.loads(request.body)
        name = data.get('name')
        category = data.get('category')
        color = data.get('color')
        grade = data.get('grade')
        price = data.get('price')
        stock = data.get('stock')
        unit = data.get('unit')
        is_available = data.get('is_available', True)
        description = data.get('description', '')
        if not name or not category or not color or not grade or price is None or stock is None:
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        product = Product.objects.create(
            name=name,
            category=category,
            color=color,
            grade=grade,
            price=price,
            stock=stock,
            unit=unit,
            is_available=is_available,
            description=description,
        )
        return JsonResponse({'success': True, 'product_id': product.id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_POST
@login_required
def admin_delete_product(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('id')
        product = Product.objects.get(id=product_id)
        product.delete()
        return JsonResponse({'success': True})
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


class CustomersAdminView(LoginRequiredMixin, ListView):
    template_name = "business_admin/customers.html"
    context_object_name = "customers"
    paginate_by = 15

    def get_queryset(self):
        # Get all orders, group by email (unique customers)
        queryset = Order.objects.values('email', 'full_name', 'phone', 'address', 'city', 'state')
        queryset = queryset.annotate(
            order_count=Count('id'),
            total_spent=Sum('total')
        ).order_by('-total_spent')

        # Search
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_filters'] = {
            'search': self.request.GET.get('search', ''),
        }
        return context


@require_GET
@login_required
def customer_orders_api(request):
    email = request.GET.get('email')
    if not email:
        return JsonResponse({'error': 'Email required'}, status=400)
    orders = Order.objects.filter(email=email).order_by('-created_at')
    if not orders.exists():
        return JsonResponse({'error': 'Customer not found'}, status=404)
    customer = orders.first()
    data = {
        'customer': {
            'full_name': customer.full_name,
            'email': customer.email,
            'phone': customer.phone,
            'city': customer.city,
            'state': customer.state,
            'order_count': orders.count(),
            'total_spent': sum(o.total for o in orders),
        },
        'orders': [
            {
                'id': o.id,
                'created_at': o.created_at.strftime('%Y-%m-%d %H:%M'),
                'total': float(o.total),
                'status': o.status,
                'status_label': o.get_status_display(),
            }
            for o in orders
        ]
    }
    return JsonResponse(data)



class DeliveriesAdminView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "business_admin/deliveries.html"
    context_object_name = "orders"
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset().select_related('user')

        # Only filter by status if a specific status is provided
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(status=status)

        # Search filter
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search) |
                Q(email__icontains=search) |
                Q(id__icontains=search)
            )

        # Date range filters
        date_from = self.request.GET.get('date_from', '')
        date_to = self.request.GET.get('date_to', '')
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)

        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_filters'] = {
            'search': self.request.GET.get('search', ''),
            'status': self.request.GET.get('status', ''),
            'date_from': self.request.GET.get('date_from', ''),
            'date_to': self.request.GET.get('date_to', ''),
        }
        return context




class CategoriesAdminView(LoginRequiredMixin, ListView):
    model = Category
    template_name = "business_admin/categories.html"
    context_object_name = "categories"
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_filters'] = {
            'search': self.request.GET.get('search', ''),
        }
        return context

@require_POST
@login_required
def admin_add_category(request):
    try:
        data = json.loads(request.body)
        name = data.get('name')
        description = data.get('description', '')
        if not name:
            return JsonResponse({'error': 'Name is required'}, status=400)
        category = Category.objects.create(name=name, description=description)
        return JsonResponse({'success': True, 'category_id': category.id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_POST
@login_required
def admin_update_category(request):
    try:
        data = json.loads(request.body)
        category_id = data.get('id')
        name = data.get('name')
        description = data.get('description', '')
        category = Category.objects.get(id=category_id)
        category.name = name
        category.description = description
        category.save()
        return JsonResponse({'success': True})
    except Category.DoesNotExist:
        return JsonResponse({'error': 'Category not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_POST
@login_required
def admin_delete_category(request):
    try:
        data = json.loads(request.body)
        category_id = data.get('id')
        category = Category.objects.get(id=category_id)
        if category.products.exists():
            return JsonResponse({'error': 'Cannot delete category with existing products. Reassign products first.'}, status=400)
        category.delete()
        return JsonResponse({'success': True})
    except Category.DoesNotExist:
        return JsonResponse({'error': 'Category not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)



class DiscountsAdminView(LoginRequiredMixin, ListView):
    model = Product
    template_name = "business_admin/discounts.html"
    context_object_name = "products"
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset().order_by('name')
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(name__icontains=search)

        only_discounted = self.request.GET.get('discounted', '')
        if only_discounted == 'true':
            queryset = queryset.filter(discount_price__isnull=False, discount_price__lt=F('price'))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = context['products']
        for product in products:
            product.is_discounted = (product.discount_price is not None and product.discount_price < product.price)
            if product.is_discounted:
                product.discount_percent = int(((product.price - product.discount_price) / product.price) * 100)
            else:
                product.discount_percent = None
        context['current_filters'] = {
            'search': self.request.GET.get('search', ''),
            'discounted': self.request.GET.get('discounted', ''),
        }
        return context

@require_POST
@login_required
def admin_bulk_discount(request):
    try:
        data = json.loads(request.body)
        apply_to = data.get('apply_to', 'all')
        discount_type = data.get('discount_type', 'percentage')
        value = Decimal(str(data.get('value', 0)))

        if apply_to != 'all':
            return JsonResponse({'error': 'Only "All Products" is currently supported.'}, status=400)

        products = Product.objects.all()
        updated = 0

        for product in products:
            if discount_type == 'percentage':
                # new_price = price * (1 - value/100)
                discount_factor = Decimal('1') - (value / Decimal('100'))
                new_price = product.price * discount_factor
            else:  # fixed amount
                new_price = product.price - value

            # Only apply if new price is positive
            if new_price > 0:
                # Round to 2 decimal places
                product.discount_price = new_price.quantize(Decimal('0.01'))
                product.save()
                updated += 1

        return JsonResponse({'success': True, 'updated': updated})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)