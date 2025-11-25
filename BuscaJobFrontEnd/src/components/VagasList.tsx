import type { Vaga } from '../api/client'

function baseUrlForSite(site?: string): string | null {
  const s = (site || '').trim().toLowerCase()
  switch (s) {
    case 'indeed': return 'https://br.indeed.com'
    case 'catho': return 'https://www.catho.com.br'
    case 'vagas': return 'https://www.vagas.com.br'
    case 'vagas.com.br': return 'https://www.vagas.com.br'
    case 'linkedin': return 'https://www.linkedin.com'
    case 'glassdoor': return 'https://www.glassdoor.com.br'
    case 'infojobs': return 'https://www.infojobs.com.br'
    case 'stackoverflow': return 'https://stackoverflow.com'
    case 'stack overflow jobs': return 'https://stackoverflow.com'
    case 'github': return 'https://github.com'
    case 'github jobs': return 'https://github.com'
    case 'trampos': return 'https://trampos.co'
    case 'trampos.co': return 'https://trampos.co'
    case 'rocket': return 'https://rocketjobs.com.br'
    case 'rocket jobs': return 'https://rocketjobs.com.br'
    case 'startup': return 'https://startupjobs.com'
    case 'startup jobs': return 'https://startupjobs.com'
    default: return null
  }
}

function normalizeUrl(url?: string, site?: string): string | null {
  if (!url) return null
  let s = url.trim()
  if (!s) return null

  // Corrige casos comuns de protocolo sem dois-pontos: "http//" ou "https//"
  s = s.replace(/^(https?)(\/\/)/i, (_, proto) => `${proto}://`)

  // Se for caminho relativo, usa domínio base do site se disponível
  if(/^\/.+/.test(s)){
    const base = baseUrlForSite(site)
    if (base) {
      s = `${base}${s}`
    }
  }

  // Se não houver esquema e não parecer domínio (sem ponto), trata como relativo sem barra
  const hasScheme = /^[a-zA-Z][a-zA-Z0-9+.-]*:/.test(s)
  const looksLikeDomain = /^[a-z0-9.-]+\.[a-z]{2,}/i.test(s)
  if (!hasScheme && !looksLikeDomain) {
    const base = baseUrlForSite(site)
    if (base) {
      s = `${base.replace(/\/$/, '')}/${s.replace(/^\/+/, '')}`
    }
  }

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
  if (!hasScheme) {
    s = `https://${s.replace(/^\/+/, '')}`
  }

  try {
    const u2 = new URL(s)
    return u2.toString()
  } catch {
    return null
  }
}

function openExternal(url?: string, site?: string) {
  const finalUrl = normalizeUrl(url, site)
  if (!finalUrl) return
  try {
    window.open(finalUrl, '_blank', 'noopener,noreferrer')
  } catch (e) {
    console.error('Falha ao abrir link da vaga:', e)
  }
}

export function VagasList({ vagas }: { vagas: Vaga[] }) {
  if (!vagas?.length) {
    return <p className="text-gray-600">Nenhuma vaga para exibir.</p>
  }

  return (
    <div className="grid gap-5">
      {vagas.map((v, i) => {
        const normUrl = normalizeUrl(v.url, v.site)
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
              {v.modalidade && (
                <span className="inline-flex items-center rounded-full bg-gray-100 px-2 py-1 text-xs text-gray-700">🏠 {v.modalidade}</span>
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
              <button
                type="button"
                onClick={() => openExternal(v.url, v.site)}
                className="inline-flex items-center justify-center gap-2 rounded-md bg-primary px-3 py-2 text-white shadow-sm hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50"
                disabled={!normUrl}
                title={normUrl ? 'Abrir vaga em nova aba' : 'Link indisponível'}
              >
                <span>🔗</span>
                <span>Abrir Vaga</span>
              </button>
            </div>
          </div>
        )
      })}
    </div>
  )
}
