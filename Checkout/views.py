from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView
from django.conf import settings
from Products.models import Cart, CartItem, Order
from .models import Payment
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
import razorpay
from django.http import HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


# Create your views here.

class Paymentsuccess(TemplateView):
    template_name = "order-success-page.html"

class Paymentfailure(TemplateView):
    template_name = "order-failure-page.html"


class CheckoutView(LoginRequiredMixin, View):
    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_items = CartItem.objects.select_related('laptop').filter(cart=cart)

        cart_data = []
        total_price = 0.0

        for item in cart_items:
            unit_price = float(str(item.laptop.price).replace(',', '').strip())
            total = unit_price * item.quantity
            total_price += total

            cart_data.append({
                'name': item.laptop.name,
                'quantity': item.quantity,
                'total_price': "{:,.2f}".format(total)
            })

        # Razorpay Order Creation
        amount_paise = int(total_price * 100)

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        order = client.order.create({
            "amount": amount_paise,
            "currency": "INR",
            "payment_capture": 1
        })

        # Save order in DB
        Payment.objects.create(
            user=request.user,
            razorpay_order_id=order['id'],
            amount=amount_paise
        )

        context = {
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'order_id': order['id'],
            'amount': amount_paise,
            'display_amount': total_price,
            'callback_url': reverse('paymenthandler'),
            'cart_items': cart_data,
            'user': request.user
        }

        return render(request, 'checkout.html', context)

@method_decorator(csrf_exempt, name='dispatch')
class PaymentHandlerView(View):
    def post(self, request):
        payment = None
        try:
            payment_id = request.POST.get('razorpay_payment_id')
            order_id = request.POST.get('razorpay_order_id')
            signature = request.POST.get('razorpay_signature')

            payment = Payment.objects.get(razorpay_order_id=order_id)
            payment.razorpay_payment_id = payment_id
            payment.razorpay_signature = signature

            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            client.utility.verify_payment_signature({
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature
            })

            payment.status = "PAID"
            payment.save()

            # Create Order(s) for each cart item
            cart = Cart.objects.get(user=payment.user)   
            cart_items = CartItem.objects.select_related('laptop').filter(cart=cart)
            created_orders = []
            for item in cart_items:
                order = Order.objects.create(
                    laptop=item.laptop,
                    customer=payment.user,  
                    quantity=item.quantity,
                    price=item.laptop.price * item.quantity,
                    address="",  
                    phone="",
                    status=True
                )

                created_orders.append(order)

            # Clear cart after successful payment
            cart_items.delete()

            return render(request, 'order-success-page.html', {'payment': payment, 'orders': created_orders})

        except razorpay.errors.SignatureVerificationError:
            if payment:
                payment.status = "FAILED"
                payment.save()
            return render(request, 'order-failure-page.html', {'payment': payment})

        except Exception as e:
            return HttpResponseBadRequest(str(e))