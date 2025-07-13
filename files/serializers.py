from rest_framework import serializers
from .models import File
from categories.models import Category

class FileSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()
    user = serializers.ReadOnlyField(source='user.username')
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        write_only=True
    )

    class Meta:
        model = File
        fields = ('id', 'description', 'category', 'category_name', 'url', 'user')
        read_only_fields = ('id', 'url', 'user')

    def get_category_name(self, obj):
        return obj.category.name if obj.category else None
#它首先检查obj是否有category属性。如果存在，它将返回category属性的name属性；
# 如果不存在（即obj.category为None或False），则整个表达式返回None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # 替换category_name为API要求的category字段
        representation['category'] = representation.pop('category_name')
        return representation
#它可能被用来将数据库模型实例转换为API可以使用的格式。
# 举例来说，如果有一个博客文章的模型，其中有一个字段叫做category_name，API可能需要这个字段被命名为category。
# 在这个例子中，to_representation方法就会将category_name字段重命名为category，以符合API的规范。