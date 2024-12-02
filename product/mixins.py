from rest_framework.exceptions import PermissionDenied


class CheckGroupPermissionsMixin:
    allowed_group_names = []

    def check_permissions(self, request):
        if not request.method == "GET":
            user_groups = request.user.groups.values_list("name", flat=True)
            if not any(group_name in user_groups for group_name in self.allowed_group_names):
                raise PermissionDenied()


class CheckSupplierAdminGroupMixin(CheckGroupPermissionsMixin):
    allowed_group_names = ["Supplier Admin"]


class CheckProductManagerGroupMixin(CheckGroupPermissionsMixin):
    allowed_group_names = ["Supplier Admin", "Supplier Product Manager"]
