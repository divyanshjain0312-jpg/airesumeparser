'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { FileSearch, Target } from 'lucide-react'

const TABS = [
  { href: '/', label: 'Resume Parser', icon: FileSearch },
  { href: '/skill-gap', label: 'Skill Gap & Courses', icon: Target },
]

export function Tabs() {
  const pathname = usePathname()

  return (
    <div className="flex gap-2 mb-8 border-b border-border">
      {TABS.map((tab) => {
        const active = pathname === tab.href
        const Icon = tab.icon
        return (
          <Link
            key={tab.href}
            href={tab.href}
            className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 -mb-px transition-colors ${
              active
                ? 'border-primary text-foreground'
                : 'border-transparent text-muted-foreground hover:text-foreground hover:border-border'
            }`}
          >
            <Icon className="w-4 h-4" />
            {tab.label}
          </Link>
        )
      })}
    </div>
  )
}
