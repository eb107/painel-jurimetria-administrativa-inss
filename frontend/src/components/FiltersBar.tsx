import type { Especie, Filtros } from "../lib/api"

interface FiltersBarProps {
  filtros: Filtros
  ufs: string[]
  especies: Especie[]
  aoMudar: (filtros: Filtros) => void
}

export default function FiltersBar({ filtros, ufs, especies, aoMudar }: FiltersBarProps) {
  function mudarCompetenciaInicio(valor: string) {
    aoMudar({ ...filtros, competenciaInicio: valor || undefined })
  }

  function mudarCompetenciaFim(valor: string) {
    aoMudar({ ...filtros, competenciaFim: valor || undefined })
  }

  function mudarUf(valor: string) {
    aoMudar({ ...filtros, uf: valor || undefined })
  }

  function mudarEspecie(valor: string) {
    aoMudar({ ...filtros, especie: valor || undefined })
  }

  function limpar() {
    aoMudar({})
  }

  return (
    <div className="flex flex-wrap items-end gap-4 rounded-lg border border-black/10 bg-[#fcfcfb] p-4">
      <div className="flex flex-col gap-1">
        <label htmlFor="competencia-inicio" className="text-xs text-[#52514e]">
          Competência início
        </label>
        <input
          id="competencia-inicio"
          type="date"
          value={filtros.competenciaInicio ?? ""}
          onChange={(evento) => mudarCompetenciaInicio(evento.target.value)}
          className="rounded border border-[#c3c2b7] px-2 py-1 text-sm"
        />
      </div>

      <div className="flex flex-col gap-1">
        <label htmlFor="competencia-fim" className="text-xs text-[#52514e]">
          Competência fim
        </label>
        <input
          id="competencia-fim"
          type="date"
          value={filtros.competenciaFim ?? ""}
          onChange={(evento) => mudarCompetenciaFim(evento.target.value)}
          className="rounded border border-[#c3c2b7] px-2 py-1 text-sm"
        />
      </div>

      <div className="flex flex-col gap-1">
        <label htmlFor="uf" className="text-xs text-[#52514e]">
          UF
        </label>
        <select
          id="uf"
          value={filtros.uf ?? ""}
          onChange={(evento) => mudarUf(evento.target.value)}
          className="rounded border border-[#c3c2b7] px-2 py-1 text-sm"
        >
          <option value="">Todas</option>
          {ufs.map((uf) => (
            <option key={uf} value={uf}>
              {uf}
            </option>
          ))}
        </select>
      </div>

      <div className="flex flex-col gap-1">
        <label htmlFor="especie" className="text-xs text-[#52514e]">
          Espécie
        </label>
        <select
          id="especie"
          value={filtros.especie ?? ""}
          onChange={(evento) => mudarEspecie(evento.target.value)}
          className="max-w-[280px] rounded border border-[#c3c2b7] px-2 py-1 text-sm"
        >
          <option value="">Todas</option>
          {especies.map((especie) => (
            <option key={especie.id} value={especie.codigo}>
              {especie.codigo} - {especie.descricao}
            </option>
          ))}
        </select>
      </div>

      <button
        type="button"
        onClick={limpar}
        className="rounded border border-[#c3c2b7] px-3 py-1 text-sm text-[#52514e] hover:bg-black/5"
      >
        Limpar filtros
      </button>
    </div>
  )
}