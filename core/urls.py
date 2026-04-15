"""
Main URL configuration for SmartEcoSystem.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Import patterns from admin_panel api file specifically 
# for legacy support if needed
from admin_panel.api.urls import auth_urlpatterns

urlpatterns = [
    # Django Admin Panel
    path('django-admin/', admin.site.urls),

    # API Endpoints (Unified v1)
    path('api/v1/auth/', include((auth_urlpatterns, 'auth'))),
    path('api/v1/admin/', include('admin_panel.api.urls')),
    path('api/v1/staff/', include('staff.api.urls')),
    path('api/v1/investor/', include('investor.api.urls')),

    # Role-based App Frontend Pages
    path('admin/', include('admin_panel.urls')),
    path('staff/', include('staff.urls')),
    path('investor/', include('investor.urls')),

    # Root Pages (Login, etc.)
    path('', include('api.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
