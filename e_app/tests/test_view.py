import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from Products.models import Laptop

User = get_user_model()

def create_laptop(**kwargs):
    from Products.models import Category
    category, _ = Category.objects.get_or_create(id=1, defaults={"name": "Default Category"})

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
def test_ajax_search_view(client):
    create_laptop(name="Test Laptop 1")
    create_laptop(name="Another Laptop")

    response = client.get(reverse('ajax_search') + '?q=Test')
    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) == 1
    assert data['results'][0]['name'] == "Test Laptop 1"

@pytest.mark.django_db
def test_product_by_processor_view(client):
    create_laptop(name="Intel Laptop", processor_name="Intel i5")
    response = client.get(reverse('products_by_processor', args=['Intel']))
    assert response.status_code == 200
    assert b"Intel Laptop" in response.content

@pytest.mark.django_db
def test_product_by_price_view(client):
    create_laptop(name="Budget Laptop", price=30000)
    create_laptop(name="Expensive Laptop", price=90000)

    response = client.get(reverse('products_by_price', args=[20000, 40000]))
    assert response.status_code == 200
    assert b"Budget Laptop" in response.content
    assert b"Expensive Laptop" not in response.content

@pytest.mark.django_db
def test_product_by_brand_view(client):
    create_laptop(name="HP Laptop", brand="HP")
    response = client.get(reverse('products_by_brand', args=['HP']))
    assert response.status_code == 200
    assert b"HP Laptop" in response.content

@pytest.mark.django_db
def test_profile_view_authenticated(client):
    user = User.objects.create_user(
        email='test@example.com',
        password='pass123',
        name='Test User'
    )
    client.login(email='test@example.com', password='pass123')
    response = client.get(reverse('profile'))
    assert response.status_code == 200
    assert b"profile" in response.content.lower()

@pytest.mark.django_db
def test_profile_view_unauthenticated(client):
    response = client.get(reverse('profile'))
    assert response.status_code == 302  # Redirect to login
    assert "/login" in response.url.lower()
