from django.core.management.base import BaseCommand
from django.db.models import Count
from django.db.models.functions import TruncMonth

from jurimetria.models import Concessao, Indeferimento


class Command(BaseCommand):
    help = "Mostra quantos registros existem por mes, para conferencia."

    def handle(self, *args, **options):
        self.stdout.write(f"Total concessoes: {Concessao.objects.count()}")
        self.stdout.write(f"Total indeferimentos: {Indeferimento.objects.count()}")
        self.stdout.write("")
        self.stdout.write("Concessoes por mes:")
        for r in Concessao.objects.annotate(mes=TruncMonth("competencia")).values("mes").annotate(qtd=Count("id")).order_by("mes"):
            self.stdout.write(f"  {r['mes']}  {r['qtd']}")
        self.stdout.write("")
        self.stdout.write("Indeferimentos por mes:")
        for r in Indeferimento.objects.annotate(mes=TruncMonth("competencia")).values("mes").annotate(qtd=Count("id")).order_by("mes"):
            self.stdout.write(f"  {r['mes']}  {r['qtd']}")