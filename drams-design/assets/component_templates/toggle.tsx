import React from 'react'
import * as SwitchPrimitive from '@radix-ui/react-switch'

// DRAMS Principles: Understandable, Unobtrusive
// - Clear on/off state
// - Smooth transitions
// - ARIA handled by Radix UI

interface ToggleProps {
  checked: boolean
  onChange: (checked: boolean) => void
  label?: string
  id?: string
  disabled?: boolean
}

export function Toggle({
  checked,
  onChange,
  label,
  id,
  disabled = false
}: ToggleProps) {
  const toggleId = id || label?.toLowerCase().replace(/\s+/g, '-')

  return (
    <div className="flex items-center gap-3">
      <SwitchPrimitive.Root
        id={toggleId}
        checked={checked}
        onCheckedChange={onChange}
        disabled={disabled}
        className="h-6 w-11 rounded-full bg-slate-200 data-[state=checked]:bg-slate-900 transition-colors disabled:opacity-50 relative"
      >
        <SwitchPrimitive.Thumb className="block h-5 w-5 rounded-full bg-white shadow-sm transition-transform data-[state=checked]:translate-x-6" />
      </SwitchPrimitive.Root>

      {label && (
        <label
          htmlFor={toggleId}
          className="text-sm text-slate-700 cursor-pointer"
        >
          {label}
        </label>
      )}
    </div>
  )
}
