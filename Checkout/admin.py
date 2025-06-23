from django.contrib import admin
from .models import Payment


class PaymentAdmin(admin.ModelAdmin):
    model = Payment  
    list_display = ('user', 'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature', 'amount', 'status', 'created_at')
    list_filter = ('status', 'razorpay_order_id', 'razorpay_payment_id')
    search_fields = ('razorpay_order_id', 'razorpay_payment_id', 'user__email')

admin.site.register(Payment, PaymentAdmin)

