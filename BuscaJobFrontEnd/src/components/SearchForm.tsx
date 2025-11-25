import { useEffect, useState } from 'react'
import type { BuscarCriterios } from '../api/client'
import { getSites } from '../api/client'

const FALLBACK_SITES = [
  'linkedin','indeed','catho','glassdoor','vagas','infojobs','stackoverflow','github','trampos','rocket','startup'
]

export function SearchForm({ onBuscar }: { onBuscar: (c: BuscarCriterios) => void }) {
  const [allSites, setAllSites] = useState<string[]>(FALLBACK_SITES)
  const [selectedSites, setSelectedSites] = useState<string[]>(FALLBACK_SITES)
  const cargoOptions = ['Analista de Sistemas','Desenvolvedor','Backend','Frontend','QA','DevOps','Product Manager']
  const localOptions = ['São Paulo','Belo Horizonte','Rio de Janeiro','Curitiba','Porto Alegre','Remoto','Híbrido']
  const [selectedCargos, setSelectedCargos] = useState<string[]>([cargoOptions[0]])
  const [selectedLocais, setSelectedLocais] = useState<string[]>([localOptions[0]])
  const modalidadeOptions = ['Home office','Presencial','Híbrido']
  const [selectedModalidades, setSelectedModalidades] = useState<string[]>(modalidadeOptions)

  useEffect(() => {
    ;(async () => {
      try {
        const sites = await getSites()
        if (sites.length) {
          setAllSites(sites)
          setSelectedSites(sites)
        }
      } catch {
        // Mantém fallback em caso de erro
      }
    })()
  }, [])

  function submit(e: React.FormEvent) {
    e.preventDefault()
    const cargoSel = selectedCargos[0] ?? cargoOptions[0]
    const localSel = selectedLocais[0] ?? localOptions[0]
    const criterios: BuscarCriterios = { cargo: cargoSel, localizacao: localSel, sites: selectedSites, tipos_contratacao: ['CLT', 'PJ'] }
    // Só envia modalidades se não estiverem todas selecionadas (para não reduzir resultados por falta de inferência)
    if (selectedModalidades.length && selectedModalidades.length < modalidadeOptions.length) {
      criterios.modalidades = selectedModalidades
    }
    onBuscar(criterios)
  }

  function toggleSite(site: string) {
    setSelectedSites(prev => {
      if (prev.includes(site)) {
        return prev.filter(s => s !== site)
      }
      return [...prev, site]
    })
  }

  function selectAll() {
    setSelectedSites(allSites)
  }

  function clearAll() {
    setSelectedSites([])
  }

  const allSelected = allSites.length > 0 && selectedSites.length === allSites.length
  const allCargosSelected = cargoOptions.length > 0 && selectedCargos.length === cargoOptions.length
  const allLocaisSelected = localOptions.length > 0 && selectedLocais.length === localOptions.length
  const allModalidadesSelected = selectedModalidades.length === modalidadeOptions.length

  function toggleCargoOption(opt: string) {
    setSelectedCargos(prev => (
      prev.includes(opt) ? prev.filter(s => s !== opt) : [...prev, opt]
    ))
  }

  function selectAllCargos() { setSelectedCargos(cargoOptions) }
  function clearCargos() { setSelectedCargos([]) }

  function toggleLocalOption(opt: string) {
    setSelectedLocais(prev => (
      prev.includes(opt) ? prev.filter(s => s !== opt) : [...prev, opt]
    ))
  }

  function selectAllLocais() { setSelectedLocais(localOptions) }
  function clearLocais() { setSelectedLocais([]) }

  function toggleModalidadeOption(opt: string) {
    setSelectedModalidades(prev => (
      prev.includes(opt) ? prev.filter(s => s !== opt) : [...prev, opt]
    ))
  }
  function selectAllModalidades() { setSelectedModalidades(modalidadeOptions) }
  function clearModalidades() { setSelectedModalidades([]) }

  return (
    <div className="mb-6 rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
      <form onSubmit={submit} className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <div className="md:col-span-2 lg:col-span-3 grid gap-1">
          <div className="flex items-center justify-between gap-2">
            <label className="text-xs font-medium text-gray-700">Cargo</label>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2">
            <label className="inline-flex items-center gap-2 text-xs text-gray-700">
              <input
                type="checkbox"
                className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                checked={allCargosSelected}
                onChange={(e) => (e.target.checked ? selectAllCargos() : clearCargos())}
                disabled={cargoOptions.length === 0}
              />
              <span>Todos</span>
            </label>
            {cargoOptions.map(opt => (
              <label key={opt} className="inline-flex items-center gap-2 text-xs text-gray-700">
                <input
                  type="checkbox"
                  className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                  checked={selectedCargos.includes(opt)}
                  onChange={() => toggleCargoOption(opt)}
                />
                <span>{opt}</span>
              </label>
            ))}
          </div>
        </div>
        <div className="md:col-span-2 lg:col-span-3 grid gap-1">
          <div className="flex items-center justify-between gap-2">
            <label className="text-xs font-medium text-gray-700">Localização</label>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2">
            <label className="inline-flex items-center gap-2 text-xs text-gray-700">
              <input
                type="checkbox"
                className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                checked={allLocaisSelected}
                onChange={(e) => (e.target.checked ? selectAllLocais() : clearLocais())}
                disabled={localOptions.length === 0}
              />
              <span>Todos</span>
            </label>
            {localOptions.map(opt => (
              <label key={opt} className="inline-flex items-center gap-2 text-xs text-gray-700">
                <input
                  type="checkbox"
                  className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                  checked={selectedLocais.includes(opt)}
                  onChange={() => toggleLocalOption(opt)}
                />
                <span>{opt}</span>
              </label>
            ))}
          </div>
        </div>
        <div className="md:col-span-2 lg:col-span-3 grid gap-1">
          <div className="flex items-center justify-between gap-2">
            <label className="text-xs font-medium text-gray-700">Modalidade</label>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2">
            <label className="inline-flex items-center gap-2 text-xs text-gray-700">
              <input
                type="checkbox"
                className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                checked={allModalidadesSelected}
                onChange={(e) => (e.target.checked ? selectAllModalidades() : clearModalidades())}
                disabled={modalidadeOptions.length === 0}
              />
              <span>Todos</span>
            </label>
            {modalidadeOptions.map(opt => (
              <label key={opt} className="inline-flex items-center gap-2 text-xs text-gray-700">
                <input
                  type="checkbox"
                  className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                  checked={selectedModalidades.includes(opt)}
                  onChange={() => toggleModalidadeOption(opt)}
                />
                <span>{opt}</span>
              </label>
            ))}
          </div>
        </div>
        <div className="md:col-span-2 lg:col-span-3 grid gap-2">
          <div className="flex items-center justify-between gap-2">
            <label className="text-xs font-medium text-gray-700">Sites</label>
          </div>
          <div className="rounded-md border border-gray-200 bg-gray-50 p-3">
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2 max-h-32 overflow-auto pr-1">
              <label className="inline-flex items-center gap-2 text-xs text-gray-700 leading-tight">
                <input
                  type="checkbox"
                  className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                  checked={allSelected}
                  onChange={(e) => (e.target.checked ? selectAll() : clearAll())}
                  disabled={allSites.length === 0}
                />
                <span className="capitalize">Todos</span>
              </label>
              {allSites.map(site => {
                const id = `site-${site}`
                const checked = selectedSites.includes(site)
                return (
                  <label key={site} htmlFor={id} className="inline-flex items-center gap-2 text-xs text-gray-700 leading-tight">
                    <input
                      id={id}
                      type="checkbox"
                      className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                      checked={checked}
                      onChange={() => toggleSite(site)}
                    />
                    <span className="capitalize">{site}</span>
                  </label>
                )
              })}
            </div>
          </div>
        </div>
        <div className="md:col-span-2 lg:col-span-3 flex justify-end">
          <button
            type="submit"
            className="inline-flex items-center justify-center gap-2 rounded-md bg-primary px-4 py-2 text-white shadow-sm hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <span>🔎</span>
            <span>Buscar</span>
          </button>
        </div>
      </form>
    </div>
  )
}
