export function formatInteiro(valor: number): string {
  return valor.toLocaleString("pt-BR")
}

export function formatPercentual(valor: number): string {
  return `${valor.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}%`
}

export function formatCompetencia(competencia: string): string {
  const [ano, mes] = competencia.split("-")
  const data = new Date(Number(ano), Number(mes) - 1, 1)
  return data.toLocaleDateString("pt-BR", { month: "short", year: "2-digit" })
}

export function truncarTexto(texto: string, tamanho: number): string {
  return texto.length > tamanho ? `${texto.slice(0, tamanho).trimEnd()}…` : texto
}