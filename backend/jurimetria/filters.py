import django_filters

from .models import Concessao, Indeferimento


class FiltroPeriodoUfEspecie(django_filters.FilterSet):
    """Filtros comuns aos dois tipos de benefício: período, UF e espécie."""

    competencia_inicio = django_filters.DateFilter(field_name="competencia", lookup_expr="gte")
    competencia_fim = django_filters.DateFilter(field_name="competencia", lookup_expr="lte")
    uf = django_filters.CharFilter(field_name="uf")
    especie = django_filters.CharFilter(field_name="especie__codigo")


class ConcessaoFilter(FiltroPeriodoUfEspecie):
    class Meta:
        model = Concessao
        fields = ["uf", "especie", "sexo", "clientela"]


class IndeferimentoFilter(FiltroPeriodoUfEspecie):
    class Meta:
        model = Indeferimento
        fields = ["uf", "especie", "sexo", "clientela"]