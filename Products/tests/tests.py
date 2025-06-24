import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from Products.models import Laptop, Cart, CartItem, Review

User = get_user_model()

def create_laptop(**kwargs):
    from Products.models import Category
    category, _ = Category.objects.get_or_create(id=1, defaults={'name': 'Test Category'})
    return Laptop.objects.create(
        name=kwargs.get("name", "Laptop X"),
        price=kwargs.get("price", 50000),
        product_image=kwargs.get("product_image", "test.jpg"),
        category=category,
        brand=kwargs.get("brand", "HP"),
        ram=kwargs.get("ram", 8),
        storage=kwargs.get("storage", 256),
        processor_name=kwargs.get("processor_name", "i5"),
        processor_brand=kwargs.get("processor_brand", "Intel"),
        processor_generation=kwargs.get("processor_generation", "10th Gen"),
        display=kwargs.get("display", "15.6 inch FHD"),
        operating_system=kwargs.get("operating_system", "Windows 11"),
        battery=kwargs.get("battery", 4.5),
        graphic_processor=kwargs.get("graphic_processor", "Intel Iris Xe"),
        touch_screen=kwargs.get("touch_screen", "No"),
        screen_size=kwargs.get("screen_size", "15.6"),
        screen_resolution=kwargs.get("screen_resolution", "1920x1080"),
    )

@pytest.mark.django_db
def test_cart_count_view(client):
    user = User.objects.create_user(email='test@example.com', password='testpass', name='Test User')
    client.login(email='test@example.com', password='testpass')
    response = client.get(reverse('cart_count_api'))
    assert response.status_code == 200
    assert 'count' in response.json()

@pytest.mark.django_db
def test_add_to_cart_view(client):
    user = User.objects.create_user(email='user@example.com', password='testpass', name='User')
    laptop = create_laptop()
    client.login(email='user@example.com', password='testpass')
    response = client.post(reverse('add_to_cart', args=[laptop.id]))
    assert response.status_code == 302  # redirect to cart
    assert CartItem.objects.filter(laptop=laptop, cart__user=user).exists()

@pytest.mark.django_db
def test_cart_view(client):
    user = User.objects.create_user(email='user2@example.com', password='testpass', name='User2')
    laptop = create_laptop()
    cart = Cart.objects.create(user=user)
    CartItem.objects.create(cart=cart, laptop=laptop)
    client.login(email='user2@example.com', password='testpass')
    response = client.get(reverse('cart'))
    assert response.status_code == 200
    assert b"Laptop X" in response.content

@pytest.mark.django_db
def test_remove_from_cart_view(client):
    user = User.objects.create_user(email='user3@example.com', password='testpass', name='User3')
    laptop = create_laptop()
    cart = Cart.objects.create(user=user)
    CartItem.objects.create(cart=cart, laptop=laptop)
    client.login(email='user3@example.com', password='testpass')
    response = client.post(reverse('cart_item_delete', args=[laptop.id]))
    assert response.status_code == 302
    assert not CartItem.objects.filter(cart=cart, laptop=laptop).exists()

@pytest.mark.django_db
def test_cart_item_update_view(client):
    user = User.objects.create_user(email='user4@example.com', password='testpass', name='User4')
    laptop = create_laptop()
    cart = Cart.objects.create(user=user)
    item = CartItem.objects.create(cart=cart, laptop=laptop, quantity=1)
    client.login(email='user4@example.com', password='testpass')
    response = client.post(reverse('cart_item_update', args=[laptop.id]), data={'action': 'increment'})
    item.refresh_from_db()
    assert item.quantity == 2

@pytest.mark.django_db
def test_product_detail_view_get(client):
    laptop = create_laptop(name="Detail Laptop")
    url = reverse('product_detail', args=[laptop.id])
    response = client.get(url)
    assert response.status_code == 200
    assert b"Detail Laptop" in response.content

@pytest.mark.django_db
def test_product_detail_view_post_review(client):
    user = User.objects.create_user(email='user5@example.com', password='testpass', name='User5')
    laptop = create_laptop()
    client.login(email='user5@example.com', password='testpass')
    response = client.post(reverse('product_detail', args=[laptop.id]), data={'rating': 5, 'comment': 'Great'})
    assert response.status_code == 302  # redirect after post
    assert Review.objects.filter(user=user, product=laptop).exists()
