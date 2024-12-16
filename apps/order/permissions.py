from rest_framework.permissions import BasePermission

class CheckOrderUser(BasePermission):
    def has_permission(self, request, view):
         group = request.user.groups.first()
         return bool(request.user and request.user.is_authenticated and group and group.name=='buyer')


