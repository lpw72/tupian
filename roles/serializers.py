from rest_framework import serializers
from .models import Role
from permissions.models import Permission

class RoleSerializer(serializers.ModelSerializer):
    # 读取时返回权限ID列表，写入时接受权限ID列表
    permissions = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Permission.objects.all(),
        write_only=False
    )

    class Meta:
        model = Role
        fields = ['id', 'name', 'permissions']

    # 自定义返回格式，确保返回权限ID列表
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['permissions'] = [perm.id for perm in instance.permissions.all()]
        return representation