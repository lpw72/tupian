from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True)
    role = models.ForeignKey('roles.Role', on_delete=models.SET_NULL, null=True, blank=True)  # 新增角色关联
    
    # 显式定义groups和user_permissions字段并设置唯一related_name
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        related_name='custom_user_groups',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name='custom_user_permissions',
        related_query_name='custom_user',
    )

    def __str__(self):
        return self.username