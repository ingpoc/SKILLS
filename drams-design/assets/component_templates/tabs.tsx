import React from 'react'
import * as TabsPrimitive from '@radix-ui/react-tabs'

// DRAMS Principles: Useful, Understandable
// - Clear tab labels
// - Semantic structure
// - ARIA handled by Radix UI

interface Tab {
  value: string
  label: string
  content: React.ReactNode
}

interface TabsProps {
  tabs: Tab[]
  defaultValue: string
  ariaLabel?: string
}

export function Tabs({ tabs, defaultValue, ariaLabel = 'Tabs' }: TabsProps) {
  return (
    <TabsPrimitive.Root defaultValue={defaultValue} className="w-full">
      <TabsPrimitive.List
        aria-label={ariaLabel}
        className="inline-flex border-b border-slate-200 w-full"
      >
        {tabs.map((tab) => (
          <TabsPrimitive.Trigger
            key={tab.value}
            value={tab.value}
            className="px-4 py-2 text-sm font-medium text-slate-600 hover:text-slate-900 border-b-2 border-transparent data-[state=active]:border-slate-900 data-[state=active]:text-slate-900 transition-colors focus:outline-none focus:ring-2 focus:ring-slate-400"
          >
            {tab.label}
          </TabsPrimitive.Trigger>
        ))}
      </TabsPrimitive.List>

      {tabs.map((tab) => (
        <TabsPrimitive.Content
          key={tab.value}
          value={tab.value}
          className="pt-4"
        >
          {tab.content}
        </TabsPrimitive.Content>
      ))}
    </TabsPrimitive.Root>
  )
}
