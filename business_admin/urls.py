from django.urls import path

from .views import (
    CategoriesAdminView, DashboardView, DeliveriesAdminView, DiscountsAdminView, OrdersAdminView, ProductsAdminView, admin_add_category, 
    admin_add_product, admin_bulk_discount, admin_delete_category, admin_delete_order, 
    admin_delete_product, admin_update, admin_update_category, customer_orders_api, CustomersAdminView
)

app_name = "business_admin"

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("orders/", OrdersAdminView.as_view(), name="orders"),
    path('products/', ProductsAdminView.as_view(), name='products'),
    path('customers/', CustomersAdminView.as_view(), name='customers'),
    path('deliveries/', DeliveriesAdminView.as_view(), name='deliveries'),
    path('categories/', CategoriesAdminView.as_view(), name='categories'),
    path('discounts/', DiscountsAdminView.as_view(), name='discounts'),


    # API endpoint for updating order/product details
    path('api/update/', admin_update, name='admin_update'),
    path('api/delete-order/', admin_delete_order, name='admin_delete_order'),
    path('api/delete-product/', admin_delete_product, name='admin_delete_product'),
    path('api/add-product/', admin_add_product, name='admin_add_product'),
    path('api/delete-product/', admin_delete_product, name='admin_delete_product'),
    path('api/customer-orders/', customer_orders_api, name='customer_orders_api'),
    
    path('api/add-category/', admin_add_category, name='admin_add_category'),
    path('api/update-category/', admin_update_category, name='admin_update_category'),
    path('api/delete-category/', admin_delete_category, name='admin_delete_category'),
    path('api/bulk-discount/', admin_bulk_discount, name='admin_bulk_discount'),
]
