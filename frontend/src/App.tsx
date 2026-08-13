import { useEffect, useState } from "react"
import { construirQueryString, filtrosDaUrl, type Filtros } from "./lib/api"
import { useApiData, useOpcoesFiltro } from "./hooks/useApiData"
import { transformarMotivos, transformarPorEspecie, transformarPorUf } from "./lib/transformacoes"
import { formatInteiro, formatPercentual } from "./lib/formatacao"
import FiltersBar from "./components/FiltersBar"
import KpiRow from "./components/KpiRow"
import SerieTemporalChart from "./components/SerieTemporalChart"
import RankingBarChart from "./components/RankingBarChart"
import JudicializacaoCard from "./components/JudicializacaoCard"

function App() {
  const [filtros, setFiltros] = useState<Filtros>(filtrosDaUrl)
  const { kpis, serieTemporal, porUf, porEspecie, motivosIndeferimento, carregando, erro } =
    useApiData(filtros)
  const { especies, ufs } = useOpcoesFiltro()

  // Sincroniza os filtros com a URL (sobrevive a F5 e da pra compartilhar o
  // link já filtrado). Usa replaceState, não pushState, de propósito: senão
  // cada ajuste de filtro criaria uma entrada nova no histórico do navegador
  // e o botão "voltar" ficaria desfazendo filtro por filtro em vez de sair da página.
  useEffect(() => {
    const query = construirQueryString(filtros)
    const novaUrl = query ? `${window.location.pathname}${query}` : window.location.pathname
    window.history.replaceState(null, "", novaUrl)
  }, [filtros.uf, filtros.especie, filtros.competenciaInicio, filtros.competenciaFim])

  return (
    <div className="min-h-screen bg-[#f9f9f7] px-6 py-8">
      <div className="mx-auto flex max-w-6xl flex-col gap-6">
        <header>
          <h1 className="text-2xl font-semibold text-[#0b0b0b]">
            Painel de Jurimetria Administrativa
          </h1>
          <p className="text-sm text-[#52514e]">
            Concessão e indeferimento de benefícios do INSS, jun a nov/2023
          </p>
        </header>

        <FiltersBar filtros={filtros} ufs={ufs} especies={especies} aoMudar={setFiltros} />

        {erro && (
          <p className="rounded-lg border border-[#e34948]/30 bg-[#e34948]/5 p-3 text-sm text-[#e34948]">
            Não foi possível carregar os dados: {erro}
          </p>
        )}

        <KpiRow kpis={kpis} carregando={carregando} />

        <JudicializacaoCard
          totalJudicial={kpis?.total_concessoes_judiciais ?? 0}
          taxa={kpis?.taxa_judicializacao ?? 0}
          carregando={carregando}
        />

        <SerieTemporalChart dados={serieTemporal} />

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <RankingBarChart
            titulo="Taxa de indeferimento por UF"
            descricao="Estados onde o INSS mais nega pedido de benefício, proporcionalmente ao volume analisado em cada um."
            dados={transformarPorUf(porUf)}
            formatarValor={formatPercentual}
          />
          <RankingBarChart
            titulo="Taxa de indeferimento por espécie (volume ≥ 1.000 casos)"
            descricao="Tipos de benefício com maior chance de indeferimento. Espécies com menos de 1.000 casos no período ficam de fora, pra taxa não distorcer com volume pequeno."
            dados={transformarPorEspecie(porEspecie)}
            formatarValor={formatPercentual}
          />
        </div>

        <RankingBarChart
          titulo="Principais motivos de indeferimento"
          descricao="Razões mais citadas pelo INSS para negar um pedido, considerando o período e os filtros selecionados."
          dados={transformarMotivos(motivosIndeferimento)}
          formatarValor={formatInteiro}
          altura={520}
        />
      </div>
    </div>
  )
}

export default App