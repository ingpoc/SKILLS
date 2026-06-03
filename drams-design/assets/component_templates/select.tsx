import React from 'react'
import * as SelectPrimitive from '@radix-ui/react-select'

// DRAMS Principles: Useful, Understandable
// - Clear purpose with aria-label
// - Radix UI handles accessibility
// - Minimal styling with neutral palette

interface SelectProps {
  value: string
  onChange: (value: string) => void
  options: { value: string; label: string }[]
  placeholder?: string
  ariaLabel?: string
}

export function Select({
  value,
  onChange,
  options,
  placeholder = 'Select...',
  ariaLabel = 'Select option'
}: SelectProps) {
  return (
    <SelectPrimitive.Root value={value} onValueChange={onChange}>
      <SelectPrimitive.Trigger
        aria-label={ariaLabel}
        className="flex items-center justify-between w-full px-3 py-2 text-left border border-slate-300 rounded-md bg-white focus:ring-2 focus:ring-slate-400 focus:border-transparent"
      >
        <SelectPrimitive.Value placeholder={placeholder} />
        <SelectPrimitive.Icon className="ml-2">
          <svg width="12" height="12" viewBox="0 0 12 12" aria-hidden="true">
            <path d="M1 4l5 5 5-5" stroke="currentColor" strokeWidth="2" fill="none" />
          </svg>
        </SelectPrimitive.Icon>
      </SelectPrimitive.Trigger>

      <SelectPrimitive.Portal>
        <SelectPrimitive.Content className="overflow-hidden bg-white border border-slate-200 rounded-md shadow-lg z-50">
          <SelectPrimitive.Viewport className="p-1">
            {options.map((option) => (
              <SelectPrimitive.Item
                key={option.value}
                value={option.value}
                className="relative flex items-center px-3 py-2 text-sm text-slate-900 rounded-md cursor-pointer hover:bg-slate-100 focus:bg-slate-100 focus:outline-none"
              >
                <SelectPrimitive.ItemText>{option.label}</SelectPrimitive.ItemText>
              </SelectPrimitive.Item>
            ))}
          </SelectPrimitive.Viewport>
        </SelectPrimitive.Content>
      </SelectPrimitive.Portal>
    </SelectPrimitive.Root>
  )
}
