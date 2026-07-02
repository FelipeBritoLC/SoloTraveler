from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = "travels"

urlpatterns = [
    path("", views.FeedPublicoView.as_view(), name="feed"),
    path("registrar/", views.registrar, name="registrar"),
    path("login/", views.MinhaLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),

    path("minhas-viagens/", views.MinhasViagensView.as_view(), name="minhas_viagens"),
    path("viagens/nova/", views.ViagemCreateView.as_view(), name="viagem_create"),
    path("viagens/<int:pk>/", views.ViagemDetailView.as_view(), name="viagem_detail"),
    path("viagens/<int:pk>/editar/", views.ViagemUpdateView.as_view(), name="viagem_update"),
    path("viagens/<int:pk>/excluir/", views.ViagemDeleteView.as_view(), name="viagem_delete"),

    path("viagens/<int:viagem_pk>/atividades/nova/", views.AtividadeCreateView.as_view(), name="atividade_create"),
    path("atividades/<int:pk>/editar/", views.AtividadeUpdateView.as_view(), name="atividade_update"),
    path("atividades/<int:pk>/excluir/", views.AtividadeDeleteView.as_view(), name="atividade_delete"),
]
