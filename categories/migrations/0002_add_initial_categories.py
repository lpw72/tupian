from django.db import migrations
from categories.models import Category

def add_initial_categories(apps, schema_editor):
    # 定义初始类别数据
    categories = [
        {'name': '人物'},
        {'name': '风景'},
        {'name': '文字'},
        {'name': '其他'}
    ]
    
    # 批量创建类别（避免重复）
    for category_data in categories:
        Category.objects.get_or_create(**category_data)

def reverse_func(apps, schema_editor):
    # 迁移回滚时删除添加的类别
    Category.objects.filter(name__in=['人物', '风景', '文字', '其他']).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('categories', '0001_initial'),  # 确保依赖于初始迁移
    ]

    operations = [
        migrations.RunPython(add_initial_categories, reverse_func),
    ]