from rest_framework.views import APIView  # 导入APIView类，用于创建自定义的API视图
from rest_framework.response import Response  # 导入Response类，用于构建HTTP响应
from rest_framework import status, permissions  # 导入状态码和权限类
from rest_framework_simplejwt.views import TokenBlacklistView  # 导入JWT令牌黑名单视图
from .serializers import UserSerializer, UserListSerializer, UserRoleUpdateSerializer, UserUpdateSerializer, \
    ChangePasswordSerializer  # 导入序列化器类
from .models import CustomUser  # 导入CustomUser模型
from django.http import Http404  # 导入Http404异常类
from permissions.permissions import CanDeleteUser  # 导入自定义权限类CanDeleteUser
from roles.models import Role  # 导入Role模型
from rest_framework.generics import RetrieveUpdateAPIView  # 导入RetrieveUpdateAPIView类
from rest_framework.permissions import IsAuthenticated, AllowAny  # 导入IsAuthenticated和AllowAny权限类
from rest_framework_simplejwt.tokens import RefreshToken  # 导入RefreshToken类


class RegisterView(APIView):  # 定义注册视图类RegisterView，继承自APIView
    permission_classes = [AllowAny]  # 设置权限类为AllowAny，允许任何人访问

    def post(self, request):  # 定义POST方法处理用户注册请求
        serializer = UserSerializer(data=request.data)  # 使用UserSerializer验证请求数据
        if serializer.is_valid():  # 检查序列化器是否有效
            try:
                regular_role = Role.objects.get(name='普通用户')  # 获取名为“普通用户”的角色对象
                user = serializer.save()  # 保存新的用户对象
                user.role = regular_role  # 将用户的角色设置为“普通用户”
                user.save()  # 保存更新后的用户对象
                return Response(serializer.data, status=status.HTTP_201_CREATED)  # 返回成功的响应，状态码201
            except Role.DoesNotExist:  # 如果角色不存在，则捕获DoesNotExist异常
                return Response({'error': '普通用户角色不存在'}, status=status.HTTP_400_BAD_REQUEST)  # 返回错误响应，状态码400
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # 如果序列化器无效，返回错误信息，状态码400


class LoginView(APIView):  # 定义登录视图类LoginView，继承自APIView
    permission_classes = [AllowAny]  # 设置权限类为AllowAny，允许任何人访问

    def post(self, request):  # 定义POST方法处理用户登录请求
        username = request.data.get('username')  # 从请求数据中获取用户名
        password = request.data.get('password')  # 从请求数据中获取密码
        try:
            user = CustomUser.objects.get(username=username)  # 根据用户名查找用户对象
        except CustomUser.DoesNotExist:  # 如果用户不存在，则捕获DoesNotExist异常
            return Response({'error': 'Invalid credentials'}, status=400)  # 返回错误响应，状态码400

        if not user.check_password(password):  # 检查用户密码是否正确
            return Response({'error': 'Invalid credentials'}, status=400)  # 如果密码不正确，返回错误响应，状态码400

        refresh = RefreshToken.for_user(user)  # 生成刷新令牌
        response_data = {
            'refresh': str(refresh),  # 刷新令牌字符串
            'access': str(refresh.access_token),  # 访问令牌字符串
        }
        return Response(response_data)  # 返回包含令牌的响应


class LogoutView(TokenBlacklistView):  # 定义注销视图类LogoutView，继承自TokenBlacklistView
    permission_classes = [permissions.IsAuthenticated]  # 设置权限类为IsAuthenticated，只有认证用户才能访问


class UserListView(APIView):  # 定义用户列表视图类UserListView，继承自APIView
    permission_classes = [CanDeleteUser]  # 设置权限类为CanDeleteUser，只有有删除用户权限的用户才能访问

    def get(self, request):  # 定义GET方法处理获取用户列表请求
        users = CustomUser.objects.all()  # 获取所有用户对象
        serializer = UserListSerializer(users, many=True)  # 使用UserListSerializer序列化用户对象列表
        return Response(serializer.data)  # 返回序列化后的用户列表数据


class UserDetailView(APIView):  # 定义用户详情视图类UserDetailView，继承自APIView
    permission_classes = [permissions.IsAuthenticated]  # 设置权限类为IsAuthenticated，只有认证用户才能访问

    def get_object(self, pk):  # 定义get_object方法根据主键获取用户对象
        try:
            return CustomUser.objects.get(pk=pk)  # 根据主键查找用户对象
        except CustomUser.DoesNotExist:  # 如果用户不存在，则捕获DoesNotExist异常
            raise Http404  # 抛出Http404异常

    def put(self, request, pk):  # 定义PUT方法处理更新用户信息请求
        user = self.get_object(pk)  # 获取用户对象
        # Use UserSerializer instead of UserRoleUpdateSerializer  # 注释：使用UserSerializer代替UserRoleUpdateSerializer
        serializer = UserSerializer(user, data=request.data)  # 使用UserSerializer验证请求数据
        if serializer.is_valid():  # 检查序列化器是否有效
            serializer.save()  # 保存更新后的用户对象
            return Response(UserListSerializer(user).data)  # 返回序列化后的用户数据
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # 如果序列化器无效，返回错误信息，状态码400

    def delete(self, request, pk):  # 定义DELETE方法处理删除用户请求
        user = self.get_object(pk)  # 获取用户对象
        user.delete()  # 删除用户对象
        return Response(status=status.HTTP_204_NO_CONTENT)  # 返回无内容响应，状态码204


# 添加以下新视图
class UserProfileView(RetrieveUpdateAPIView):  # 定义用户个人资料视图类UserProfileView，继承自RetrieveUpdateAPIView
    permission_classes = [IsAuthenticated]  # 设置权限类为IsAuthenticated，只有认证用户才能访问
    http_method_names = ['get', 'put', 'patch']  # 允许的HTTP方法为GET、PUT和PATCH

    def get_object(self):  # 定义get_object方法获取当前用户对象
        return self.request.user  # 返回请求中的用户对象

    def get_serializer_class(self):  # 定义get_serializer_class方法根据请求方法选择合适的序列化器
        if self.request.method in ['PUT', 'PATCH']:  # 如果请求方法是PUT或PATCH
            return UserUpdateSerializer  # 返回UserUpdateSerializer
        return UserSerializer  # 否则返回UserSerializer


# 添加密码修改视图
class ChangePasswordView(APIView):  # 定义密码修改视图类ChangePasswordView，继承自APIView
    permission_classes = [permissions.IsAuthenticated]  # 设置权限类为IsAuthenticated，只有认证用户才能访问

    def post(self, request):  # 定义POST方法处理密码修改请求
        serializer = ChangePasswordSerializer(data=request.data,
                                              context={'request': request})  # 使用ChangePasswordSerializer验证请求数据
        if serializer.is_valid():  # 检查序列化器是否有效
            # 更新用户密码  # 注释：更新用户密码
            user = request.user  # 获取请求中的用户对象
            user.set_password(serializer.validated_data['new_password'])  # 设置新密码
            user.save()  # 保存更新后的用户对象
            return Response({"message": "密码修改成功"}, status=status.HTTP_200_OK)  # 返回成功的响应，状态码200
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # 如果序列化器无效，返回错误信息，状态码400


