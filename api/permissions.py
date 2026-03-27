"""
Custom permission classes for SmartEcoSystem.
Role-based access control: Admin, Staff, Investor.
"""

from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """Allows access only to users with role='admin'."""
    message = "Access restricted to Administrators only."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'admin'
        )


class IsStaffRole(BasePermission):
    """Allows access only to users with role='staff'."""
    message = "Access restricted to Staff members only."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'staff'
        )


class IsInvestorRole(BasePermission):
    """Allows access only to users with role='investor'."""
    message = "Access restricted to Investors only."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'investor'
        )


class IsAdminOrStaff(BasePermission):
    """Allows access to both Admin and Staff users."""
    message = "Access restricted to Admin or Staff members."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role in ('admin', 'staff')
        )


class IsOwnerOrAdmin(BasePermission):
    """Object-level: only owner or admin can modify."""
    message = "You do not have permission to access this resource."

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.user.role == 'admin':
            return True
        # Check if object has submitted_by, staff, investor, or sender field
        owner_field = getattr(obj, 'submitted_by', None) or \
                      getattr(obj, 'staff', None) or \
                      getattr(obj, 'investor', None) or \
                      getattr(obj, 'sender', None) or \
                      getattr(obj, 'assigned_to', None)
        return owner_field == request.user
