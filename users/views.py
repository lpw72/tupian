from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenBlacklistView
from .serializers import UserSerializer, UserListSerializer, UserRoleUpdateSerializer
from .models import CustomUser
from django.http import Http404
from rest_framework.permissions import IsAuthenticated
from permissions.permissions import CanDeleteUser
from roles.models import Role  # 添加此行导入Role模型
from .serializers import ChangePasswordSerializer
from rest_framework.generics import RetrieveUpdateAPIView
from .serializers import UserSerializer, UserUpdateSerializer, ChangePasswordSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            try:
                regular_role = Role.objects.get(name='普通用户')
                user = serializer.save()
                user.role = regular_role
                user.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Role.DoesNotExist:
                return Response({'error': '普通用户角色不存在'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=400)
        
        if not user.check_password(password):
            return Response({'error': 'Invalid credentials'}, status=400)
        
        refresh = RefreshToken.for_user(user)
        response_data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        return Response(response_data)

class LogoutView(TokenBlacklistView):
    permission_classes = [permissions.IsAuthenticated]

class UserListView(APIView):
    permission_classes = [CanDeleteUser]  # 修改此行

    def get(self, request):
        users = CustomUser.objects.all()
        serializer = UserListSerializer(users, many=True)
        return Response(serializer.data)

class UserDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            raise Http404

    def put(self, request, pk):
        user = self.get_object(pk)
        # Use UserSerializer instead of UserRoleUpdateSerializer
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(UserListSerializer(user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = self.get_object(pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# 添加以下新视图
class UserProfileView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'put', 'patch']

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer  # Now this reference will work
        return UserSerializer

# 添加密码修改视图
class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # 更新用户密码
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"message": "密码修改成功"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)