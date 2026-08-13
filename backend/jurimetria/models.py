from django.db import models


class Sexo(models.TextChoices):
    MASCULINO = "M", "Masculino"
    FEMININO = "F", "Feminino"


class Clientela(models.TextChoices):
    URBANA = "URBANA", "Urbana"
    RURAL = "RURAL", "Rural"


class Especie(models.Model):
    codigo = models.CharField(max_length=10, unique=True)
    descricao = models.CharField(max_length=255)

    class Meta:
        ordering = ["codigo"]

    def __str__(self):
        return f"{self.codigo} - {self.descricao}"


class BeneficioBase(models.Model):
    """Campos que existem tanto em Concessao quanto em Indeferimento."""
    competencia = models.DateField(db_index=True)
    especie = models.ForeignKey(Especie, on_delete=models.PROTECT, related_name="+")
    data_nascimento = models.DateField(null=True, blank=True)
    sexo = models.CharField(max_length=1, choices=Sexo.choices, blank=True)
    clientela = models.CharField(max_length=10, choices=Clientela.choices, blank=True)
    forma_filiacao = models.CharField(max_length=120, blank=True)
    ramo_atividade = models.CharField(max_length=120, blank=True)
    uf = models.CharField(max_length=2, db_index=True, blank=True)
    aps_codigo = models.CharField(max_length=20, blank=True)
    aps_nome = models.CharField(max_length=255, blank=True)

    class Meta:
        abstract = True


class Concessao(BeneficioBase):
    cid_codigo = models.CharField(max_length=10, blank=True)
    cid_descricao = models.CharField(max_length=255, blank=True)
    despacho_codigo = models.CharField(max_length=10, blank=True)
    despacho_descricao = models.CharField(max_length=255, blank=True)
    municipio = models.CharField(max_length=120, blank=True)
    qt_sm_rmi = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    qt_anos_contribuicao = models.PositiveIntegerField(null=True, blank=True)
    data_dib = models.DateField(null=True, blank=True, help_text="Data de Início do Benefício")

    class Meta:
        indexes = [
            models.Index(fields=["competencia", "uf"]),
            models.Index(fields=["competencia", "especie"]),
        ]

    def __str__(self):
        return f"Concessão {self.especie_id} - {self.competencia} - {self.uf}"


class Indeferimento(BeneficioBase):
    motivo = models.CharField(max_length=255, db_index=True)
    data_indeferimento = models.DateField(null=True, blank=True)
    data_der = models.DateField(null=True, blank=True, help_text="Data de Entrada do Requerimento")

    class Meta:
        indexes = [
            models.Index(fields=["competencia", "uf"]),
            models.Index(fields=["competencia", "especie"]),
        ]

    def __str__(self):
        return f"Indeferimento {self.especie_id} - {self.competencia} - {self.uf}"