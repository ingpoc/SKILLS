import React from 'react'
import * as CheckboxPrimitive from '@radix-ui/react-checkbox'

// DRAMS Principles: Understandable, Useful
// - Radix UI handles ARIA
// - Clear label association
// - Visual feedback for checked state

interface CheckboxProps {
  checked: boolean
  onChange: (checked: boolean) => void
  label?: string
  id?: string
  disabled?: boolean
}

export function Checkbox({
  checked,
  onChange,
  label,
  id,
  disabled = false
}: CheckboxProps) {
  const checkboxId = id || label?.toLowerCase().replace(/\s+/g, '-')

  return (
    <div className="flex items-center gap-2">
      <CheckboxPrimitive.Root
        id={checkboxId}
        checked={checked}
        onCheckedChange={(checked) => onChange(checked === true)}
        disabled={disabled}
        className="h-4 w-4 rounded border border-slate-300 bg-white flex items-center justify-center hover:border-slate-400 focus:ring-2 focus:ring-slate-400 data-[state=checked]:bg-slate-900 data-[state=checked]:border-slate-900 disabled:opacity-50"
      >
        <CheckboxPrimitive.Indicator className="text-white">
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none" aria-hidden="true">
            <path d="M2 6l3 3 5-5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </CheckboxPrimitive.Indicator>
      </CheckboxPrimitive.Root>

      {label && (
        <label
          htmlFor={checkboxId}
          className="text-sm text-slate-700 cursor-pointer"
        >
          {label}
        </label>
      )}
    </div>
  )
}
