import React from 'react'

// DRAMS Principles: Thorough, Useful, Understandable
// - Handles all states: loading, error, success
// - Clear labels and error messages
// - ARIA attributes for accessibility

interface FormProps {
  onSubmit: (e: React.FormEvent) => void
  children: React.ReactNode
  isLoading?: boolean
  error?: string
}

export function Form({ onSubmit, children, isLoading = false, error }: FormProps) {
  return (
    <form onSubmit={onSubmit} className="space-y-6" aria-busy={isLoading}>
      {error && (
        <div role="alert" className="bg-red-50 border border-red-200 rounded-md p-4 text-red-900">
          {error}
        </div>
      )}

      {children}

      {isLoading && (
        <div className="flex items-center justify-center">
          <div className="h-6 w-6 border-2 border-slate-200 border-t-slate-900 rounded-full animate-spin" aria-hidden="true" />
        </div>
      )}
    </form>
  )
}

interface FieldGroupProps {
  children: React.ReactNode
}

export function FieldGroup({ children }: FieldGroupProps) {
  return <div className="space-y-4">{children}</div>
}

interface FieldProps {
  children: React.ReactNode
}

export function Field({ children }: FieldProps) {
  return <div className="space-y-1">{children}</div>
}
