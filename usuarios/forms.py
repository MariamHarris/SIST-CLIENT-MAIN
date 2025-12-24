from __future__ import annotations

import re

from django import forms
from django.core.exceptions import ValidationError

from .models import Usuario
from .utils import sync_user_group


class UsuarioForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        help_text="En creación es obligatorio. En edición, déjalo vacío para no cambiarlo.",
    )

    class Meta:
        model = Usuario
        fields = [
            'username',
            'email',
            'nombre_completo',
            'telefono',
            'rol',
            'is_active',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance is None or self.instance.pk is None:
            self.fields['password'].required = True

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip()
        if not email:
            raise ValidationError('El correo es obligatorio.')
        if Usuario.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise ValidationError('Este correo ya está en uso.')
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if self.fields['password'].required and not password:
            raise ValidationError('La contraseña es obligatoria.')
        if password:
            if len(password) < 8 or not re.search(r'[A-Z]', password) or not re.search(r'\d', password):
                raise ValidationError('La contraseña debe tener al menos 8 caracteres, una mayúscula y un número.')
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
            sync_user_group(user)
        return user