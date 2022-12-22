from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if (request.user.is_authenticated):
            return (
                request.user.is_admin
                or request.user.is_staff
            )
        return False

    def has_object_permission(self, request, view, obj):
        if (request.user.is_authenticated):
            return (
                request.user.is_admin
                or request.user.is_staff
            )
        return False


class IsAuthorOrAdminOrModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
                request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if (request.user.is_authenticated or request.method in permissions.SAFE_METHODS):
            return (
                obj.author == request.user
                or request.user.is_moderator
                or request.user.is_admin
            )
