from rest_framework import viewsets, permissions
from .models import Role
from .serializers import RoleSerializer
# viewsets：Django REST framework提供的视图集基类，用于简化视图的编写。
# permissions：用于处理权限检查的模块。
# Role：这是一个模型（Model），定义了角色的数据库结构和行为。
# RoleSerializer：这是一个序列化器（Serializer），用于将Role模型实例转换为JSON等格式的数据，反之亦然。
class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]  # 添加认证权限
