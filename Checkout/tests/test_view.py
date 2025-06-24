from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch
from Products.models import Cart, CartItem, Laptop, Category, Order
from Checkout.models import Payment

User = get_user_model()


class CheckoutViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email="test@example.com", password="pass1234", name="Test User")
        self.client.login(email="test@example.com", password="pass1234")

        self.category = Category.objects.create(name="Test Category")

        self.cart = Cart.objects.create(user=self.user)
        self.laptop = Laptop.objects.create(
            name="Dell XPS",
            price=Decimal('50000'),
            ram=16,
            storage=512,
            processor_name="Intel i7",
            processor_brand="Intel",
            processor_generation="11th Gen",
            display="15.6 inch",
            operating_system="Windows 11",
            battery=6.5,
            graphic_processor="Intel Iris",
            touch_screen="No",
            screen_size="15.6",
            screen_resolution="1920x1080",
            category=self.category
        )

        CartItem.objects.create(cart=self.cart, laptop=self.laptop, quantity=2)

    @patch("Checkout.views.razorpay.Client")
    def test_checkout_creates_payment_and_renders_template(self, mock_client_class):
        mock_client = mock_client_class.return_value
        mock_client.order.create.return_value = {
            'id': 'order_test123',
            'amount': 100000,
            'currency': 'INR',
            'status': 'created'
        }

        response = self.client.get(reverse("checkout"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "checkout.html")

        payment = Payment.objects.get(razorpay_order_id="order_test123")
        self.assertEqual(payment.user, self.user)
        self.assertEqual(payment.amount, Decimal('10000000')) 


class PaymentHandlerTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email="test2@example.com", password="testpass", name="Buyer")
        self.client.login(email="test2@example.com", password="testpass")

        self.category = Category.objects.create(name="Electronics")
        self.cart = Cart.objects.create(user=self.user)

        self.laptop = Laptop.objects.create(
            name="HP Pavilion",
            price=Decimal('60000'),
            ram=8,
            storage=256,
            processor_name="Ryzen 5",
            processor_brand="AMD",
            processor_generation="5th Gen",
            display="14 inch",
            operating_system="Ubuntu",
            battery=5.0,
            graphic_processor="AMD Radeon",
            touch_screen="No",
            screen_size="14",
            screen_resolution="1920x1080",
            category=self.category
        )

        CartItem.objects.create(cart=self.cart, laptop=self.laptop, quantity=1)

        self.payment = Payment.objects.create(
            user=self.user,
            razorpay_order_id="order_abc123",
            amount=60000,
            status="CREATED"
        )

    @patch("Checkout.views.razorpay.Client")
    def test_payment_handler_success(self, mock_client_class):
        mock_client = mock_client_class.return_value
        mock_client.utility.verify_payment_signature.return_value = True

        response = self.client.post(reverse("paymenthandler"), {
            "razorpay_order_id": "order_abc123",
            "razorpay_payment_id": "pay_success123",
            "razorpay_signature": "valid_signature"
        })

        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, "PAID")
        self.assertTemplateUsed(response, "order-success-page.html")

        orders = Order.objects.filter(customer=self.user)
        self.assertEqual(orders.count(), 1)
        self.assertEqual(orders.first().laptop.name, "HP Pavilion")

        # Cart should be empty
        self.assertFalse(CartItem.objects.filter(cart=self.cart).exists())

    @patch("Checkout.views.razorpay.Client")
    def test_payment_handler_signature_failure(self, mock_client_class):
        from razorpay.errors import SignatureVerificationError

        mock_client = mock_client_class.return_value
        mock_client.utility.verify_payment_signature.side_effect = SignatureVerificationError("Invalid Signature", {})

        response = self.client.post(reverse("paymenthandler"), {
            "razorpay_order_id": "order_abc123",
            "razorpay_payment_id": "pay_fail123",
            "razorpay_signature": "bad_signature"
        })

        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, "FAILED")
        self.assertTemplateUsed(response, "order-failure-page.html")

        # No orders should be created
        self.assertFalse(Order.objects.filter(customer=self.user).exists())

        # Cart should still have item
        self.assertTrue(CartItem.objects.filter(cart=self.cart).exists())
