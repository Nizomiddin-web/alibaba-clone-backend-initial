from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsProductOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner==request.user

class HasCategoryPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.groups.all().exists():
            return False
        return request.user.groups.first().name=='buyer'


class HasProductPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return bool(
                    request.user.is_authenticated
                    and request.user.groups.first()
                    and request.user.groups.first().name=='seller'
               )

    def has_object_permission(self, request, view, obj):
        pass