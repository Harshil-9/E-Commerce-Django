from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    CustomLoginView, CustomRegisterView, UserLogoutView, CustomHomeView,
    ProductDetailView, AllProductView, CartView, AddToCartView,
    RemoveFromCart, CartItemUpdateView, PaymentHandlerView, CheckoutView,
    Paymentsuccess, Paymentfailure, CartCountView, AjaxSearchView, ProductbyProcessor,
    ProductbyPrice, ProductbyBrand, ProfileView
)

urlpatterns = [

    path('profile/', ProfileView.as_view(), name='profile'),

    # Auth
    path('', CustomLoginView.as_view(), name='login'),
    path('register/', CustomRegisterView.as_view(), name='register2'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('logout/', UserLogoutView.as_view(), name='homeproduct'),

    # cart count
    path('api/cart/count/', CartCountView.as_view(), name='cart_count_api'),

    # search
    path('ajax/search/', AjaxSearchView.as_view(), name='ajax_search'),

    # Product
    path('home/', CustomHomeView.as_view(), name='index'),
    path('products/', AllProductView.as_view(), name='all_product'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),

    # Reset password 
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),

    # Cart
    path('cart/', CartView.as_view(), name='cart'),
    path('add-to-cart/<int:pk>/', AddToCartView.as_view(), name='add_to_cart'),
    path('cart/item/<int:pk>/delete/', RemoveFromCart.as_view(), name='cart_item_delete'),
    path('cart/item/update/<int:pk>/', CartItemUpdateView.as_view(), name='cart_item_update'),

    # Checkout & Payment
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('paymenthandler/', PaymentHandlerView.as_view(), name='paymenthandler'),
    path('success/', Paymentsuccess.as_view(), name='success'),
    path('failure/', Paymentfailure.as_view(), name='failure'),

    # filters 
    path('products/processor/<str:processor>/', ProductbyProcessor.as_view(), name='products_by_processor'),
    path('products/price/<int:min_price>/<int:max_price>/', ProductbyPrice.as_view(), name='products_by_price'),
    path('products/brand/<str:brand>/', ProductbyBrand.as_view(), name='products_by_brand'),

    # Review
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail')
]



