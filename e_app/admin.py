from django.contrib import admin
from .models import CustomUser, Laptop, Order, Category, Payment, Review
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    readonly_fields = ['date_joined']
    list_display = ('email', 'name', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff')
    search_fields = ('email', 'name')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'name', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)

class LaptopAdmin(admin.ModelAdmin):
    model = Laptop
    list_display = ('product_image','name', 'price', 'ram', 'storage', 'processor_name', 'is_available', 'date_buy')
    list_filter = ('is_available', 'processor_brand', 'operating_system')
    search_fields = ('name', 'processor_name', 'processor_brand')

admin.site.register(Laptop, LaptopAdmin)

class OrderAdmin(admin.ModelAdmin):
    model = Order
    list_display = ('laptop','customer', 'quantity', 'price', 'address', 'phone', 'status')
    list_filter = ('customer', 'price')
    search_fields = ('laptop','customer','price')

admin.site.register(Order, OrderAdmin)

class CategoryAdmin(admin.ModelAdmin):
    model = Category
    list_display = ('name',)

admin.site.register(Category, CategoryAdmin)

class PaymentAdmin(admin.ModelAdmin):
    model = Payment  
    list_display = ('user', 'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature', 'amount', 'status', 'created_at')
    list_filter = ('status', 'razorpay_order_id', 'razorpay_payment_id')
    search_fields = ('razorpay_order_id', 'razorpay_payment_id', 'user__email')

admin.site.register(Payment, PaymentAdmin)

class ReviewAdmin(admin.ModelAdmin):
    model = Review  


admin.site.register(Review, ReviewAdmin)