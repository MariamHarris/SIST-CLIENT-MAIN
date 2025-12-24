from __future__ import annotations

from django import forms

from .models import Cliente


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            "nombre",
            "apellido",
            "email",
            "telefono",
            "direccion",
            "estado",
            "nivel_riesgo",
        ]
        widgets = {
            "direccion": forms.Textarea(attrs={"rows": 2}),
        }
