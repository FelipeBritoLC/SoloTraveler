from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from .models import Atividade, Viagem


class RegistroForm(UserCreationForm):
    """Formulário simples de criação de conta (RF01)."""
    email = forms.EmailField(required=True, label=_("e-mail"))

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class ViagemForm(forms.ModelForm):
    class Meta:
        model = Viagem
        fields = ["titulo", "destino", "data_inicio", "data_fim", "publica", "foto"]
        widgets = {
            "data_inicio": forms.DateInput(attrs={"type": "date"}),
            "data_fim": forms.DateInput(attrs={"type": "date"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        inicio = cleaned_data.get("data_inicio")
        fim = cleaned_data.get("data_fim")
        if inicio and fim and fim < inicio:
            raise forms.ValidationError(
                _("A data de fim não pode ser anterior à data de início.")
            )
        return cleaned_data


class AtividadeForm(forms.ModelForm):
    class Meta:
        model = Atividade
        fields = ["nome", "categoria", "data_hora", "custo_estimado", "descricao"]
        widgets = {
            "data_hora": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, viagem=None, **kwargs):
        # A viagem é passada pela view para validarmos o período (RF10)
        self.viagem = viagem
        super().__init__(*args, **kwargs)

    def clean_data_hora(self):
        data_hora = self.cleaned_data["data_hora"]
        if self.viagem:
            data_atividade = data_hora.date()
            if data_atividade < self.viagem.data_inicio or data_atividade > self.viagem.data_fim:
                raise forms.ValidationError(
                    _("A data da atividade deve estar dentro do período da viagem (%(inicio)s a %(fim)s).")
                    % {"inicio": self.viagem.data_inicio, "fim": self.viagem.data_fim}
                )
        return data_hora
