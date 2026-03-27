"""
Main URL configuration for SmartEcoSystem.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Import patterns from admin_panel api file specifically for legacy support if needed
from admin_panel.api.urls import auth_urlpatterns

urlpatterns = [
    # Django Admin Panel
    path('django-admin/', admin.site.urls),

    # Shared Auth API (namespaced)
    path('api/v1/auth/', include((auth_urlpatterns, 'auth'))),

    # Role-based Apps (Frontend + API)
    path('admin/', include('admin_panel.urls')),
    path('staff/', include('staff.urls')),
    path('investor/', include('investor.urls')),

    # Root Pages (Login, etc.)
    path('', include('api.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
