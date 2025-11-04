interface PaginationProps {
  currentPage: number
  totalItems: number
  pageSize: number
  onPageChange: (page: number) => void
}

export function Pagination({ currentPage, totalItems, pageSize, onPageChange }: PaginationProps) {
  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize))

  function goTo(page: number) {
    const p = Math.min(Math.max(1, page), totalPages)
    if (p !== currentPage) onPageChange(p)
  }

  return (
    <div className="mt-6 flex items-center justify-between">
      <div className="text-sm text-gray-600">
        Página <span className="font-medium text-gray-900">{currentPage}</span> de{' '}
        <span className="font-medium text-gray-900">{totalPages}</span>
      </div>
      <div className="flex items-center gap-2">
        <button
          type="button"
          className="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm text-gray-700 shadow-sm hover:bg-gray-50 disabled:opacity-50"
          onClick={() => goTo(currentPage - 1)}
          disabled={currentPage <= 1}
        >
          ‹ Anterior
        </button>
        <button
          type="button"
          className="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm text-gray-700 shadow-sm hover:bg-gray-50 disabled:opacity-50"
          onClick={() => goTo(currentPage + 1)}
          disabled={currentPage >= totalPages}
        >
          Próxima ›
        </button>
      </div>
    </div>
  )
}