from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    CustomLoginView, CustomRegisterView, UserLogoutView, CustomHomeView
)

urlpatterns = [

    path('home/', CustomHomeView.as_view(), name='index'),

    path('', CustomLoginView.as_view(), name='login'),
    path('register/', CustomRegisterView.as_view(), name='register2'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('logout/', UserLogoutView.as_view(), name='homeproduct'),

    # Reset password 
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),

]