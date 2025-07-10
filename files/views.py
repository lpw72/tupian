from django.conf import settings
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import File
from .serializers import FileSerializer
from .utils import generate_upload_token, delete_qiniu_file, get_file_url
from categories.models import Category
from roles.models import Role
from permissions.permissions import CanDeleteUser

class FileViewSet(viewsets.ModelViewSet):
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = File.objects.all()
        # 管理员查看所有文件，其他用户查看自己的文件
        if not (self.request.user.role and self.request.user.role.name == '管理员'):
            queryset = queryset.filter(user=self.request.user)

        # 搜索功能
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(description__icontains=search) | 
                Q(category__name__icontains=search)
            )
        return queryset

    def perform_create(self, serializer):
        # 保存文件并关联当前用户
        serializer.save(user=self.request.user)

        # 普通用户上传文件后升级为UP主
        if self.request.user.role and self.request.user.role.name == '普通用户':
            up_role = Role.objects.get(name='UP主')
            self.request.user.role = up_role
            self.request.user.save()

    def perform_destroy(self, instance):
        # 从七牛云删除文件
        # 提取URL中的key
        key = instance.url.replace(f'http://{settings.QINIU_DOMAIN}/', '')
        delete_qiniu_file(key)
        # 删除数据库记录
        instance.delete()

    @action(detail=False, methods=['get'])
    def upload_token(self, request):
        """获取七牛云上传凭证"""
        filename = request.query_params.get('filename')
        category_id = request.query_params.get('category')

        if not filename:
            return Response({'error': 'filename is required'}, status=status.HTTP_400_BAD_REQUEST)

        # 获取类别名称
        category_name = '未分类'
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
                category_name = category.name
            except Category.DoesNotExist:
                pass

        token, key = generate_upload_token(filename, category_name)
        return Response({
            'upload_token': token,
            'upload_url': settings.QINIU_UPLOAD_URL,
            'filename': filename  # 修改为返回原始文件名而非带路径的key
        })

    @action(detail=False, methods=['post'])
    def save_file_info(self, request):
        """保存文件信息到数据库"""
        key = request.data.get('key')
        category_id = request.data.get('category')
        description = request.data.get('description', key)
        hash_value = request.data.get('hash')  # 获取hash参数
    
        if not key or not category_id or not hash_value:  # 增加hash验证
            return Response({
                'error': 'key, category and hash are required'
            }, status=status.HTTP_400_BAD_REQUEST)
    
        try:
            category = Category.objects.get(id=category_id)
            file_url = get_file_url(key)
            file = File.objects.create(
                user=request.user,
                description=description,
                category=category,
                url=file_url,
                hash=hash_value  # 保存hash值
            )
            return Response(FileSerializer(file).data, status=status.HTTP_201_CREATED)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, status=status.HTTP_400_BAD_REQUEST)

    def get_permissions(self):
        if self.action == 'list':
            return [CanDeleteUser()]
        return super().get_permissions()