import type { MotivoIndeferimento, PontoPorEspecie, PontoPorUf } from "./api"

const VOLUME_MINIMO_ESPECIE = 1000

export function transformarPorUf(dados: PontoPorUf[]) {
  return [...dados]
    .sort((a, b) => b.taxa_indeferimento - a.taxa_indeferimento)
    .map((item) => ({ rotulo: item.uf, valor: item.taxa_indeferimento }))
}

export function transformarPorEspecie(dados: PontoPorEspecie[]) {
  return dados
    .filter((item) => item.concedidos + item.indeferidos >= VOLUME_MINIMO_ESPECIE)
    .sort((a, b) => b.taxa_indeferimento - a.taxa_indeferimento)
    .map((item) => ({ rotulo: item.especie_descricao, valor: item.taxa_indeferimento }))
}

export function transformarMotivos(dados: MotivoIndeferimento[]) {
  return [...dados]
    .sort((a, b) => b.total - a.total)
    .map((item) => ({ rotulo: item.motivo, valor: item.total }))
}