from django.core.exceptions import PermissionDenied

class AdminRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        if getattr(request.user, 'rol', None) != 'admin':
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

class RoleRequiredMixin:
    allowed_roles = []  # Lista de roles permitidos

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        if request.user.rol not in self.allowed_roles:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)