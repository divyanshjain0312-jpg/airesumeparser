interface StatusBadgeProps {
  status: 'loaded' | 'parsed' | 'chunked' | 'embedded' | 'stored' | 'retrieved' | 'generated'
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const statusConfig = {
    loaded: { bg: 'bg-status-loaded/20', text: 'text-status-loaded', label: 'Loaded' },
    parsed: { bg: 'bg-status-parsed/20', text: 'text-status-parsed', label: 'Parsed' },
    chunked: { bg: 'bg-status-chunked/20', text: 'text-status-chunked', label: 'Chunked' },
    embedded: { bg: 'bg-status-embedded/20', text: 'text-status-embedded', label: 'Embedded' },
    stored: { bg: 'bg-status-stored/20', text: 'text-status-stored', label: 'Stored' },
    retrieved: { bg: 'bg-status-retrieved/20', text: 'text-status-retrieved', label: 'Retrieved' },
    generated: { bg: 'bg-status-generated/20', text: 'text-status-generated', label: 'Generated' },
  }

  const config = statusConfig[status]

  return (
    <span className={`inline-block px-3 py-1 text-xs font-semibold rounded-full ${config.bg} ${config.text}`}>
      {config.label}
    </span>
  )
}
