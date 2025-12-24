from __future__ import annotations

from functools import wraps

from django.core.exceptions import PermissionDenied


def role_required(roles=None):
    if roles is None:
        roles = []

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied

            if getattr(request.user, "is_superuser", False):
                return view_func(request, *args, **kwargs)

            if getattr(request.user, "rol", None) not in roles:
                raise PermissionDenied

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
