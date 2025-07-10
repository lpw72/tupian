from rest_framework import viewsets, permissions
from .models import Permission
from .serializers import PermissionSerializer

class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated]  # 添加认证权限
