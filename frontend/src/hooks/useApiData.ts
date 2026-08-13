import { useEffect, useState } from "react"
import {
  type Filtros,
  type Kpis,
  type PontoSerieTemporal,
  type PontoPorUf,
  type PontoPorEspecie,
  type MotivoIndeferimento,
  type Especie,
  getKpis,
  getSerieTemporal,
  getPorUf,
  getPorEspecie,
  getMotivosIndeferimento,
  getEspecies,
  getUfs,
} from "../lib/api"

interface DadosPainel {
  kpis: Kpis | null
  serieTemporal: PontoSerieTemporal[]
  porUf: PontoPorUf[]
  porEspecie: PontoPorEspecie[]
  motivosIndeferimento: MotivoIndeferimento[]
  carregando: boolean
  erro: string | null
}

export function useApiData(filtros: Filtros): DadosPainel {
  const [kpis, setKpis] = useState<Kpis | null>(null)
  const [serieTemporal, setSerieTemporal] = useState<PontoSerieTemporal[]>([])
  const [porUf, setPorUf] = useState<PontoPorUf[]>([])
  const [porEspecie, setPorEspecie] = useState<PontoPorEspecie[]>([])
  const [motivosIndeferimento, setMotivosIndeferimento] = useState<MotivoIndeferimento[]>([])
  const [carregando, setCarregando] = useState(true)
  const [erro, setErro] = useState<string | null>(null)

  useEffect(() => {
    let cancelado = false

    async function carregar() {
      setCarregando(true)
      setErro(null)
      try {
        const [kpisResp, serieResp, ufResp, especieResp, motivosResp] = await Promise.all([
          getKpis(filtros),
          getSerieTemporal(filtros),
          getPorUf(filtros),
          getPorEspecie(filtros),
          getMotivosIndeferimento(filtros),
        ])

        if (cancelado) return

        setKpis(kpisResp)
        setSerieTemporal(serieResp)
        setPorUf(ufResp)
        setPorEspecie(especieResp)
        setMotivosIndeferimento(motivosResp)
      } catch (erroCapturado) {
        if (cancelado) return
        setErro(erroCapturado instanceof Error ? erroCapturado.message : "Erro desconhecido")
      } finally {
        if (!cancelado) setCarregando(false)
      }
    }

    carregar()

    return () => {
      cancelado = true
    }
    // Depende dos quatro campos individualmente, não do objeto `filtros`
    // inteiro: se o componente que chama esse hook recriar o objeto a cada
    // render (`useApiData({ uf })`), a referência muda mesmo com os mesmos
    // valores, e usar [filtros] aqui causaria um loop infinito de refetch.
  }, [filtros.uf, filtros.especie, filtros.competenciaInicio, filtros.competenciaFim])

  return { kpis, serieTemporal, porUf, porEspecie, motivosIndeferimento, carregando, erro }
}

export function useOpcoesFiltro() {
  const [especies, setEspecies] = useState<Especie[]>([])
  const [ufs, setUfs] = useState<string[]>([])

  useEffect(() => {
    getEspecies().then(setEspecies).catch(() => {})
    getUfs().then(setUfs).catch(() => {})
  }, [])

  return { especies, ufs }
}