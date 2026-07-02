from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import AtividadeForm, RegistroForm, ViagemForm
from .models import Atividade, Categoria, Viagem


# ---------------------------------------------------------------------------
# Autenticação (RF01)
# ---------------------------------------------------------------------------

class MinhaLoginView(LoginView):
    template_name = "registration/login.html"


def registrar(request):
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            return redirect("travels:minhas_viagens")
    else:
        form = RegistroForm()
    return render(request, "registration/register.html", {"form": form})


# ---------------------------------------------------------------------------
# Feed público (RF03, RF08, RF09) - com paginação
# ---------------------------------------------------------------------------

class FeedPublicoView(ListView):
    model = Viagem
    template_name = "travels/feed.html"
    context_object_name = "viagens"
    paginate_by = 6  # RF08 - 6 roteiros por página

    def get_queryset(self):
        qs = Viagem.objects.filter(publica=True).select_related("usuario")
        categoria_id = self.request.GET.get("categoria")
        if categoria_id:
            qs = qs.filter(atividades__categoria_id=categoria_id).distinct()
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categorias"] = Categoria.objects.all()
        context["categoria_selecionada"] = self.request.GET.get("categoria", "")
        return context


# ---------------------------------------------------------------------------
# Minhas viagens (RF02, RF04) - somente do usuário logado
# ---------------------------------------------------------------------------

class MinhasViagensView(LoginRequiredMixin, ListView):
    model = Viagem
    template_name = "travels/viagem_list.html"
    context_object_name = "viagens"
    paginate_by = 6

    def get_queryset(self):
        return Viagem.objects.filter(usuario=self.request.user)


class ViagemDetailView(DetailView):
    """Detalhe de uma viagem. Viagem privada só pode ser vista pelo dono."""
    model = Viagem
    template_name = "travels/viagem_detail.html"
    context_object_name = "viagem"

    def get_queryset(self):
        return Viagem.objects.select_related("usuario")

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.publica and self.object.usuario != request.user:
            return redirect("travels:feed")
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class ViagemCreateView(LoginRequiredMixin, CreateView):
    model = Viagem
    form_class = ViagemForm
    template_name = "travels/viagem_form.html"

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("travels:viagem_detail", kwargs={"pk": self.object.pk})


class ViagemDonoMixin(LoginRequiredMixin, UserPassesTestMixin):
    """RF02/RF11 - garante que só o criador pode editar/excluir a viagem."""

    def test_func(self):
        viagem = self.get_object()
        return viagem.usuario == self.request.user

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        return redirect("travels:minhas_viagens")


class ViagemUpdateView(ViagemDonoMixin, UpdateView):
    model = Viagem
    form_class = ViagemForm
    template_name = "travels/viagem_form.html"

    def get_success_url(self):
        return reverse_lazy("travels:viagem_detail", kwargs={"pk": self.object.pk})


class ViagemDeleteView(ViagemDonoMixin, DeleteView):
    model = Viagem
    template_name = "travels/viagem_confirm_delete.html"
    success_url = reverse_lazy("travels:minhas_viagens")


# ---------------------------------------------------------------------------
# Atividades (RF05, RF06, RF10) - autorização por dono da viagem
# ---------------------------------------------------------------------------

class AtividadeCreateView(LoginRequiredMixin, CreateView):
    model = Atividade
    form_class = AtividadeForm
    template_name = "travels/atividade_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.viagem = get_object_or_404(Viagem, pk=kwargs["viagem_pk"])
        if self.viagem.usuario != request.user:
            return redirect("travels:viagem_detail", pk=self.viagem.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["viagem"] = self.viagem
        return kwargs

    def form_valid(self, form):
        form.instance.viagem = self.viagem
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["viagem"] = self.viagem
        return context

    def get_success_url(self):
        return reverse_lazy("travels:viagem_detail", kwargs={"pk": self.viagem.pk})


class AtividadeDonoMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        atividade = self.get_object()
        return atividade.viagem.usuario == self.request.user

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        return redirect("travels:minhas_viagens")


class AtividadeUpdateView(AtividadeDonoMixin, UpdateView):
    model = Atividade
    form_class = AtividadeForm
    template_name = "travels/atividade_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["viagem"] = self.object.viagem if hasattr(self, "object") else self.get_object().viagem
        return kwargs

    def get_success_url(self):
        return reverse_lazy("travels:viagem_detail", kwargs={"pk": self.object.viagem.pk})


class AtividadeDeleteView(AtividadeDonoMixin, DeleteView):
    model = Atividade
    template_name = "travels/atividade_confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy("travels:viagem_detail", kwargs={"pk": self.object.viagem.pk})
