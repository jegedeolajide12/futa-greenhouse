from django.urls import path

from .views import (
    OrdersPageView, ShopPageView, HarvestPageView, BulkOrderPageView, ProductDetailPageView,  CartPageView, CheckoutPageView, 
    cart_add, cart_items, cart_remove, cart_update, place_order
)

app_name = "products"

urlpatterns = [
    path("shop/", ShopPageView.as_view(), name="shop"),
    path("harvest/", HarvestPageView.as_view(), name="harvest"),
    path("bulk-order/", BulkOrderPageView.as_view(), name="bulk_order"),
    path('product/<slug:slug>/', ProductDetailPageView.as_view(), name='product_detail'),
    path("cart/", CartPageView.as_view(), name="cart"),
    path("checkout/", CheckoutPageView.as_view(), name="checkout"),
    path("orders/", OrdersPageView.as_view(), name="orders"),
    # Cart API endpoints
    path('cart/add/', cart_add, name='cart_add'),
    path('cart/items/', cart_items, name='cart_items'),
    path('cart/remove/', cart_remove, name='cart_remove'),
    path('cart/update/', cart_update, name='cart_update'),
    path('checkout/place-order/', place_order, name='place_order'),
]