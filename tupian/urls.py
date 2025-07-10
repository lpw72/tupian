from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/files/', include('files.urls')),
    path('api/categories/', include('categories.urls')),
    path('api/roles/', include('roles.urls')),
    path('api/permissions/', include('permissions.urls')),
]