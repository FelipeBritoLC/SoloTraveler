from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import api_views

router = DefaultRouter()
router.register("categorias", api_views.CategoriaViewSet, basename="categoria")
router.register("viagens", api_views.ViagemViewSet, basename="viagem")
router.register("atividades", api_views.AtividadeViewSet, basename="atividade")

urlpatterns = [
    path("", include(router.urls)),
]
