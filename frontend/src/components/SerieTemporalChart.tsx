import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { PontoSerieTemporal } from "../lib/api";
import { cores } from "../lib/palette";
import { formatCompetencia, formatInteiro } from "../lib/formatacao";

interface SerieTemporalChartProps {
  dados: PontoSerieTemporal[];
}

export default function SerieTemporalChart({ dados }: SerieTemporalChartProps) {
  return (
    <div className="rounded-lg border border-black/10 bg-[#fcfcfb] p-5">
      <h2 className="text-sm font-semibold text-[#0b0b0b]">
        Concedidos x indeferidos por mês
      </h2>
      <div className="mt-4 h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={dados}
            margin={{ top: 8, right: 16, left: 0, bottom: 0 }}
          >
            <CartesianGrid stroke="#e1e0d9" vertical={false} />
            <XAxis
              dataKey="competencia"
              tickFormatter={formatCompetencia}
              stroke="#c3c2b7"
              tick={{ fill: "#898781", fontSize: 12 }}
            />
            <YAxis
              stroke="#c3c2b7"
              tick={{ fill: "#898781", fontSize: 12 }}
              tickFormatter={(valor: number) => formatInteiro(valor)}
            />
            <Tooltip
              labelFormatter={(label) => formatCompetencia(String(label))}
              formatter={(valor) => formatInteiro(Number(valor))}
              contentStyle={{
                borderRadius: 8,
                border: "1px solid rgba(11,11,11,0.10)",
                fontSize: 13,
              }}
            />
            <Legend wrapperStyle={{ fontSize: 13, color: "#52514e" }} />
            <Line
              type="monotone"
              dataKey="concedidos"
              name="Concedidos"
              stroke={cores.concedidos}
              strokeWidth={2}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
            />
            <Line
              type="monotone"
              dataKey="indeferidos"
              name="Indeferidos"
              stroke={cores.indeferidos}
              strokeWidth={2}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
