import { useEffect, useState } from 'react'
import { getUltimoResultado, buscarVagas, type Vaga, type BuscarCriterios } from './api/client'
import { SearchForm } from './components/SearchForm'
import { VagasList } from './components/VagasList'
import { Pagination } from './components/Pagination'

export default function App() {
  const [vagas, setVagas] = useState<Vaga[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [info, setInfo] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)

  useEffect(() => {
    ;(async () => {
      setLoading(true)
      setError(null)
      try {
        const data = await getUltimoResultado()
        setVagas(data.vagas ?? [])
        setInfo(data.arquivo ? `Carregado ${data.arquivo}` : null)
        setPage(1)
      } catch (e: any) {
        setError(e?.message || 'Erro ao carregar último resultado')
      } finally {
        setLoading(false)
      }
    })()
  }, [])

  async function onBuscar(criterios: BuscarCriterios) {
    setLoading(true)
    setError(null)
    setInfo(null)
    try {
      const data = await buscarVagas(criterios)
      setVagas(data.vagas ?? [])
      setInfo(`Encontradas ${data.total_vagas ?? data.total ?? (data.vagas?.length ?? 0)} vagas`)
      setPage(1)
    } catch (e: any) {
      setError(e?.message || 'Erro ao buscar vagas')
    } finally {
      setLoading(false)
    }
  }

  const total = vagas.length
  const start = (page - 1) * pageSize
  const end = start + pageSize
  const pagedVagas = vagas.slice(start, end)

  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      <div className="mx-auto max-w-5xl px-4 py-8">
        <header className="mb-8">
          <div className="rounded-xl bg-gradient-to-r from-primary to-primary-dark p-6 text-white shadow-sm">
            <h1 className="text-3xl font-bold">BuscaJob</h1>
            <p className="mt-1 text-sm opacity-90">Busca simples e lista de vagas via API</p>
          </div>
        </header>

        <SearchForm onBuscar={onBuscar} />

        <div className="space-y-2 my-3">
          {loading && (
            <div className="rounded-md border border-blue-200 bg-blue-50 px-3 py-2 text-blue-700">
              Carregando...
            </div>
          )}
          {error && (
            <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-red-700">
              {error}
            </div>
          )}
          {info && (
            <div className="rounded-md border border-green-200 bg-green-50 px-3 py-2 text-green-700">
              {info}
            </div>
          )}
        </div>

        <div className="mb-4 flex items-center justify-between">
          <div className="text-sm text-gray-700">Total: <span className="font-medium">{total}</span> vagas</div>
          <div className="flex items-center gap-2">
            <label htmlFor="pageSize" className="text-sm text-gray-700">Itens por página</label>
            <select
              id="pageSize"
              className="rounded-md border border-gray-300 px-2 py-1 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-primary"
              value={pageSize}
              onChange={e => { setPageSize(Number(e.target.value)); setPage(1) }}
            >
              {[5, 10, 20, 50].map(n => <option key={n} value={n}>{n}</option>)}
            </select>
          </div>
        </div>

        <VagasList vagas={pagedVagas} />

        <Pagination
          currentPage={page}
          totalItems={total}
          pageSize={pageSize}
          onPageChange={setPage}
        />
      </div>
    </div>
  )
}