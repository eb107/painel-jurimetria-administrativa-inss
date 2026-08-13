from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.views.decorators.cache import cache_page
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from .filters import ConcessaoFilter, IndeferimentoFilter
from .models import Concessao, Especie, Indeferimento
from .serializers import ConcessaoSerializer, EspecieSerializer, IndeferimentoSerializer


def _aplicar_filtros(queryset, request, especie_field="especie__codigo"):
    """Filtros compartilhados pelos endpoints analiticos: uf, especie e periodo."""
    params = request.query_params
    uf = params.get("uf")
    especie = params.get("especie")
    competencia_inicio = params.get("competencia_inicio")
    competencia_fim = params.get("competencia_fim")

    if uf:
        queryset = queryset.filter(uf=uf)
    if especie:
        queryset = queryset.filter(**{especie_field: especie})
    if competencia_inicio:
        queryset = queryset.filter(competencia__gte=competencia_inicio)
    if competencia_fim:
        queryset = queryset.filter(competencia__lte=competencia_fim)
    return queryset


def _taxa(indeferidos: int, concedidos: int) -> float:
    total = indeferidos + concedidos
    if not total:
        return 0.0
    return round((indeferidos / total) * 100, 2)


def _percentual(parte: int, total: int) -> float:
    if not total:
        return 0.0
    return round((parte / total) * 100, 2)


class ConcessaoViewSet(ReadOnlyModelViewSet):
    queryset = Concessao.objects.select_related("especie").all().order_by("-competencia")
    serializer_class = ConcessaoSerializer
    filterset_class = ConcessaoFilter


class IndeferimentoViewSet(ReadOnlyModelViewSet):
    queryset = Indeferimento.objects.select_related("especie").all().order_by("-competencia")
    serializer_class = IndeferimentoSerializer
    filterset_class = IndeferimentoFilter


@cache_page(60 * 10)
@api_view(["GET"])
def kpis_view(request):
    concessoes_qs = _aplicar_filtros(Concessao.objects.all(), request)
    concedidos = concessoes_qs.count()
    indeferidos = _aplicar_filtros(Indeferimento.objects.all(), request).count()
    total = concedidos + indeferidos

    # Esse despacho especifico marca concessao que o INSS so liberou depois
    # que o segurado entrou com acao na Justica, nao administrativamente.
    # E a metrica de judicializacao: quanto maior, mais vezes o INSS so cede
    # sob decisao judicial em vez de reconhecer o direito na via administrativa.
    concessoes_judiciais = concessoes_qs.filter(
        despacho_descricao="Concessao Decorrente de Acao Judicial"
    ).count()

    return Response({
        "total_concedidos": concedidos,
        "total_indeferidos": indeferidos,
        "total_geral": total,
        "taxa_indeferimento": _taxa(indeferidos, concedidos),
        "total_concessoes_judiciais": concessoes_judiciais,
        "taxa_judicializacao": _percentual(concessoes_judiciais, concedidos),
    })


@cache_page(60 * 10)
@api_view(["GET"])
def serie_temporal_view(request):
    concedidos_qs = (
        _aplicar_filtros(Concessao.objects.all(), request)
        .annotate(mes=TruncMonth("competencia"))
        .values("mes")
        .annotate(total=Count("id"))
    )
    indeferidos_qs = (
        _aplicar_filtros(Indeferimento.objects.all(), request)
        .annotate(mes=TruncMonth("competencia"))
        .values("mes")
        .annotate(total=Count("id"))
    )

    dados = {}
    for row in concedidos_qs:
        chave = row["mes"].strftime("%Y-%m")
        dados.setdefault(chave, {"concedidos": 0, "indeferidos": 0})["concedidos"] = row["total"]
    for row in indeferidos_qs:
        chave = row["mes"].strftime("%Y-%m")
        dados.setdefault(chave, {"concedidos": 0, "indeferidos": 0})["indeferidos"] = row["total"]

    resultado = [
        {
            "competencia": chave,
            "concedidos": valores["concedidos"],
            "indeferidos": valores["indeferidos"],
            "taxa_indeferimento": _taxa(valores["indeferidos"], valores["concedidos"]),
        }
        for chave, valores in sorted(dados.items())
    ]
    return Response(resultado)


@cache_page(60 * 10)
@api_view(["GET"])
def por_uf_view(request):
    concedidos_qs = _aplicar_filtros(Concessao.objects.all(), request).values("uf").annotate(total=Count("id"))
    indeferidos_qs = _aplicar_filtros(Indeferimento.objects.all(), request).values("uf").annotate(total=Count("id"))

    dados = {}
    for row in concedidos_qs:
        if not row["uf"]:
            continue
        dados.setdefault(row["uf"], {"concedidos": 0, "indeferidos": 0})["concedidos"] = row["total"]
    for row in indeferidos_qs:
        if not row["uf"]:
            continue
        dados.setdefault(row["uf"], {"concedidos": 0, "indeferidos": 0})["indeferidos"] = row["total"]

    resultado = [
        {
            "uf": uf,
            "concedidos": valores["concedidos"],
            "indeferidos": valores["indeferidos"],
            "taxa_indeferimento": _taxa(valores["indeferidos"], valores["concedidos"]),
        }
        for uf, valores in dados.items()
    ]
    resultado.sort(key=lambda item: item["taxa_indeferimento"], reverse=True)
    return Response(resultado)


@cache_page(60 * 10)
@api_view(["GET"])
def por_especie_view(request):
    concedidos_qs = (
        _aplicar_filtros(Concessao.objects.all(), request)
        .values("especie__codigo", "especie__descricao")
        .annotate(total=Count("id"))
    )
    indeferidos_qs = (
        _aplicar_filtros(Indeferimento.objects.all(), request)
        .values("especie__codigo", "especie__descricao")
        .annotate(total=Count("id"))
    )

    dados = {}
    for row in concedidos_qs:
        codigo = row["especie__codigo"]
        item = dados.setdefault(codigo, {
            "especie_codigo": codigo,
            "especie_descricao": row["especie__descricao"],
            "concedidos": 0,
            "indeferidos": 0,
        })
        item["concedidos"] = row["total"]
    for row in indeferidos_qs:
        codigo = row["especie__codigo"]
        item = dados.setdefault(codigo, {
            "especie_codigo": codigo,
            "especie_descricao": row["especie__descricao"],
            "concedidos": 0,
            "indeferidos": 0,
        })
        item["indeferidos"] = row["total"]

    resultado = []
    for item in dados.values():
        item["taxa_indeferimento"] = _taxa(item["indeferidos"], item["concedidos"])
        resultado.append(item)
    resultado.sort(key=lambda item: item["concedidos"] + item["indeferidos"], reverse=True)
    return Response(resultado)


@cache_page(60 * 10)
@api_view(["GET"])
def motivos_indeferimento_view(request):
    qs = _aplicar_filtros(Indeferimento.objects.all(), request)
    # "{ñ class}" nao e um motivo de indeferimento de verdade, e um valor
    # invalido que ja vem assim no arquivo aberto do INSS (confirmado: nao
    # e gerado pelo ingest_pda, o dado bruto ja chega assim). Afeta 0,12%
    # dos indeferimentos, mas sem excluir pode subir no ranking quando o
    # filtro aplicado deixa poucos casos no total.
    qs = qs.exclude(motivo="{ñ class}")
    total_indeferidos = qs.count()

    agregados = qs.values("motivo").annotate(total=Count("id")).order_by("-total")[:15]

    resultado = [
        {
            "motivo": row["motivo"],
            "total": row["total"],
            "percentual": round((row["total"] / total_indeferidos) * 100, 2) if total_indeferidos else 0,
        }
        for row in agregados
    ]
    return Response(resultado)


@cache_page(60 * 60)
@api_view(["GET"])
def especies_view(request):
    return Response(EspecieSerializer(Especie.objects.all(), many=True).data)


@cache_page(60 * 60)
@api_view(["GET"])
def ufs_view(request):
    ufs_concedidos = Concessao.objects.exclude(uf="").values_list("uf", flat=True).distinct()
    ufs_indeferidos = Indeferimento.objects.exclude(uf="").values_list("uf", flat=True).distinct()
    todas = sorted(set(ufs_concedidos) | set(ufs_indeferidos))
    return Response(todas)
