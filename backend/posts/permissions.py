from rest_framework import permissions


class IsAuthorOrAdmin(permissions.BasePermission):
    """
    Allow safe methods for anyone.
    For unsafe methods, allow only the author or staff users.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and (
            getattr(obj, 'author', None) == request.user or request.user.is_staff
        )
