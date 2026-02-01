from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """
    Only admin users
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.profile.role.name == "admin"
        )


class IsUserOrAdmin(BasePermission):
    """
    Normal users + admins
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated