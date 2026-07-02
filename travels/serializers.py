from rest_framework import serializers

from .models import Atividade, Categoria, Viagem


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nome"]


class AtividadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Atividade
        fields = ["id", "viagem", "categoria", "nome", "data_hora", "custo_estimado", "descricao"]

    def validate(self, data):
        """RF10 via API - valida se a data está dentro do período da viagem."""
        viagem = data.get("viagem") or getattr(self.instance, "viagem", None)
        data_hora = data.get("data_hora") or getattr(self.instance, "data_hora", None)
        if viagem and data_hora:
            data_atividade = data_hora.date()
            if data_atividade < viagem.data_inicio or data_atividade > viagem.data_fim:
                raise serializers.ValidationError(
                    "A data da atividade deve estar dentro do período da viagem."
                )
        return data


class ViagemSerializer(serializers.ModelSerializer):
    usuario = serializers.ReadOnlyField(source="usuario.username")
    custo_total = serializers.ReadOnlyField()
    atividades = AtividadeSerializer(many=True, read_only=True)

    class Meta:
        model = Viagem
        fields = [
            "id", "usuario", "titulo", "destino", "data_inicio", "data_fim",
            "publica", "foto", "custo_total", "atividades",
        ]

    def validate(self, data):
        inicio = data.get("data_inicio") or getattr(self.instance, "data_inicio", None)
        fim = data.get("data_fim") or getattr(self.instance, "data_fim", None)
        if inicio and fim and fim < inicio:
            raise serializers.ValidationError(
                "A data de fim não pode ser anterior à data de início."
            )
        return data
