from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("concessoes", views.ConcessaoViewSet, basename="concessao")
router.register("indeferimentos", views.IndeferimentoViewSet, basename="indeferimento")

urlpatterns = [
    path("kpis/", views.kpis_view, name="kpis"),
    path("serie-temporal/", views.serie_temporal_view, name="serie-temporal"),
    path("por-uf/", views.por_uf_view, name="por-uf"),
    path("por-especie/", views.por_especie_view, name="por-especie"),
    path(
        "motivos-indeferimento/",
        views.motivos_indeferimento_view,
        name="motivos-indeferimento",
    ),
    path("especies/", views.especies_view, name="especies"),
    path("ufs/", views.ufs_view, name="ufs"),
    path("", include(router.urls)),
]