from __future__ import annotations

from django.contrib.auth.models import Group


def ensure_role_groups() -> tuple[Group, Group]:
    admin_group, _ = Group.objects.get_or_create(name='admin')
    analista_group, _ = Group.objects.get_or_create(name='analista')
    return admin_group, analista_group


def sync_user_group(user) -> None:
    """Sincroniza el Group Django con el campo Usuario.rol.

    No cambia el modelo; solo usa auth.Group para permisos/roles.
    """
    admin_group, analista_group = ensure_role_groups()

    # limpiar solo estos dos grupos para no interferir otros permisos
    user.groups.remove(admin_group, analista_group)

    if getattr(user, 'rol', None) == 'admin':
        user.groups.add(admin_group)
    else:
        user.groups.add(analista_group)
