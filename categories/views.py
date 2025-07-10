from rest_framework import viewsets
from rest_framework import permissions  # 添加此行导入权限模块
from .models import Category
from .serializers import CategorySerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]  # 现在可以正确引用permissions
    permission_classes = [permissions.IsAuthenticated]  # 添加认证权限