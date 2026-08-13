import { formatInteiro, formatPercentual } from "../lib/formatacao"

interface JudicializacaoCardProps {
  totalJudicial: number
  taxa: number
  carregando: boolean
}

export default function JudicializacaoCard({ totalJudicial, taxa, carregando }: JudicializacaoCardProps) {
  return (
    <div
      className={`rounded-lg border-l-4 border-[#2a78d6] bg-[#fcfcfb] p-5 transition-opacity duration-200 ${
        carregando ? "opacity-60" : "opacity-100"
      }`}
    >
      <p className="text-sm text-[#52514e]">Concessões que só saíram após ação judicial</p>
      <p className="mt-1 text-3xl font-semibold text-[#0b0b0b]">
        {formatPercentual(taxa)}
        <span className="ml-2 text-base font-normal text-[#52514e]">
          ({formatInteiro(totalJudicial)} casos no período)
        </span>
      </p>
      <p className="mt-2 text-xs text-[#898781]">
        Percentual das concessões cujo despacho foi "Concessão Decorrente de Ação Judicial", ou seja, o INSS só
        concedeu depois que o segurado precisou recorrer à Justiça.
      </p>
    </div>
  )
}