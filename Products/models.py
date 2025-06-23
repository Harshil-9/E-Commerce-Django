from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from Auth.models import CustomUser 

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=50)

    @staticmethod
    def get_all_categories():
        return Category.objects.all()

    def __str__(self):
        return self.name

class Laptop(models.Model):
    product_image = models.ImageField(upload_to='product_image/', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    brand = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=255)
    price = models.FloatField()
    ram = models.IntegerField()
    storage = models.IntegerField()
    processor_name = models.TextField(max_length=50)
    processor_brand = models.CharField(max_length=50)
    processor_generation = models.TextField(max_length=50)
    display = models.TextField(max_length=100)
    operating_system = models.TextField(max_length=50)
    battery = models.FloatField()
    graphic_processor = models.CharField(max_length=50)
    touch_screen = models.TextField(max_length=50)
    screen_size = models.TextField(max_length=50)
    screen_resolution = models.TextField(max_length=50)
    is_available = models.BooleanField(default=True)
    date_buy = models.DateField(auto_now_add=True)

    @staticmethod
    def get_products_by_id(ids):
        return Laptop.objects.filter(id__in=ids)

    @staticmethod
    def get_all_products():
        return Laptop.objects.all()

    @staticmethod
    def get_all_products_by_categoryid(category_id):
        if category_id:
            return Laptop.objects.filter(category=category_id)
        else:
            return Laptop.get_all_products()
        
    def get_price_value(self):
        return float(self.price.replace(',', ''))

    def __str__(self):
        return self.name
    
User = get_user_model()
    
class Order(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    laptop = models.ForeignKey('Laptop', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.TextField()
    phone = models.CharField(max_length=15)
    status = models.BooleanField(default=False)  # True = Order placed successfully
    payment = models.ForeignKey('Checkout.Payment', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"Order #{self.pk} by {self.customer.email}"
    
class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    laptop = models.ForeignKey(Laptop, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

class Review(models.Model):
    product = models.ForeignKey(Laptop, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1 to 5 stars
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')  # Only one review per user per product