from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from functools import wraps

def role_required(roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            if getattr(request.user, 'rol', None) not in roles:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator