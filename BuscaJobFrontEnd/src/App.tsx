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

  function onReset() {
    setVagas([])
    setInfo(null)
    setError(null)
    setPage(1)
  }

  const total = vagas.length
  const start = (page - 1) * pageSize
  const end = start + pageSize
  const pagedVagas = vagas.slice(start, end)

  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      <header className="bg-white shadow-sm border-b border-gray-100">
        <div className="mx-auto max-w-7xl px-4 py-6">
          <div className="flex items-center gap-3">
            <div className="bg-primary rounded-lg p-2 text-white">
              <span className="text-2xl">💼</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">BuscaJob</h1>
              <p className="text-sm text-gray-500">Encontre sua próxima oportunidade</p>
            </div>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-4 py-8">
        <div className="flex flex-col lg:flex-row gap-8">
          
          {/* Sidebar - Filtros */}
          <aside className="w-full lg:w-80 flex-shrink-0">
            <div className="sticky top-8">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Filtros</h2>
              <SearchForm onBuscar={onBuscar} onReset={onReset} />
            </div>
          </aside>

          {/* Main Content - Resultados */}
          <main className="flex-1 min-w-0">
            <div className="space-y-4">
              {loading && (
                <div className="rounded-xl border border-blue-100 bg-blue-50 px-4 py-3 text-blue-700 flex items-center gap-2">
                  <span className="animate-spin">⏳</span>
                  Carregando vagas...
                </div>
              )}
              {error && (
                <div className="rounded-xl border border-red-100 bg-red-50 px-4 py-3 text-red-700">
                  {error}
                </div>
              )}
              {info && (
                <div className="rounded-xl border border-green-100 bg-green-50 px-4 py-3 text-green-700">
                  {info}
                </div>
              )}

              <div className="bg-white rounded-xl border border-gray-200 p-4 flex flex-col sm:flex-row items-center justify-between gap-4 shadow-sm">
                <div className="text-gray-700">
                  Encontradas <span className="font-bold text-primary text-lg">{total}</span> vagas
                </div>
                <div className="flex items-center gap-3">
                  <label htmlFor="pageSize" className="text-sm text-gray-600 font-medium">Vagas por página:</label>
                  <select
                    id="pageSize"
                    className="rounded-lg border border-gray-300 bg-gray-50 px-3 py-1.5 text-sm font-medium text-gray-700 shadow-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary transition-shadow cursor-pointer hover:bg-white"
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
          </main>
        </div>
      </div>
    </div>
  )
}