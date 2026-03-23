from rest_framework import permissions


class IsSeller(permissions.BasePermission):
    """Allow access only to approved sellers."""
    message = 'Only approved sellers can perform this action.'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == 'seller' and
            hasattr(request.user, 'seller_profile') and
            request.user.seller_profile.is_approved
        )


class IsSellerPending(permissions.BasePermission):
    """Allow any seller (even unapproved) — for profile setup."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'seller'


class IsOwnerOrAdmin(permissions.BasePermission):
    """Object-level permission: owner or admin only."""
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'buyer'):
            return obj.buyer == request.user
        return False


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'
