interface StatusCardProps {
  title: string
  value: string | number
  icon?: React.ReactNode
  status?: 'idle' | 'loading' | 'success' | 'error'
}

export function StatusCard({ title, value, icon, status }: StatusCardProps) {
  const statusColors = {
    idle: 'bg-muted',
    loading: 'bg-yellow-500/10 text-yellow-400',
    success: 'bg-status-loaded/10 text-status-loaded',
    error: 'bg-destructive/10 text-destructive',
  }

  return (
    <div className="bg-card border border-border rounded-lg p-6">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-muted-foreground mb-1">{title}</p>
          <p className="text-2xl font-bold text-foreground">{value}</p>
        </div>
        {icon && <div className="text-primary">{icon}</div>}
      </div>
      {status && (
        <div className={`mt-4 text-xs font-medium px-3 py-1 rounded-full w-fit ${statusColors[status]}`}>
          {status === 'idle' && 'Not Started'}
          {status === 'loading' && 'Processing...'}
          {status === 'success' && 'Complete'}
          {status === 'error' && 'Error'}
        </div>
      )}
    </div>
  )
}
