from django.contrib.auth import login, logout
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import DetailView, CreateView, DeleteView, TemplateView, UpdateView, ListView
from django.conf import settings
from .forms import RegisterForms, LoginForm
from django.views.generic.edit import FormView
from .models import Laptop, Cart, CartItem, Order, Payment, Review
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
import razorpay
from django.http import HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.template.loader import render_to_string
from .forms import ReviewForm
from e_app import models
from django.db.models import Avg

@method_decorator(login_required, name='dispatch')
class CartCountView(View):
    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        count = CartItem.objects.filter(cart=cart).count()
        return JsonResponse({'count': count})

class CustomHomeView(View):
    template_name = 'index.html'

    def get(self,request):
        laptops = Laptop.get_all_products()
        return render(request, "index.html", {'laptops': laptops})

class CustomLoginView(LoginView):
    authentication_form = LoginForm
    template_name = 'login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        self.request.session['user_id'] = self.request.user.id
        self.request.session['username'] = self.request.user.email
        return response

class CustomRegisterView(FormView):
    template_name = "register2.html"
    form_class = RegisterForms
    success_url = reverse_lazy("index") 

    def form_valid(self, form):
        user = form.save()
        if user:
            login(self.request, user)
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logout(request)
        return super().dispatch(request, *args, **kwargs)
    
class UserLogoutView(LogoutView):
    next_page = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
            request.session.pop('user_id', None)
            request.session.pop('username', None)
            return super().dispatch(request, *args, **kwargs)

# class ProductDetailView(DetailView):
#     model = Laptop
#     template_name = 'product_detail.html'
#     context_object_name = 'laptop'

class AllProductView(ListView):
    model = Laptop
    template_name = 'product.html'
    context_object_name = 'laptops'

class AddToCartView(LoginRequiredMixin, View):
    def post(self, request, pk):
        print("POST request received to add to cart")
        laptop = get_object_or_404(Laptop, pk=pk)
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, laptop=laptop)
        if not item_created:
            cart_item.quantity += 1
            cart_item.save()
        print(f"Item {'added' if item_created else 'updated'} in cart")
        return redirect('cart')

class CartView(ListView):
    model = CartItem
    template_name = 'cart.html'
    context_object_name = 'cart_items'

    def get_queryset(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return CartItem.objects.filter(cart=cart)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        context['cart'] = cart
        return context
    
class RemoveFromCart(View):
    def post(self, request, pk):
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item = CartItem.objects.filter(cart=cart, laptop_id=pk).first()
        if cart_item:
            cart_item.delete()
        return redirect('cart')

class CartItemUpdateView(View):
    def post(self, request, pk):
        item = get_object_or_404(CartItem, laptop__id=pk, cart__user=request.user)
        action = request.POST.get('action')
        if action == 'increment':
            item.quantity += 1
        elif action == 'decrement' and item.quantity > 1:
            item.quantity -= 1
        item.save()
        return redirect('cart')

class Paymentsuccess(TemplateView):
    template_name = "order-success-page.html"

class Paymentfailure(TemplateView):
    template_name = "order-failure-page.html"


class CheckoutView(LoginRequiredMixin, View):
    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)

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
            cart_items = CartItem.objects.filter(cart=cart)
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
    
class AjaxSearchView(View):
    def get(self, request):
        q = request.GET.get('q', '')
        result = []
        if q:
            laptops = Laptop.objects.filter(name__icontains=q)[:10]
            result = [
                {'id': l.id, 'name': l.name, 'price': l.price, 'image': l.product_image.url}
                for l in laptops
            ]
        return JsonResponse({'results': result})
    
class ProductbyProcessor(View):
    def get(self, request, processor):
        laptops = Laptop.objects.filter(processor_name__icontains=processor)
        return render(request, "products_by_processor.html", {
            'laptops': laptops,
            'processor': processor
        })
 
class ProductbyPrice(View):
    def get(self, request, min_price, max_price):
        laptops = Laptop.objects.filter(price__gte=min_price, price__lte=max_price)
        return render(request, "products_by_price.html", {
            'laptops': laptops,
            'min_price': min_price,
            'max_price': max_price
        })
    
class ProductbyBrand(View):
    def get(self, request, brand):
        laptops = Laptop.objects.filter(brand__icontains=brand)
        return render(request, "products_by_brand.html", {
            'laptops': laptops,
            'brand': brand
        })
    
class ProductDetailView(DetailView):
    model = Laptop
    template_name = 'product_detail.html'
    context_object_name = 'laptop'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        reviews = product.reviews.all()
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

        if self.request.user.is_authenticated:
            try:
                existing_review = Review.objects.get(product=product, user=self.request.user)
                form = ReviewForm(instance=existing_review)
            except Review.DoesNotExist:
                form = ReviewForm()
        else:
            form = None

        context['reviews'] = reviews
        context['form'] = form
        context['avg_rating'] = round(avg_rating, 1)
        return context

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        product = self.object
        try:
            review = Review.objects.get(product=product, user=request.user)
            form = ReviewForm(request.POST, instance=review)
        except Review.DoesNotExist:
            form = ReviewForm(request.POST)

        if form.is_valid():
            new_review = form.save(commit=False)
            new_review.product = product
            new_review.user = request.user
            new_review.save()
        return redirect('product_detail', pk=product.id)

@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        return render(request, 'profile.html', {'user': request.user})
