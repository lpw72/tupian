from rest_framework import serializers
from .models import CustomUser
from roles.models import Role  # Add this import

class UserSerializer(serializers.ModelSerializer):
    role = serializers.SlugRelatedField(slug_field='name', queryset=Role.objects.all(), required=False)
    permission_count = serializers.SerializerMethodField()  # 新增权限数量字段

    class Meta:
        model = CustomUser
        fields = ['id', 'username',  'password','phone_number', 'email', 'role', 'permission_count']  # 包含权限数量字段


    def get_permission_count(self, obj):
        # 通过用户角色计算权限数量
        if obj.role:
            return obj.role.permissions.count()
        return 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance is not None:
            self.fields['password'].required = False
            self.fields['username'].required = False
            self.fields['email'].required = False
            self.fields['phone_number'].required = False

    def create(self, validated_data):
        user = CustomUser(
            username=validated_data['username'],
            email=validated_data['email'],
            phone_number=validated_data['phone_number']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        # Handle password hashing for updates
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)

# 个人信息的序列化器
class UserListSerializer(serializers.ModelSerializer):
    role = serializers.StringRelatedField()
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'phone_number', 'role', 'permissions']

    def get_permissions(self, obj):
        if obj.role:
            return obj.role.permissions.values_list('code', flat=True)
        return []

# 新增角色更新序列化器
class UserRoleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['role']

# 添加密码修改序列化器
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_new_password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        # 验证新密码和确认密码是否一致
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError({"confirm_new_password": "新密码和确认密码不一致"})
        return data

    def validate_old_password(self, value):
        # 验证原密码是否正确
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("原密码不正确")
        return value

# 用基本信息的序列化器
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone_number']
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True}
        }

    def validate_email(self, value):
        # 排除当前用户进行邮箱唯一性验证
        instance = self.instance
        if CustomUser.objects.filter(email=value).exclude(pk=instance.pk).exists():
            raise serializers.ValidationError("该邮箱已被其他用户使用")
        return value

    def validate_username(self, value):
        # 排除当前用户进行用户名唯一性验证
        instance = self.instance
        if CustomUser.objects.filter(username=value).exclude(pk=instance.pk).exists():
            raise serializers.ValidationError("该用户名已被其他用户使用")
        return value