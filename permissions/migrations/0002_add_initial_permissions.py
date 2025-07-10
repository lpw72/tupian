from django.db import migrations
from permissions.models import Permission

def add_initial_permissions(apps, schema_editor):
    permissions = [
        {'name': '查看文件权限', 'code': 'view_file'},
        {'name': '发布文件权限', 'code': 'publish_file'},
        {'name': '编辑自己文件权限', 'code': 'edit_own_file'},
        {'name': '删除自己文件权限', 'code': 'delete_own_file'},
        {'name': '删除任何文件权限', 'code': 'delete_any_file'},
        {'name': '管理角色权限', 'code': 'manage_role'},
        {'name': '删除用户权限', 'code': 'delete_user'}
    ]
    
    for perm_data in permissions:
        perm, created = Permission.objects.get_or_create(**perm_data)
        if created:
            print(f"Created permission: {perm.name}")  # 添加此行

def reverse_func(apps, schema_editor):
    Permission.objects.filter(code__in=[
        'view_file', 'publish_file', 'edit_own_file', 
        'delete_own_file', 'delete_any_file', 'manage_role', 'delete_user'
    ]).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('permissions', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_initial_permissions, reverse_func),
    ]