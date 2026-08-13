from rest_framework import serializers

from .models import Concessao, Especie, Indeferimento


class EspecieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Especie
        fields = ["id", "codigo", "descricao"]


class ConcessaoSerializer(serializers.ModelSerializer):
    especie_codigo = serializers.CharField(source="especie.codigo", read_only=True)
    especie_descricao = serializers.CharField(source="especie.descricao", read_only=True)

    class Meta:
        model = Concessao
        fields = [
            "id", "competencia", "especie_codigo", "especie_descricao",
            "cid_codigo", "cid_descricao", "despacho_codigo", "despacho_descricao",
            "data_nascimento", "sexo", "clientela", "forma_filiacao",
            "ramo_atividade", "uf", "municipio", "qt_sm_rmi",
            "qt_anos_contribuicao", "data_dib", "aps_codigo", "aps_nome",
        ]


class IndeferimentoSerializer(serializers.ModelSerializer):
    especie_codigo = serializers.CharField(source="especie.codigo", read_only=True)
    especie_descricao = serializers.CharField(source="especie.descricao", read_only=True)

    class Meta:
        model = Indeferimento
        fields = [
            "id", "competencia", "especie_codigo", "especie_descricao",
            "motivo", "data_nascimento", "sexo", "clientela", "forma_filiacao",
            "ramo_atividade", "uf", "data_indeferimento", "data_der",
            "aps_codigo", "aps_nome",
        ]