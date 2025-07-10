from django.db import migrations
from permissions.models import Permission

def re_add_initial_permissions(apps, schema_editor):
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
        Permission.objects.get_or_create(**perm_data)

def reverse_func(apps, schema_editor):
    pass  # 不需要回滚操作

class Migration(migrations.Migration):
    dependencies = [
        ('permissions', '0003_add_initial_permissions'),
    ]

    operations = [
        migrations.RunPython(re_add_initial_permissions, reverse_func),
    ]