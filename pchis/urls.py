from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path('', include('accounts.urls')),

    path('admin/', admin.site.urls),
    path('dashboard/', include('dashboard.urls')),
    path('records/', include('records.urls')),
    path('appointments/', include('appointments.urls')),
    path('patients/', include('patients.urls')),
    path('messaging/', include('messaging.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)