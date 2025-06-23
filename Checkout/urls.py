from django.urls import path
from .views import (
    PaymentHandlerView, CheckoutView,
    Paymentsuccess, Paymentfailure
)

urlpatterns = [

    # Checkout & Payment
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('paymenthandler/', PaymentHandlerView.as_view(), name='paymenthandler'),
    path('success/', Paymentsuccess.as_view(), name='success'),
    path('failure/', Paymentfailure.as_view(), name='failure'),

]



