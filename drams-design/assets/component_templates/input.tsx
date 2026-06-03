import React from 'react'

// DRAMS Principles: Useful, Understandable, Honest, Thorough
// - Clear labels with htmlFor association
// - ARIA descriptions for help text
// - Accurate error states with aria-invalid
// - Handles disabled, error, description states

interface InputProps {
  id?: string
  type?: 'text' | 'email' | 'password' | 'number'
  value?: string
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void
  placeholder?: string
  disabled?: boolean
  error?: string
  label?: string
  description?: string
}

export function Input({
  id,
  type = 'text',
  value,
  onChange,
  placeholder,
  disabled = false,
  error,
  label,
  description
}: InputProps) {
  const inputId = id || label?.toLowerCase().replace(/\s+/g, '-')
  const errorId = error ? `${inputId}-error` : undefined
  const descriptionId = description ? `${inputId}-description` : undefined

  return (
    <div className="space-y-1">
      {label && (
        <label htmlFor={inputId} className="block text-sm font-medium text-slate-700">
          {label}
        </label>
      )}

      <input
        id={inputId}
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        disabled={disabled}
        aria-invalid={!!error}
        aria-describedby={error ? errorId : descriptionId}
        className={`w-full px-3 py-2 rounded-md border focus:ring-2 focus:ring-slate-400 focus:border-transparent disabled:opacity-50 disabled:bg-slate-50 ${error ? 'border-red-500' : 'border-slate-300'}`}
      />

      {description && !error && (
        <p id={descriptionId} className="text-sm text-slate-500">
          {description}
        </p>
      )}

      {error && (
        <p id={errorId} className="text-sm text-red-600" role="alert">
          {error}
        </p>
      )}
    </div>
  )
}
