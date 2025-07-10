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

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # 替换category_name为API要求的category字段
        representation['category'] = representation.pop('category_name')
        return representation
