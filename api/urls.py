"""api/urls.py – Root frontend pages and shared API logic."""

from django.urls import path
from .views.frontend_views import (
    IndexView, LoginView, RegisterView, ForgotPasswordView, 
    ProfileView, LogoutView
)
from .views.business_views import BusinessListView

urlpatterns = [
    # API
    path('api/v1/auth/businesses/', BusinessListView.as_view(), name='api-businesses'),
    
    # Root Pages
    path('', IndexView.as_view(), name='index'),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
