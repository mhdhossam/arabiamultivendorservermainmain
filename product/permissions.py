from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied

class IsVendor(BasePermission):
    """
    Allows access only to users who are vendors (i.e., have is_supplier=True).
    """

    def has_permission(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        
        if request.user.is_authenticated and request.user.is_supplier:
            return True
        
        raise PermissionDenied("You must be a vendor to post a product.")
