from django.db import migrations


def add_initial_roles(apps, schema_editor):
    Role = apps.get_model('roles', 'Role')
    Permission = apps.get_model('permissions', 'Permission')

    # 获取或创建权限对象（修改为get_or_create避免权限不存在时迁移失败）
    view_file, _ = Permission.objects.get_or_create(code='view_file', defaults={'name': '查看文件'})
    publish_file, _ = Permission.objects.get_or_create(code='publish_file', defaults={'name': '发布文件'})
    edit_own_file, _ = Permission.objects.get_or_create(code='edit_own_file', defaults={'name': '编辑自己文件'})
    delete_own_file, _ = Permission.objects.get_or_create(code='delete_own_file', defaults={'name': '删除自己文件'})
    delete_any_file, _ = Permission.objects.get_or_create(code='delete_any_file', defaults={'name': '删除任何文件'})
    manage_role, _ = Permission.objects.get_or_create(code='manage_role', defaults={'name': '管理角色'})
    delete_user, _ = Permission.objects.get_or_create(code='delete_user', defaults={'name': '删除用户'})

    # 创建普通用户角色
    regular_user, _ = Role.objects.get_or_create(name='普通用户')
    regular_user.permissions.set([view_file, publish_file])

    # 创建UP主角色
    up_user, _ = Role.objects.get_or_create(name='UP主')
    up_user.permissions.set([view_file, publish_file, edit_own_file, delete_own_file])

    # 创建管理员角色
    admin_user, _ = Role.objects.get_or_create(name='管理员')
    admin_user.permissions.set([view_file, publish_file, edit_own_file, delete_own_file, delete_any_file, manage_role, delete_user])

def reverse_func(apps, schema_editor):
    Role = apps.get_model('roles', 'Role')
    Role.objects.filter(name__in=['普通用户', 'UP主', '管理员']).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('roles', '0001_initial'),
        ('permissions', '0004_re_add_initial_permissions'),  # 确保权限已创建
    ]

    operations = [
        migrations.RunPython(add_initial_roles, reverse_func),
    ]