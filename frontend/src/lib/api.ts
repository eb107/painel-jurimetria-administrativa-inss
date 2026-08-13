const BASE_URL = "/api"

export interface Filtros {
  uf?: string
  especie?: string
  competenciaInicio?: string
  competenciaFim?: string
}

export interface Kpis {
  total_concedidos: number
  total_indeferidos: number
  total_geral: number
  taxa_indeferimento: number
  total_concessoes_judiciais: number
  taxa_judicializacao: number
}

export interface PontoSerieTemporal {
  competencia: string
  concedidos: number
  indeferidos: number
  taxa_indeferimento: number
}

export interface PontoPorUf {
  uf: string
  concedidos: number
  indeferidos: number
  taxa_indeferimento: number
}

export interface PontoPorEspecie {
  especie_codigo: string
  especie_descricao: string
  concedidos: number
  indeferidos: number
  taxa_indeferimento: number
}

export interface MotivoIndeferimento {
  motivo: string
  total: number
  percentual: number
}

export interface Especie {
  id: number
  codigo: string
  descricao: string
}

export function construirQueryString(filtros: Filtros): string {
  const params = new URLSearchParams()
  if (filtros.uf) params.set("uf", filtros.uf)
  if (filtros.especie) params.set("especie", filtros.especie)
  if (filtros.competenciaInicio) params.set("competencia_inicio", filtros.competenciaInicio)
  if (filtros.competenciaFim) params.set("competencia_fim", filtros.competenciaFim)
  const query = params.toString()
  return query ? `?${query}` : ""
}

export function filtrosDaUrl(): Filtros {
  const params = new URLSearchParams(window.location.search)
  const filtros: Filtros = {}
  const uf = params.get("uf")
  const especie = params.get("especie")
  const competenciaInicio = params.get("competencia_inicio")
  const competenciaFim = params.get("competencia_fim")
  if (uf) filtros.uf = uf
  if (especie) filtros.especie = especie
  if (competenciaInicio) filtros.competenciaInicio = competenciaInicio
  if (competenciaFim) filtros.competenciaFim = competenciaFim
  return filtros
}

async function buscarJson<T>(caminho: string): Promise<T> {
  const resposta = await fetch(`${BASE_URL}${caminho}`)
  if (!resposta.ok) {
    throw new Error(`Erro ${resposta.status} ao buscar ${caminho}`)
  }
  return resposta.json() as Promise<T>
}

export function getKpis(filtros: Filtros): Promise<Kpis> {
  return buscarJson(`/kpis/${construirQueryString(filtros)}`)
}

export function getSerieTemporal(filtros: Filtros): Promise<PontoSerieTemporal[]> {
  return buscarJson(`/serie-temporal/${construirQueryString(filtros)}`)
}

export function getPorUf(filtros: Filtros): Promise<PontoPorUf[]> {
  return buscarJson(`/por-uf/${construirQueryString(filtros)}`)
}

export function getPorEspecie(filtros: Filtros): Promise<PontoPorEspecie[]> {
  return buscarJson(`/por-especie/${construirQueryString(filtros)}`)
}

export function getMotivosIndeferimento(filtros: Filtros): Promise<MotivoIndeferimento[]> {
  return buscarJson(`/motivos-indeferimento/${construirQueryString(filtros)}`)
}

export function getEspecies(): Promise<Especie[]> {
  return buscarJson("/especies/")
}

export function getUfs(): Promise<string[]> {
  return buscarJson("/ufs/")
}