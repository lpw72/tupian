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


class FileViewSet(viewsets.ModelViewSet):
    serializer_class = FileSerializer  # 设置序列化器类为FileSerializer
    # 移除全局认证要求，允许所有用户访问
    permission_classes = [permissions.AllowAny]  # 修改此行

    def get_queryset(self):
        queryset = File.objects.all()  # 获取所有文件对象的查询集
        # 删除用户认证和权限过滤相关代码
        # 搜索功能
        search = self.request.query_params.get('search', None)  # 获取查询参数中的'search'值
        if search:
            queryset = queryset.filter(
                Q(description__icontains=search) |  # 过滤description字段包含搜索关键词的文件
                Q(category__name__icontains=search)  # 或者过滤category名称包含搜索关键词的文件
            )
        return queryset  # 返回处理后的查询集

    # 保留其他方法但确保不影响匿名访问
    def get_permissions(self):
        # 移除原有的权限判断，所有操作都使用全局的AllowAny权限
        return super().get_permissions()

    def perform_create(self, serializer):
        # 保存文件并关联当前用户
        serializer.save(user=self.request.user)  # 在保存文件时将user字段设置为当前请求的用户

        # 普通用户上传文件后升级为UP主
        if self.request.user.role and self.request.user.role.name == '普通用户':  # 检查用户角色是否为普通用户
            up_role = Role.objects.get(name='UP主')  # 获取名为'UP主'的角色对象
            self.request.user.role = up_role  # 将用户角色更新为UP主
            self.request.user.save()  # 保存用户对象以应用更改

    def perform_destroy(self, instance):
        # 从七牛云删除文件
        # 提取URL中的key
        key = instance.url.replace(f'http://{settings.QINIU_DOMAIN}/', '')  # 从文件URL中提取出存储在七牛云上的key
        delete_qiniu_file(key)  # 调用delete_qiniu_file函数删除七牛云上的文件
        # 删除数据库记录
        instance.delete()  # 删除数据库中的文件记录

    @action(detail=False, methods=['get'], url_path='upload-token')
    def upload_token(self, request):
        """获取七牛云上传凭证"""
        filename = request.query_params.get('filename')  # 获取查询参数中的'filename'值
        category_id = request.query_params.get('category')  # 获取查询参数中的'category'值

        if not filename:
            return Response({'error': 'filename is required'},
                            status=status.HTTP_400_BAD_REQUEST)  # 如果没有提供filename，则返回错误响应

        # 获取类别名称 - 将默认值从'未分类'改为None
        category_name = None  # 初始化category_name为None
        if category_id:
            try:
                category = Category.objects.get(id=category_id)  # 根据category_id获取对应的Category对象
                category_name = category.name  # 将category对象的name属性赋值给category_name
            except Category.DoesNotExist:
                pass  # 如果找不到对应的Category对象，则忽略异常

        token, key = generate_upload_token(filename, category_name)  # 调用generate_upload_token生成上传token和key
        return Response({
            'upload_token': token,  # 返回上传token
            'upload_url': settings.QINIU_UPLOAD_URL,  # 返回七牛云上传URL
            'filename': filename,  # 返回文件名
            'key': key  # 返回文件key，确保前端使用此key作为上传参数
        })

    @action(detail=False, methods=['post'], url_path='save-file-info')
    def save_file_info(self, request):
        """保存文件信息到数据库"""
        key = request.data.get('key')  # 从前端请求数据中获取'key'值
        category_id = request.data.get('category')  # 从前端请求数据中获取'category'值
        description = request.data.get('description', key)  # 从前端请求数据中获取'description'值，默认为key

        if not key or not category_id:
            return Response({
                'error': 'key and category are required'
            }, status=status.HTTP_400_BAD_REQUEST)  # 如果没有提供key或category，则返回错误响应

        try:
            category = Category.objects.get(id=category_id)  # 根据category_id获取对应的Category对象
            file_url = get_file_url(key)  # 根据key生成文件URL
            file = File.objects.create(
                user=request.user,  # 文件所属用户为当前请求的用户
                description=description,  # 文件描述为description
                category=category,  # 文件类别为category
                url=file_url  # 文件URL为file_url
            )

            # 添加角色升级逻辑
            if request.user.role and request.user.role.name == '普通用户':  # 检查用户角色是否为普通用户
                up_role = Role.objects.get(name='UP主')  # 获取名为'UP主'的角色对象
                request.user.role = up_role  # 将用户角色更新为UP主
                request.user.save()  # 保存用户对象以应用更改

            return Response(FileSerializer(file).data, status=status.HTTP_201_CREATED)  # 返回新创建文件的序列化数据
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'},
                            status=status.HTTP_400_BAD_REQUEST)  # 如果找不到对应的Category对象，则返回错误响应


