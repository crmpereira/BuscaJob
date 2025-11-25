import axios from 'axios'

export interface Vaga {
  id?: string
  titulo: string
  empresa: string
  localizacao: string
  salario?: string
  descricao?: string
  dataPublicacao?: string
  site?: string
  url?: string
  tipo?: string
  nivel?: string
  modalidade?: string
}

export interface BuscarCriterios {
  cargo: string
  localizacao?: string
  sites?: string[]
  tipos_contratacao?: string[]
  modalidades?: string[]
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

export async function getUltimoResultado(): Promise<{ vagas: Vaga[]; total?: number; arquivo?: string }> {
  try {
    const { data } = await axios.get(`${API_URL}/api/ultimo-resultado`)
    return data
  } catch (e: any) {
    const status = e?.response?.status
    if (status === 404) {
      // Sem arquivo de resultados ainda: retorna vazio para não quebrar a UI
      return { vagas: [], total: 0 }
    }
    const msg = e?.response?.data?.error || e?.message || 'Falha ao carregar último resultado'
    throw new Error(msg)
  }
}

export async function buscarVagas(criterios: BuscarCriterios): Promise<{ vagas: Vaga[]; total_vagas?: number; total?: number }> {
  const { data } = await axios.post(`${API_URL}/api/buscar-vagas`, criterios)
  return data
}

export async function getSites(): Promise<string[]> {
  const { data } = await axios.get(`${API_URL}/api/sites`)
  const sites = Array.isArray(data?.sites) ? data.sites : []
  return sites
}
