from rest_framework.exceptions import PermissionDenied


class BaseCheckGroupMixin:
    """
    Base mixin for checking group permissions.
    """

    required_group_names = []

    def check_permissions(self, request):
        if not request.user.groups.filter(name__in=self.required_group_names).exists():
            raise PermissionDenied()


class CheckSupplierSaleManagerGroupMixin(BaseCheckGroupMixin):
    """
    Check if the user belongs to groups with supplier sale manager permissions.
    """

    required_group_names = ["Supplier Order Manager", "Supplier Admin"]


class CheckSaleManagerGroupMixin(BaseCheckGroupMixin):
    """
    Check if the user belongs to groups with sale manager permissions.
    """

    required_group_names = [
        "Buyer Order Manager",
        "Buyer Admin",
        "Supplier Admin",
        "Supplier Sale Manager",
    ]


class CheckProductManagerGroupMixin(BaseCheckGroupMixin):
    """
    Check if the user belongs to groups with product manager permissions.
    """

    required_group_names = ["Buyer Product Manager", "Buyer Admin"]
