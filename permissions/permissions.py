from rest_framework import permissions

class CanDeleteUser(permissions.BasePermission):
    """允许拥有删除用户权限的用户访问"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated or not request.user.role:
            return False
        # 检查用户角色是否有delete_user权限
        return request.user.role.permissions.filter(code='delete_user').exists()