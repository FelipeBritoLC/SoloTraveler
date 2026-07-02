from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class Categoria(models.Model):
    """Categoria de atividades (ex: Museus, Trilhas, Restaurantes)."""
    nome = models.CharField(_("nome"), max_length=60, unique=True)

    class Meta:
        verbose_name = _("categoria")
        verbose_name_plural = _("categorias")
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Viagem(models.Model):
    """Uma viagem/roteiro criado por um usuário (RF04)."""
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="viagens",
        verbose_name=_("usuário"),
    )
    titulo = models.CharField(_("título"), max_length=120)
    destino = models.CharField(_("destino"), max_length=120)
    data_inicio = models.DateField(_("data de início"))
    data_fim = models.DateField(_("data de fim"))
    publica = models.BooleanField(_("pública"), default=False)
    foto = models.ImageField(_("foto de capa"), upload_to="viagens/%Y/%m/", blank=True, null=True)
    criada_em = models.DateTimeField(_("criada em"), auto_now_add=True)

    class Meta:
        verbose_name = _("viagem")
        verbose_name_plural = _("viagens")
        ordering = ["-criada_em"]

    def __str__(self):
        return f"{self.titulo} ({self.destino})"

    def clean(self):
        if self.data_inicio and self.data_fim and self.data_fim < self.data_inicio:
            raise ValidationError(
                {"data_fim": _("A data de fim não pode ser anterior à data de início.")}
            )

    @property
    def custo_total(self):
        """RF07 - soma automática do custo das atividades da viagem."""
        total = self.atividades.aggregate(soma=models.Sum("custo_estimado"))["soma"]
        return total or 0

    @property
    def categorias(self):
        """Categorias presentes nas atividades desta viagem (para filtro no feed)."""
        return Categoria.objects.filter(atividades__viagem=self).distinct()


class Atividade(models.Model):
    """Uma atividade dentro do itinerário de uma viagem (RF06)."""
    viagem = models.ForeignKey(
        Viagem, on_delete=models.CASCADE, related_name="atividades", verbose_name=_("viagem")
    )
    categoria = models.ForeignKey(
        Categoria, on_delete=models.PROTECT, related_name="atividades", verbose_name=_("categoria")
    )
    nome = models.CharField(_("nome"), max_length=120)
    data_hora = models.DateTimeField(_("data e hora"))
    custo_estimado = models.DecimalField(_("custo estimado"), max_digits=10, decimal_places=2, default=0)
    descricao = models.TextField(_("descrição"), blank=True)

    class Meta:
        verbose_name = _("atividade")
        verbose_name_plural = _("atividades")
        ordering = ["data_hora"]

    def __str__(self):
        return self.nome

    def clean(self):
        """RF10 - a data/hora da atividade deve estar dentro do período da viagem."""
        if self.viagem_id and self.data_hora:
            data_atividade = self.data_hora.date()
            if data_atividade < self.viagem.data_inicio or data_atividade > self.viagem.data_fim:
                raise ValidationError(
                    {"data_hora": _("A data da atividade deve estar dentro do período da viagem.")}
                )
