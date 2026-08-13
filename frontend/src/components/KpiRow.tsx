import type { Kpis } from "../lib/api"
import { formatInteiro, formatPercentual } from "../lib/formatacao"
import StatTile from "./StatTile"

interface KpiRowProps {
  kpis: Kpis | null
  carregando: boolean
}

export default function KpiRow({ kpis, carregando }: KpiRowProps) {
  return (
    <div
      className={`grid grid-cols-1 gap-4 transition-opacity duration-200 sm:grid-cols-2 lg:grid-cols-4 ${
        carregando ? "opacity-60" : "opacity-100"
      }`}
    >
      <StatTile rotulo="Concedidos" valor={kpis ? formatInteiro(kpis.total_concedidos) : "—"} />
      <StatTile rotulo="Indeferidos" valor={kpis ? formatInteiro(kpis.total_indeferidos) : "—"} />
      <StatTile rotulo="Total geral" valor={kpis ? formatInteiro(kpis.total_geral) : "—"} />
      <StatTile rotulo="Taxa de indeferimento" valor={kpis ? formatPercentual(kpis.taxa_indeferimento) : "—"} />
    </div>
  )
}