import { useEffect, useState } from 'react'
import type { BuscarCriterios } from '../api/client'
import { getSites } from '../api/client'

const FALLBACK_SITES = [
  'linkedin','indeed','catho','glassdoor','vagas','infojobs','stackoverflow','github','trampos','rocket','startup'
]

export function SearchForm({ onBuscar, onReset }: { onBuscar: (c: BuscarCriterios) => void, onReset?: () => void }) {
  const [allSites, setAllSites] = useState<string[]>(FALLBACK_SITES)
  const [selectedSites, setSelectedSites] = useState<string[]>(FALLBACK_SITES)
  const cargoOptions = ['Analista de Sistemas','Analista de Negócios','Analista de Requisitos','Desenvolvedor','Backend','Frontend','QA','DevOps','Product Manager','Gerente de TI','Coordenador de TI']
  const localOptions = ['São Paulo','Belo Horizonte','Rio de Janeiro','Curitiba','Porto Alegre','Santa Catarina','Joinville','Jaraguá do Sul','Remoto','Híbrido']
  const [selectedCargos, setSelectedCargos] = useState<string[]>([cargoOptions[0]])
  const [selectedLocais, setSelectedLocais] = useState<string[]>([localOptions[0]])
  const modalidadeOptions = ['Home office','Presencial','Híbrido']
  const [selectedModalidades, setSelectedModalidades] = useState<string[]>(modalidadeOptions)

  function handleReset() {
    setSelectedCargos([cargoOptions[0]])
    setSelectedLocais([localOptions[0]])
    setSelectedModalidades(modalidadeOptions)
    setSelectedSites(allSites)
    if (onReset) onReset()
  }

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
      <form onSubmit={submit} className="flex flex-col gap-6">
        <div className="pb-4 border-b border-gray-100 mb-2">
          <button
            type="submit"
            className="w-full inline-flex items-center justify-center gap-2 rounded-md bg-primary px-4 py-3 text-white shadow-sm hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-primary font-medium transition-colors"
          >
            <span>🔎</span>
            <span>Buscar Vagas</span>
          </button>
          
          <button
            type="button"
            onClick={handleReset}
            className="mt-3 w-full inline-flex items-center justify-center gap-2 rounded-md border border-gray-300 bg-white px-4 py-2 text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary font-medium transition-colors"
          >
            <span>🗑️</span>
            <span>Resetar</span>
          </button>
        </div>
        <div className="grid gap-2">
          <div className="flex items-center justify-between gap-2">
            <label className="text-sm font-semibold text-gray-900">Cargo</label>
          </div>
          <div className="flex flex-col gap-2 max-h-60 overflow-y-auto pr-2 custom-scrollbar">
            <label className="inline-flex items-center gap-2 text-sm text-gray-700 hover:bg-gray-50 p-1 rounded cursor-pointer">
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
              <label key={opt} className="inline-flex items-center gap-2 text-sm text-gray-700 hover:bg-gray-50 p-1 rounded cursor-pointer">
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
        <div className="grid gap-2">
          <div className="flex items-center justify-between gap-2">
            <label className="text-sm font-semibold text-gray-900">Localização</label>
          </div>
          <div className="flex flex-col gap-2 max-h-60 overflow-y-auto pr-2 custom-scrollbar">
            <label className="inline-flex items-center gap-2 text-sm text-gray-700 hover:bg-gray-50 p-1 rounded cursor-pointer">
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
              <label key={opt} className="inline-flex items-center gap-2 text-sm text-gray-700 hover:bg-gray-50 p-1 rounded cursor-pointer">
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
        <div className="grid gap-2">
          <div className="flex items-center justify-between gap-2">
            <label className="text-sm font-semibold text-gray-900">Modalidade</label>
          </div>
          <div className="flex flex-col gap-2">
            <label className="inline-flex items-center gap-2 text-sm text-gray-700 hover:bg-gray-50 p-1 rounded cursor-pointer">
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
              <label key={opt} className="inline-flex items-center gap-2 text-sm text-gray-700 hover:bg-gray-50 p-1 rounded cursor-pointer">
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
        <div className="grid gap-2">
          <div className="flex items-center justify-between gap-2">
            <label className="text-sm font-semibold text-gray-900">Sites</label>
          </div>
          <div className="rounded-md border border-gray-200 bg-gray-50 p-3">
            <div className="flex flex-col gap-2 max-h-48 overflow-y-auto pr-1 custom-scrollbar">
              <label className="inline-flex items-center gap-2 text-sm text-gray-700 leading-tight hover:bg-gray-100 p-1 rounded cursor-pointer">
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
                  <label key={site} htmlFor={id} className="inline-flex items-center gap-2 text-sm text-gray-700 leading-tight hover:bg-gray-100 p-1 rounded cursor-pointer">
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
      </form>
    </div>
  )
}