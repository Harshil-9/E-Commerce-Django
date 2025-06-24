from django.urls import path
from .views import (
    AjaxSearchView, ProductbyProcessor,
    ProductbyPrice, ProductbyBrand, ProfileView
)

urlpatterns = [

    path('profile/', ProfileView.as_view(), name='profile'),
    

    # search
    path('ajax/search/', AjaxSearchView.as_view(), name='ajax_search'),

    # filters 
    path('products/processor/<str:processor>/', ProductbyProcessor.as_view(), name='products_by_processor'),
    path('products/price/<int:min_price>/<int:max_price>/', ProductbyPrice.as_view(), name='products_by_price'),
    path('products/brand/<str:brand>/', ProductbyBrand.as_view(), name='products_by_brand'),

]



