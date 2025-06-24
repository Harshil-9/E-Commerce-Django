from django.shortcuts import redirect, get_object_or_404
from django.views.generic import DetailView, ListView
from .models import Laptop, Cart, CartItem, Review
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .forms import ReviewForm
from django.db.models import Avg

# Create your views here.


@method_decorator(login_required, name='dispatch')
class CartCountView(View):
    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        count = CartItem.objects.select_related('cart').filter(cart=cart).count()
        return JsonResponse({'count': count})
    
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
        return CartItem.objects.select_related('laptop').filter(cart=cart)

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


class ProductDetailView(DetailView):
    model = Laptop
    template_name = 'product_detail.html'
    context_object_name = 'laptop'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        reviews = product.reviews.select_related('user').all()
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