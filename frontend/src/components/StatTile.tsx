interface StatTileProps {
  rotulo: string
  valor: string
}

export default function StatTile({ rotulo, valor }: StatTileProps) {
  return (
    <div className="rounded-lg border border-black/10 bg-[#fcfcfb] p-5">
      <p className="text-sm text-[#52514e]">{rotulo}</p>
      <p className="mt-1 text-3xl font-semibold text-[#0b0b0b]">{valor}</p>
    </div>
  )
}