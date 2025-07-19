from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('health.urls')),
    path('accounts/', include('django.contrib.auth.urls')),  # login/logout
]
