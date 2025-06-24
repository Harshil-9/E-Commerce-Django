from django.shortcuts import redirect, render, get_object_or_404
from Products.models import Laptop, CartItem
from django.views import View
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse



    
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
@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        return render(request, 'profile.html', {'user': request.user})
