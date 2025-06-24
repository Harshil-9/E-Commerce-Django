from django.contrib.auth import login, logout
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.views import View
from Products.models import CartItem, Laptop
from .forms import RegisterForms, LoginForm
from django.views.generic.edit import FormView

class CustomHomeView(View):
    template_name = 'index.html'

    def get(self,request):
        laptops = Laptop.get_all_products()
        return render(request, "index.html", {'laptops': laptops})

    def post(self, request, pk):
        item = get_object_or_404(CartItem, laptop__id=pk, cart__user=request.user)
        action = request.POST.get('action')
        if action == 'increment':
            item.quantity += 1
        elif action == 'decrement' and item.quantity > 1:
            item.quantity -= 1
        item.save()
        return redirect('cart')

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