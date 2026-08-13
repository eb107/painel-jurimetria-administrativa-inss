"""
Importa um arquivo mensal real do Plano de Dados Abertos do INSS (SUIBE).

Uso:
    uv run python manage.py ingest_pda "arquivo.xlsx" --tipo concedido
    uv run python manage.py ingest_pda "arquivo.xlsx" --tipo indeferido

Layout verificado contra os arquivos de junho/2023 baixados do portal oficial
(dadosabertos.inss.gov.br). A linha 1 do arquivo é um título mesclado, a
linha 2 é o cabeçalho real.
"""

from __future__ import annotations

import datetime as dt
import unicodedata
from decimal import Decimal, InvalidOperation
from pathlib import Path

import openpyxl
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from jurimetria.models import Clientela, Concessao, Especie, Indeferimento, Sexo

UF_NOME_PARA_SIGLA = {
    "ACRE": "AC", "ALAGOAS": "AL", "AMAPA": "AP", "AMAZONAS": "AM",
    "BAHIA": "BA", "CEARA": "CE", "DISTRITO FEDERAL": "DF",
    "ESPIRITO SANTO": "ES", "GOIAS": "GO", "MARANHAO": "MA",
    "MATO GROSSO": "MT", "MATO GROSSO DO SUL": "MS", "MINAS GERAIS": "MG",
    "PARA": "PA", "PARAIBA": "PB", "PARANA": "PR", "PERNAMBUCO": "PE",
    "PIAUI": "PI", "RIO DE JANEIRO": "RJ", "RIO GRANDE DO NORTE": "RN",
    "RIO GRANDE DO SUL": "RS", "RONDONIA": "RO", "RORAIMA": "RR",
    "SANTA CATARINA": "SC", "SAO PAULO": "SP", "SERGIPE": "SE",
    "TOCANTINS": "TO",
}

# cabeçalho real (linha 2), verificado nos arquivos de junho/2023
COLUNAS_CONCEDIDO = [
    "APS", "APS", "Competência concessão", "Espécie", "Espécie", "CID", "CID",
    "Despacho", "Despacho", "Dt Nascimento", "Sexo.", "Clientela", "Mun Resid",
    "Vínculo dependentes", "Forma Filiação", "UF", "Qt SM RMI", "Ramo Atividade",
    "Dt DCB", "Dt DDB", "Dt DIB", "País de Acordo Internacional",
    "Classificador PA", "CNAE 2.0", "CNAE 2.0", "Grau Instrução",
    "Qt Anos Contribuição",
]
COLUNAS_INDEFERIDO = [
    "Competência indeferimento", "Espécie", "Espécie", "Motivo Indeferimento",
    "Dt Nascimento", "Sexo.", "Clientela", "Forma Filiação", "UF",
    "Dt Indeferimento", "Ramo Atividade", "APS", "APS", "Dt DER",
]


def normalizar(texto) -> str:
    if texto is None:
        return ""
    texto = str(texto).strip()
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return texto.upper()


def parse_uf(valor) -> str:
    return UF_NOME_PARA_SIGLA.get(normalizar(valor), "")


def parse_sexo(valor) -> str:
    texto = normalizar(valor)
    if texto.startswith("M"):
        return Sexo.MASCULINO
    if texto.startswith("F"):
        return Sexo.FEMININO
    return ""


def parse_clientela(valor) -> str:
    texto = normalizar(valor)
    if texto.startswith("URB"):
        return Clientela.URBANA
    if texto.startswith("RUR"):
        return Clientela.RURAL
    return ""


def parse_competencia(valor) -> dt.date | None:
    if valor is None:
        return None
    texto = str(int(valor))  # vem como 202306
    return dt.date(int(texto[:4]), int(texto[4:6]), 1)


def parse_data(valor) -> dt.date | None:
    if isinstance(valor, dt.datetime):
        return valor.date()
    if isinstance(valor, dt.date):
        return valor
    return None


def parse_municipio(valor) -> str:
    # vem como "15116-PE-Recife", queremos só "Recife"
    if not valor:
        return ""
    return str(valor).split("-")[-1].strip()


def parse_decimal(valor) -> Decimal | None:
    if valor in (None, ""):
        return None
    try:
        return Decimal(str(valor))
    except InvalidOperation:
        return None


class Command(BaseCommand):
    help = "Importa um arquivo mensal XLSX real do Plano de Dados Abertos do INSS."

    def add_arguments(self, parser):
        parser.add_argument("arquivo", type=str)
        parser.add_argument("--tipo", choices=["concedido", "indeferido"], required=True)

    def handle(self, *args, **options):
        caminho = Path(options["arquivo"])
        tipo = options["tipo"]
        if not caminho.exists():
            raise CommandError(f"Arquivo não encontrado: {caminho}")

        wb = openpyxl.load_workbook(caminho, read_only=True, data_only=True)
        ws = wb.worksheets[0]
        linhas = ws.iter_rows(values_only=True)
        next(linhas)  # linha 1: título mesclado, ignora
        cabecalho = list(next(linhas))

        esperado = COLUNAS_CONCEDIDO if tipo == "concedido" else COLUNAS_INDEFERIDO
        if [normalizar(c) for c in cabecalho] != [normalizar(c) for c in esperado]:
            raise CommandError(
                "Cabeçalho do arquivo não bate com o esperado.\n"
                f"Esperado: {esperado}\nEncontrado: {cabecalho}\n"
                "Confira se é o tipo certo (--tipo) ou se o layout desse mês mudou."
            )

        especie_cache: dict[str, Especie] = {}
        objetos = []
        total = 0
        modelo = Concessao if tipo == "concedido" else Indeferimento

        def get_especie(codigo, nome) -> Especie:
            codigo = str(codigo)
            if codigo not in especie_cache:
                especie_cache[codigo], _ = Especie.objects.get_or_create(
                    codigo=codigo, defaults={"descricao": nome or codigo}
                )
            return especie_cache[codigo]

        with transaction.atomic():
            for linha in linhas:
                if tipo == "concedido":
                    obj = Concessao(
                        competencia=parse_competencia(linha[2]),
                        especie=get_especie(linha[3], linha[4]),
                        cid_codigo=str(linha[5] or "").strip(),
                        cid_descricao=str(linha[6] or "").strip(),
                        despacho_codigo=str(linha[7] or "").strip(),
                        despacho_descricao=str(linha[8] or "").strip(),
                        data_nascimento=parse_data(linha[9]),
                        sexo=parse_sexo(linha[10]),
                        clientela=parse_clientela(linha[11]),
                        municipio=parse_municipio(linha[12]),
                        forma_filiacao=str(linha[14] or "").strip(),
                        uf=parse_uf(linha[15]),
                        qt_sm_rmi=parse_decimal(linha[16]),
                        ramo_atividade=str(linha[17] or "").strip(),
                        data_dib=parse_data(linha[20]),
                        qt_anos_contribuicao=linha[26] if isinstance(linha[26], int) else None,
                        aps_codigo=str(linha[0] or "").strip(),
                        aps_nome=str(linha[1] or "").strip(),
                    )
                else:
                    obj = Indeferimento(
                        competencia=parse_competencia(linha[0]),
                        especie=get_especie(linha[1], linha[2]),
                        motivo=str(linha[3] or "").strip(),
                        data_nascimento=parse_data(linha[4]),
                        sexo=parse_sexo(linha[5]),
                        clientela=parse_clientela(linha[6]),
                        forma_filiacao=str(linha[7] or "").strip(),
                        uf=parse_uf(linha[8]),
                        data_indeferimento=parse_data(linha[9]),
                        ramo_atividade=str(linha[10] or "").strip(),
                        aps_codigo=str(linha[11] or "").strip(),
                        aps_nome=str(linha[12] or "").strip(),
                        data_der=parse_data(linha[13]),
                    )

                if obj.competencia is None:
                    continue
                objetos.append(obj)

                if len(objetos) >= 5000:
                    modelo.objects.bulk_create(objetos)
                    total += len(objetos)
                    self.stdout.write(f"{total} linhas importadas...")
                    objetos = []

            if objetos:
                modelo.objects.bulk_create(objetos)
                total += len(objetos)

        self.stdout.write(self.style.SUCCESS(f"{total} registros importados de {caminho.name} (tipo={tipo})."))