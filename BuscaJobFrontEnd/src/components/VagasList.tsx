import type { Vaga } from '../api/client'

function normalizeUrl(url?: string): string | null {
  if (!url) return null
  let s = url.trim()
  if (!s) return null

  // Corrige casos comuns de protocolo sem dois-pontos: "http//" ou "https//"
  s = s.replace(/^(https?)(\/\/)/i, (_, proto) => `${proto}://`)

  // Se já for uma URL válida com protocolo, retorna normalizada
  try {
    const u = new URL(s)
    return u.toString()
  } catch {}

  // Adiciona https:// quando iniciar com www.
  if (/^www\./i.test(s)) {
    s = `https://${s}`
  }

  // Se ainda não tiver esquema, prefixa https:// e remove barras iniciais extras
  if (!/^[a-zA-Z][a-zA-Z0-9+.-]*:/.test(s)) {
    s = `https://${s.replace(/^\/+/, '')}`
  }

  try {
    const u2 = new URL(s)
    return u2.toString()
  } catch {
    return null
  }
}

export function VagasList({ vagas }: { vagas: Vaga[] }) {
  if (!vagas?.length) {
    return <p className="text-gray-600">Nenhuma vaga para exibir.</p>
  }

  return (
    <div className="grid gap-5">
      {vagas.map((v, i) => {
        const normUrl = normalizeUrl(v.url)
        const key = v.id ?? `${v.titulo}-${v.empresa}-${i}`
        return (
          <div key={key} className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm transition hover:shadow-lg hover:border-primary">
            <div className="flex items-start justify-between">
              <strong className="text-xl text-gray-900">{v.titulo}</strong>
              <span className="text-sm text-gray-600">{v.empresa}</span>
            </div>

            <div className="mt-3 flex flex-wrap gap-2">
              {v.localizacao && (
                <span className="inline-flex items-center rounded-full bg-gray-100 px-2 py-1 text-xs text-gray-700">📍 {v.localizacao}</span>
              )}
              {v.salario && (
                <span className="inline-flex items-center rounded-full bg-gray-100 px-2 py-1 text-xs text-gray-700">💰 {v.salario}</span>
              )}
              {v.site && (
                <span className="inline-flex items-center rounded-full bg-gray-100 px-2 py-1 text-xs text-gray-700">🌐 {v.site}</span>
              )}
              {v.dataPublicacao && (
                <span className="inline-flex items-center rounded-full bg-gray-100 px-2 py-1 text-xs text-gray-700">🗓️ {v.dataPublicacao}</span>
              )}
              {v.tipo && (
                <span className="inline-flex items-center rounded-full bg-gray-100 px-2 py-1 text-xs text-gray-700">📄 {v.tipo}</span>
              )}
              {v.nivel && (
                <span className="inline-flex items-center rounded-full bg-gray-100 px-2 py-1 text-xs text-gray-700">🎯 {v.nivel}</span>
              )}
            </div>

            {v.descricao && <p className="mt-3 text-sm text-gray-700">{v.descricao}</p>}

            <div className="mt-4">
              {normUrl ? (
                <a
                  href={normUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center justify-center gap-2 rounded-md bg-primary px-3 py-2 text-white shadow-sm hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-primary"
                  title="Abrir vaga em nova aba"
                >
                  <span>🔗</span>
                  <span>Abrir Vaga</span>
                </a>
              ) : (
                <button
                  type="button"
                  className="inline-flex items-center justify-center gap-2 rounded-md bg-primary px-3 py-2 text-white shadow-sm focus:outline-none disabled:opacity-50 cursor-not-allowed"
                  disabled
                  title="Link indisponível"
                >
                  <span>🔗</span>
                  <span>Abrir Vaga</span>
                </button>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}