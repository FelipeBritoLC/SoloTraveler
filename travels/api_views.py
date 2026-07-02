from rest_framework import permissions, viewsets
from rest_framework.pagination import PageNumberPagination

from .models import Atividade, Categoria, Viagem
from .serializers import AtividadeSerializer, CategoriaSerializer, ViagemSerializer


class ApiPagination(PageNumberPagination):
    """Paginação da API (também atende ao requisito de Paginação)."""
    page_size = 6
    page_size_query_param = "page_size"


class IsOwnerOrReadOnly(permissions.BasePermission):
    """RF02/RF11 - só o dono da viagem pode editar/excluir seus dados."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        dono = obj.usuario if hasattr(obj, "usuario") else obj.viagem.usuario
        return dono == request.user


class CategoriaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.AllowAny]


class ViagemViewSet(viewsets.ModelViewSet):
    """
    API REST de viagens.
    - Usuários anônimos só enxergam viagens públicas (RF03).
    - Usuários autenticados enxergam as públicas + as próprias.
    - Somente o dono pode criar/editar/excluir (RF02, RF11).
    """
    serializer_class = ViagemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    pagination_class = ApiPagination

    def get_queryset(self):
        user = self.request.user
        qs = Viagem.objects.select_related("usuario").all()
        if user.is_authenticated:
            from django.db.models import Q
            return qs.filter(Q(publica=True) | Q(usuario=user)).distinct()
        return qs.filter(publica=True)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class AtividadeViewSet(viewsets.ModelViewSet):
    serializer_class = AtividadeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    pagination_class = ApiPagination

    def get_queryset(self):
        user = self.request.user
        qs = Atividade.objects.select_related("viagem", "categoria").all()
        if user.is_authenticated:
            from django.db.models import Q
            return qs.filter(Q(viagem__publica=True) | Q(viagem__usuario=user)).distinct()
        return qs.filter(viagem__publica=True)
