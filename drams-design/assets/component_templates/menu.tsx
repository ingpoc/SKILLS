import React from 'react'
import * as DropdownMenuPrimitive from '@radix-ui/react-dropdown-menu'

// DRAMS Principles: Useful, Understandable, Unobtrusive
// - Clear purpose items
// - Keyboard navigation built-in
// - Subtle animations

interface MenuItem {
  label: string
  onClick: () => void
  icon?: React.ReactNode
}

interface MenuProps {
  trigger: React.ReactNode
  items: MenuItem[]
  align?: 'start' | 'center' | 'end'
}

export function Menu({ trigger, items, align = 'start' }: MenuProps) {
  return (
    <DropdownMenuPrimitive.Root>
      <DropdownMenuPrimitive.Trigger asChild>
        {trigger}
      </DropdownMenuPrimitive.Trigger>

      <DropdownMenuPrimitive.Portal>
        <DropdownMenuPrimitive.Content
          align={align}
          className="min-w-[180px] bg-white border border-slate-200 rounded-md shadow-lg p-1 z-50"
        >
          {items.map((item, index) => (
            <DropdownMenuPrimitive.Item
              key={index}
              onClick={item.onClick}
              className="flex items-center gap-2 px-3 py-2 text-sm text-slate-900 rounded-md cursor-pointer hover:bg-slate-100 focus:bg-slate-100 focus:outline-none"
            >
              {item.icon && <span className="text-slate-500">{item.icon}</span>}
              <span>{item.label}</span>
            </DropdownMenuPrimitive.Item>
          ))}
        </DropdownMenuPrimitive.Content>
      </DropdownMenuPrimitive.Portal>
    </DropdownMenuPrimitive.Root>
  )
}
