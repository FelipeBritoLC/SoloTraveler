"""
Testes automatizados do Solo Traveler.

Cobrem:
- RF10: validação de datas das atividades (não podem ficar fora do período da viagem);
- RF07: cálculo automático do custo total da viagem;
- RF11: permissões (usuário anônimo e usuário "B" não podem editar viagem de "A");
- comportamento básico da API REST (listagem pública x criação exige autenticação).
"""
from datetime import date, datetime

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import make_aware

from rest_framework.test import APITestCase

from .models import Atividade, Categoria, Viagem


class ViagemModelTest(TestCase):
    """Testa regras de negócio do model Viagem (RF07)."""

    def setUp(self):
        self.usuario = User.objects.create_user(username="ana", password="senha12345")
        self.categoria = Categoria.objects.create(nome="Museus")
        self.viagem = Viagem.objects.create(
            usuario=self.usuario,
            titulo="Roteiro em Lisboa",
            destino="Lisboa",
            data_inicio=date(2026, 8, 1),
            data_fim=date(2026, 8, 10),
            publica=True,
        )

    def test_custo_total_sem_atividades_e_zero(self):
        self.assertEqual(self.viagem.custo_total, 0)

    def test_custo_total_soma_atividades(self):
        Atividade.objects.create(
            viagem=self.viagem,
            categoria=self.categoria,
            nome="Visita ao Mosteiro",
            data_hora=make_aware(datetime(2026, 8, 2, 10, 0)),
            custo_estimado=50,
        )
        Atividade.objects.create(
            viagem=self.viagem,
            categoria=self.categoria,
            nome="Jantar",
            data_hora=make_aware(datetime(2026, 8, 2, 20, 0)),
            custo_estimado=30,
        )
        self.assertEqual(self.viagem.custo_total, 80)


class AtividadeValidacaoDatasTest(TestCase):
    """RF10 - a atividade deve estar dentro do período da viagem."""

    def setUp(self):
        self.usuario = User.objects.create_user(username="bruno", password="senha12345")
        self.categoria = Categoria.objects.create(nome="Trilhas")
        self.viagem = Viagem.objects.create(
            usuario=self.usuario,
            titulo="Roteiro na Serra",
            destino="Serra da Mantiqueira",
            data_inicio=date(2026, 5, 1),
            data_fim=date(2026, 5, 5),
        )

    def test_atividade_dentro_do_periodo_e_valida(self):
        atividade = Atividade(
            viagem=self.viagem,
            categoria=self.categoria,
            nome="Trilha da Pedra Redonda",
            data_hora=make_aware(datetime(2026, 5, 3, 9, 0)),
            custo_estimado=0,
        )
        atividade.full_clean()  # não deve levantar erro

    def test_atividade_fora_do_periodo_gera_erro(self):
        atividade = Atividade(
            viagem=self.viagem,
            categoria=self.categoria,
            nome="Trilha fora de época",
            data_hora=make_aware(datetime(2026, 6, 1, 9, 0)),
            custo_estimado=0,
        )
        with self.assertRaises(ValidationError):
            atividade.full_clean()


class PermissaoViagemTest(TestCase):
    """RF11 - testes de permissão de edição/exclusão de viagens."""

    def setUp(self):
        self.usuario_a = User.objects.create_user(username="usuario_a", password="senha12345")
        self.usuario_b = User.objects.create_user(username="usuario_b", password="senha12345")
        self.viagem_de_a = Viagem.objects.create(
            usuario=self.usuario_a,
            titulo="Viagem do usuário A",
            destino="Roma",
            data_inicio=date(2026, 9, 1),
            data_fim=date(2026, 9, 10),
        )

    def test_usuario_anonimo_nao_acessa_edicao(self):
        url = reverse("travels:viagem_update", args=[self.viagem_de_a.pk])
        response = self.client.get(url)
        # deve redirecionar para o login, não deixar editar diretamente
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_usuario_b_nao_pode_editar_viagem_de_a(self):
        self.client.login(username="usuario_b", password="senha12345")
        url = reverse("travels:viagem_update", args=[self.viagem_de_a.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # é redirecionado, não acessa o form

    def test_usuario_a_pode_editar_a_propria_viagem(self):
        self.client.login(username="usuario_a", password="senha12345")
        url = reverse("travels:viagem_update", args=[self.viagem_de_a.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_usuario_b_nao_pode_excluir_viagem_de_a(self):
        self.client.login(username="usuario_b", password="senha12345")
        url = reverse("travels:viagem_delete", args=[self.viagem_de_a.pk])
        self.client.post(url)
        self.assertTrue(Viagem.objects.filter(pk=self.viagem_de_a.pk).exists())


class FeedPublicoTest(TestCase):
    """Testa o feed público e a paginação (RF08, RF09)."""

    def setUp(self):
        self.usuario = User.objects.create_user(username="carla", password="senha12345")
        for i in range(8):
            Viagem.objects.create(
                usuario=self.usuario,
                titulo=f"Roteiro público {i}",
                destino="Algum lugar",
                data_inicio=date(2026, 1, 1),
                data_fim=date(2026, 1, 5),
                publica=True,
            )
        Viagem.objects.create(
            usuario=self.usuario,
            titulo="Roteiro privado",
            destino="Casa",
            data_inicio=date(2026, 1, 1),
            data_fim=date(2026, 1, 2),
            publica=False,
        )

    def test_feed_mostra_apenas_viagens_publicas(self):
        response = self.client.get(reverse("travels:feed"))
        self.assertEqual(response.status_code, 200)
        for viagem in response.context["viagens"]:
            self.assertTrue(viagem.publica)

    def test_feed_e_paginado(self):
        response = self.client.get(reverse("travels:feed"))
        # paginate_by = 6, temos 8 viagens públicas
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["viagens"]), 6)


class ApiTest(APITestCase):
    """Testes básicos da API REST (Django REST Framework)."""

    def setUp(self):
        self.usuario = User.objects.create_user(username="dani", password="senha12345")
        self.categoria = Categoria.objects.create(nome="Gastronomia")
        self.viagem_publica = Viagem.objects.create(
            usuario=self.usuario,
            titulo="Roteiro gastronômico",
            destino="São Paulo",
            data_inicio=date(2026, 3, 1),
            data_fim=date(2026, 3, 5),
            publica=True,
        )

    def test_listar_viagens_publicas_sem_autenticacao(self):
        response = self.client.get("/api/viagens/")
        self.assertEqual(response.status_code, 200)

    def test_criar_viagem_sem_autenticacao_e_negado(self):
        dados = {
            "titulo": "Tentativa anônima",
            "destino": "Nowhere",
            "data_inicio": "2026-04-01",
            "data_fim": "2026-04-05",
            "publica": True,
        }
        response = self.client.post("/api/viagens/", dados)
        self.assertEqual(response.status_code, 403)

    def test_criar_viagem_autenticado(self):
        self.client.login(username="dani", password="senha12345")
        dados = {
            "titulo": "Nova viagem via API",
            "destino": "Curitiba",
            "data_inicio": "2026-04-01",
            "data_fim": "2026-04-05",
            "publica": False,
        }
        response = self.client.post("/api/viagens/", dados)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["usuario"], "dani")
