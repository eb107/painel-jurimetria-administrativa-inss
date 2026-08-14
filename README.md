# Painel de Jurimetria Administrativa (INSS)

Painel analítico que cruza dados reais de **concessão** e **indeferimento** de
benefícios previdenciários do INSS, feito como teste técnico para a vaga de
Analista de Dados do escritório **Santana & Guedes Advogados** (Recife/PE,
atuação previdenciária). Backend em Django + Django REST Framework
(gerenciado com `uv`), frontend em React + Vite + TypeScript + Tailwind CSS.

## Sumário

- [Decisões técnicas importantes](#decisões-técnicas-importantes-leia-antes)
- [Arquitetura](#arquitetura)
- [Modelo de dados](#modelo-de-dados)
- [Como rodar o backend](#como-rodar-o-backend)
- [Como rodar o frontend](#como-rodar-o-frontend)
- [Endpoints da API](#endpoints-da-api)
- [Estrutura de pastas](#estrutura-de-pastas)
- [Limitações e próximos passos](#limitações-e-próximos-passos)

## Decisões técnicas importantes (leia antes)

**Os dados são reais**, baixados diretamente do Plano de Dados Abertos do
INSS/DATAPREV (`dadosabertos.inss.gov.br`), os mesmos conjuntos linkados no
enunciado do teste
([concedidos](https://dados.gov.br/dados/conjuntos-dados/beneficios-concedidos-plano-de-dados-abertos-jun-2023-a-jun-2025) e
[indeferidos](https://dados.gov.br/dados/conjuntos-dados/beneficios-indeferidos-plano-de-dados-abertos-jun-2023-a-jun-2025)).
O período completo publicado vai de jun/2023 a jun/2025 (25 meses, um arquivo
XLSX por mês, dezenas de milhões de linhas ao todo). Importei **6 meses**
(jun a nov/2023), decisão deliberada: o próprio enunciado pede um "painel
**simplificado**", e 6 meses já somam quase **6,1 milhões de registros**
(3.356.650 concedidos + 2.743.332 indeferidos), volume mais que suficiente
para toda análise proposta sem precisar de infraestrutura além de SQLite. O
comando de importação (`ingest_pda`, ver abaixo) funciona pra qualquer mês
do período completo, só apontar pro arquivo baixado e rodar.

**Duas particularidades dos dados de origem, verificadas e não corrigidas**
(documentadas aqui em vez de escondidas):

- Um valor de motivo de indeferimento, `"{ñ class}"`, é um artefato inválido
  que já vem assim no arquivo do INSS (confirmei: não é gerado pelo parser de
  importação). Afeta 0,12% dos indeferimentos importados e é excluído do
  ranking de motivos na API (`motivos_indeferimento_view`), pra não subir
  artificialmente quando um filtro reduz muito o total.
- Alguns valores de motivo vêm truncados em exatamente 100 caracteres na
  fonte (aparentam limite de campo de sistema legado do INSS; não é
  fatiamento deste projeto).

## Arquitetura

```
Frontend (React + Vite + TS + Tailwind, porta 5173)
        │
        │  HTTP/JSON  →  /api/...
        ▼
Backend (Django + DRF + SQLite, porta 8000)
        ▲
        │  manage.py ingest_pda
        │
Arquivos XLSX do Plano de Dados Abertos do INSS
```

O frontend não faz nenhuma agregação em memória: cada gráfico consome um
endpoint que já devolve o número pronto (contagem, taxa, ranking), calculado
via `annotate`/`Count`/`TruncMonth` do ORM do Django. Os cinco endpoints
analíticos (`kpis`, `serie-temporal`, `por-uf`, `por-especie`,
`motivos-indeferimento`) são cacheados em memória por `cache_page` (10
minutos, 1 hora para `especies`/`ufs` que são listas fixas), porque os dados
são só leitura após a importação, então recalcular a mesma combinação de
filtro em toda troca de tela é desperdício. Se o painel crescesse pro período
completo (jun/2023–jun/2025), o próximo passo de performance seria trocar
esse cache por uma tabela de resumo pré-agregada (por mês/UF/espécie), já que
cache não reduz o custo da primeira consulta de cada combinação de filtro, só
evita repetir.

Os filtros (UF, espécie, competência início/fim) ficam sincronizados com a
query string da URL: sobrevivem a um F5 e o link pode ser compartilhado já
filtrado.

## Modelo de dados

Dois modelos principais, com um conjunto de campos comuns herdado de uma
classe abstrata (`competencia`, `especie`, `uf`, `sexo`, `clientela`, `forma_filiacao`,
`ramo_atividade`, `data_nascimento`, `aps_codigo`, `aps_nome`):

- **`Concessao`** — benefício deferido. Campos extras: `cid_codigo`,
  `cid_descricao`, `despacho_codigo`, `despacho_descricao`, `municipio`,
  `qt_sm_rmi`, `qt_anos_contribuicao`, `data_dib`.
- **`Indeferimento`** — benefício negado. Campos extras: `motivo`,
  `data_indeferimento`, `data_der`.

`Especie` (espécie de benefício, ex. "41 - Aposentadoria por Idade") é uma
tabela de apoio normalizada, referenciada por FK nos dois modelos, pra
permitir agrupar/rankear sem repetir texto em cada linha. Há índices em
`competencia`, `uf`, `motivo` e compostos (`competencia+uf`,
`competencia+especie`), porque os filtros mais comuns passam por essas
colunas.

Quando o campo `despacho_descricao` é `"Concessao Decorrente de Acao
Judicial"`, o INSS só concedeu o benefício depois que o segurado entrou com
ação na Justiça, não administrativamente. O painel expõe isso como KPI de
"taxa de judicialização" (16,25% no período importado, 545.593 casos), métrica
que fala diretamente com o negócio de um escritório previdenciário.

## Como rodar o backend

Pré-requisitos: [`uv`](https://docs.astral.sh/uv/) instalado.

```bash
cd backend
uv run python manage.py migrate
```

Os dados reais não vão no repositório (arquivos de dezenas de MB cada,
listados no `.gitignore`). Baixe pelo menos um mês de cada tipo nos links do
enunciado (aba "Recursos" de cada conjunto de dados) e importe. Pra facilitar,
aqui vão os links diretos dos arquivos que eu mesmo baixei e usei (jul a
nov/2023 — jun/2023 também faz parte do período importado, mas o link direto
não foi conferido, então pegue esse mês pela aba "Recursos" do próprio
conjunto de dados):

| Mês | Concedidos | Indeferidos |
|---|---|---|
| Julho/2023 | [xlsx](https://armazenamento-dadosabertos.s3.sa-east-1.amazonaws.com/PDA_2023_2025/Grupos_de_dados/Benef%C3%ADcios+concedidos/JUN23-ABR24/DADOS+ABERTOS_CONCEDIDOS_JULHO+2023.xlsx) | [xlsx](https://armazenamento-dadosabertos.s3.sa-east-1.amazonaws.com/PDA_2023_2025/Grupos_de_dados/Benef%C3%ADcios+Indeferidos/UPDATED/INDEFERIDOS_DADOS_ABERTOS_JULHO+2023.xlsx) |
| Agosto/2023 | [xlsx](https://armazenamento-dadosabertos.s3.sa-east-1.amazonaws.com/PDA_2023_2025/Grupos_de_dados/Benef%C3%ADcios+concedidos/JUN23-ABR24/DADOS+ABERTOS_CONCEDIDOS_AGOSTO+2023.xlsx) | [xlsx](https://armazenamento-dadosabertos.s3.sa-east-1.amazonaws.com/PDA_2023_2025/Grupos_de_dados/Benef%C3%ADcios+Indeferidos/UPDATED/INDEFERIDOS_DADOS_ABERTOS_AGOSTO+2023.xlsx) |
| Setembro/2023 | [xlsx](https://armazenamento-dadosabertos.s3.sa-east-1.amazonaws.com/PDA_2023_2025/Grupos_de_dados/Benef%C3%ADcios+concedidos/JUN23-ABR24/DADOS+ABERTOS_CONCEDIDOS_SETEMBRO+2023.xlsx) | [xlsx](https://armazenamento-dadosabertos.s3.sa-east-1.amazonaws.com/PDA_2023_2025/Grupos_de_dados/Benef%C3%ADcios+Indeferidos/UPDATED/INDEFERIDOS_DADOS_ABERTOS_SETEMBRO+2023.xlsx) |
| Outubro/2023 | [xlsx](https://armazenamento-dadosabertos.s3.sa-east-1.amazonaws.com/PDA_2023_2025/Grupos_de_dados/Benef%C3%ADcios+concedidos/JUN23-ABR24/DADOS+ABERTOS_CONCEDIDOS_OUTUBRO+2023.xlsx) | [xlsx](https://armazenamento-dadosabertos.s3.sa-east-1.amazonaws.com/PDA_2023_2025/Grupos_de_dados/Benef%C3%ADcios+Indeferidos/UPDATED/INDEFERIDOS_DADOS_ABERTOS_OUTUBRO+2023.xlsx) |
| Novembro/2023 | [xlsx](https://armazenamento-dadosabertos.s3.sa-east-1.amazonaws.com/PDA_2023_2025/Grupos_de_dados/Benef%C3%ADcios+concedidos/JUN23-ABR24/DADOS+ABERTOS_CONCEDIDOS_NOVEMBRO+2023.xlsx) | [xlsx](https://armazenamento-dadosabertos.s3.sa-east-1.amazonaws.com/PDA_2023_2025/Grupos_de_dados/Benef%C3%ADcios+Indeferidos/UPDATED/INDEFERIDOS_DADOS_ABERTOS_NOVEMBRO+2023.xlsx) |

Depois de baixar, importe (troque o caminho abaixo pelo local real onde o
arquivo baixado ficou salvo, ex. `C:\Downloads\DADOS ABERTOS_CONCEDIDOS_JULHO 2023.xlsx`):

```bash
uv run python manage.py ingest_pda "<caminho-do-arquivo-concedidos>.xlsx" --tipo concedido
uv run python manage.py ingest_pda "<caminho-do-arquivo-indeferidos>.xlsx" --tipo indeferido
uv run python manage.py runserver 8000
```

A API sobe em `http://localhost:8000/api/`, navegável (Browsable API do
DRF). `uv run python manage.py resumo` mostra um resumo rápido do que foi
importado (total e por mês), útil pra conferir a importação sem precisar do
shell interativo.

## Como rodar o frontend

Pré-requisitos: Node 18+.

```bash
cd frontend
npm install
npm run dev
```

Abre em `http://localhost:5173`. O Vite faz proxy de `/api` para
`http://127.0.0.1:8000` (ver `vite.config.ts`), então não precisa configurar
CORS nem URL da API pra rodar local, só o backend estar de pé.

## Endpoints da API

Os cinco primeiros aceitam os filtros opcionais
`?uf=PE&especie=41&competencia_inicio=2023-06-01&competencia_fim=2023-11-30`:

| Endpoint | Descrição |
|---|---|
| `GET /api/kpis/` | Totais gerais: concedidos, indeferidos, total, taxa de indeferimento, taxa de judicialização |
| `GET /api/serie-temporal/` | Concedidos x indeferidos por mês (+ taxa) |
| `GET /api/por-uf/` | Taxa de indeferimento por UF, da maior pra menor |
| `GET /api/por-especie/` | Taxa de indeferimento por espécie de benefício |
| `GET /api/motivos-indeferimento/` | Ranking dos 15 principais motivos de indeferimento |
| `GET /api/especies/` | Lista de espécies (popular filtro) |
| `GET /api/ufs/` | Lista das UFs presentes nos dados (popular filtro) |
| `GET /api/concessoes/`, `/api/indeferimentos/` | Listagem paginada "crua", mesmos filtros + `sexo`, `clientela` |

## Estrutura de pastas

```
Painel de Jurimetria Administrativa/
├── backend/
│   ├── config/                       # settings, urls, wsgi (projeto Django)
│   └── jurimetria/
│       ├── models.py                 # Especie, Concessao, Indeferimento
│       ├── serializers.py
│       ├── views.py                  # endpoints analíticos + viewsets de listagem
│       ├── filters.py
│       └── management/commands/
│           ├── ingest_pda.py         # importação dos XLSX reais do INSS
│           └── resumo.py             # utilitário de conferência pós-importação
└── frontend/
    └── src/
        ├── components/                # StatTile, KpiRow, FiltersBar, gráficos (Recharts)
        ├── hooks/useApiData.ts       # fetch + refetch reativo aos filtros
        └── lib/{api,formatacao,palette,transformacoes}.ts
```

## Limitações e próximos passos

- 6 meses de dado real importados (jun a nov/2023), não o período completo
  publicado (jun/2023 a jun/2025), decisão de escopo documentada acima.
- Sem testes automatizados: não coube no prazo do teste. Próximo passo
  natural seria `pytest-django` cobrindo o parser de `ingest_pda` (incluindo
  o caso de cabeçalho divergente do esperado) e os endpoints de agregação.
- Performance das views analíticas resolvida via cache em memória
  (`cache_page`); para o período completo, uma tabela de resumo
  pré-agregada por mês/UF/espécie seria o passo seguinte real, cache sozinho
  não reduz o custo da primeira consulta de cada combinação de filtro.
- SQLite é suficiente para o volume atual; para o histórico completo,
  trocar para Postgres é troca de `DATABASES` em `backend/config/settings.py`,
  já isolado para isso.
- Sem autenticação: o escopo do teste é leitura analítica, API é somente
  leitura (`ReadOnlyModelViewSet` + views baseadas em função só com `GET`).
- Painel de admin do Django não registrado, de propósito (ver comentário em
  `jurimetria/admin.py`): não haveria uso real num projeto só de leitura.
