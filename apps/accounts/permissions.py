from rest_framework.permissions import BasePermission


class IsAdminUserRole(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == "ADMIN"


class IsCustomerRole(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == "USER"
