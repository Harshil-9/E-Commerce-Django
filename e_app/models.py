from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from datetime import datetime
from django.contrib.auth import get_user_model
from django.conf import settings  

class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError("Enter Valid Email.")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        return self.create_user(email, name, password, **extra_fields)

    
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True) 

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = CustomUserManager()

    def __str__(self):
        return self.name

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
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"Order #{self.pk} by {self.customer.email}"
    
class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    laptop = models.ForeignKey(Laptop, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=100, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.razorpay_order_id} - {self.status}"


class Review(models.Model):
    product = models.ForeignKey(Laptop, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1 to 5 stars
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')  # Only one review per user per product


