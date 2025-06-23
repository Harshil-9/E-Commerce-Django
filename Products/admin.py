from django.contrib import admin
from .models import Laptop, Order, Category, Review


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

class ReviewAdmin(admin.ModelAdmin):
    model = Review  


admin.site.register(Review, ReviewAdmin)