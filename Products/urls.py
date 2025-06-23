from django.urls import path
from .views import (
    ProductDetailView, AllProductView, CartView, AddToCartView,
    RemoveFromCart, CartItemUpdateView, CartCountView
)

urlpatterns = [

    # cart count
    path('api/cart/count/', CartCountView.as_view(), name='cart_count_api'),


    # Product
    path('products/', AllProductView.as_view(), name='all_product'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),

    

    # Cart
    path('cart/', CartView.as_view(), name='cart'),
    path('add-to-cart/<int:pk>/', AddToCartView.as_view(), name='add_to_cart'),
    path('cart/item/<int:pk>/delete/', RemoveFromCart.as_view(), name='cart_item_delete'),
    path('cart/item/update/<int:pk>/', CartItemUpdateView.as_view(), name='cart_item_update'),

    # Review
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail')
]



