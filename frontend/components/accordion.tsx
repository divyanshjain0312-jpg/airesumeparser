'use client'

import { useState } from 'react'
import { ChevronDown } from 'lucide-react'

interface AccordionItem {
  id: string
  title: string
  content: React.ReactNode
  badge?: React.ReactNode
}

interface AccordionProps {
  items: AccordionItem[]
}

export function Accordion({ items }: AccordionProps) {
  const [openId, setOpenId] = useState<string | null>(items[0]?.id || null)

  return (
    <div className="space-y-3">
      {items.map((item) => (
        <div key={item.id} className="border border-border rounded-lg bg-card overflow-hidden">
          <button
            onClick={() => setOpenId(openId === item.id ? null : item.id)}
            className="w-full px-6 py-4 flex items-center justify-between hover:bg-input transition-colors"
          >
            <div className="flex items-center gap-3">
              <h3 className="text-sm font-semibold text-foreground">{item.title}</h3>
              {item.badge}
            </div>
            <ChevronDown
              className={`w-5 h-5 text-muted-foreground transition-transform ${
                openId === item.id ? 'rotate-180' : ''
              }`}
            />
          </button>

          {openId === item.id && (
            <div className="border-t border-border px-6 py-4 bg-background/50">
              <div className="text-sm text-muted-foreground space-y-2">
                {item.content}
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  )
}

// Helper content components
export function SkeletonLoader() {
  return (
    <div className="space-y-2">
      <div className="h-4 bg-muted rounded w-full animate-pulse"></div>
      <div className="h-4 bg-muted rounded w-5/6 animate-pulse"></div>
      <div className="h-4 bg-muted rounded w-4/6 animate-pulse"></div>
    </div>
  )
}

export function CodeBlock({ code }: { code: string }) {
  return (
    <pre className="bg-input border border-border rounded p-4 overflow-x-auto font-mono text-xs">
      <code>{code}</code>
    </pre>
  )
}
