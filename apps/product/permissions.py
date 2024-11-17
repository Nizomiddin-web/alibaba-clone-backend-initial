from rest_framework.permissions import BasePermission


class IsProductOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner==request.user

class HasCategoryPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.groups.all().exists():
            return False
        return request.user.groups.first().name=='buyer'