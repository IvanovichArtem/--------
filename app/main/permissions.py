from rest_framework import permissions

class IsCustomerAndAuthenticated(permissions.BasePermission):
    """
    Custom permission to only allow customers to access the view.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'customer'

class IsEmployeeAndAuthenticated(permissions.BasePermission):
    """
    Employee permission to only allow employee to access the view.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'employee'