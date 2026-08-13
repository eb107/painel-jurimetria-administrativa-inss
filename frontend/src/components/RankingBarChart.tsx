import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import { cores } from "../lib/palette"
import { truncarTexto } from "../lib/formatacao"

interface ItemRanking {
  rotulo: string
  valor: number
}

interface RankingBarChartProps {
  titulo: string
  descricao?: string
  dados: ItemRanking[]
  formatarValor: (valor: number) => string
  altura?: number
  truncarEm?: number
}

export default function RankingBarChart({
  titulo,
  descricao,
  dados,
  formatarValor,
  altura = 360,
  truncarEm = 28,
}: RankingBarChartProps) {
  return (
    <div className="rounded-lg border border-black/10 bg-[#fcfcfb] p-5">
      <h2 className="text-sm font-semibold text-[#0b0b0b]">{titulo}</h2>
      {descricao && <p className="mt-1 text-xs text-[#898781]">{descricao}</p>}
      <div className="mt-4" style={{ height: altura }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={dados} layout="vertical" margin={{ top: 8, right: 24, left: 8, bottom: 0 }}>
            <CartesianGrid stroke="#e1e0d9" horizontal={false} />
            <XAxis
              type="number"
              stroke="#c3c2b7"
              tick={{ fill: "#898781", fontSize: 12 }}
              tickFormatter={(valor) => formatarValor(Number(valor))}
            />
            <YAxis
              type="category"
              dataKey="rotulo"
              stroke="#c3c2b7"
              tick={{ fill: "#52514e", fontSize: 12 }}
              tickFormatter={(rotulo) => truncarTexto(String(rotulo), truncarEm)}
              width={200}
            />
            <Tooltip
              labelFormatter={(rotulo) => String(rotulo)}
              formatter={(valor) => formatarValor(Number(valor))}
              contentStyle={{
                borderRadius: 8,
                border: "1px solid rgba(11,11,11,0.10)",
                fontSize: 13,
                maxWidth: 320,
              }}
              labelStyle={{
                whiteSpace: "normal",
                wordBreak: "break-word",
                marginBottom: 4,
              }}
            />
            <Bar dataKey="valor" fill={cores.ranking} radius={[0, 4, 4, 0]} barSize={20} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}