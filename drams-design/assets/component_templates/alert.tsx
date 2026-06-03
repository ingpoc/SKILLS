import React from 'react'

// DRAMS Principles: Honest, Understandable, Thorough
// - ARIA alert role for announcements
// - Icon + text for clarity
// - Handles all alert types

interface AlertProps {
  type?: 'error' | 'warning' | 'success' | 'info'
  title?: string
  children: React.ReactNode
}

export function Alert({
  type = 'info',
  title,
  children
}: AlertProps) {
  const styles = {
    error: 'bg-red-50 border-red-200 text-red-900',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-900',
    success: 'bg-green-50 border-green-200 text-green-900',
    info: 'bg-blue-50 border-blue-200 text-blue-900'
  }

  const iconStyles = {
    error: 'text-red-600',
    warning: 'text-yellow-600',
    success: 'text-green-600',
    info: 'text-blue-600'
  }

  return (
    <div
      role="alert"
      className={`border rounded-lg p-4 ${styles[type]}`}
    >
      <div className="flex items-start gap-3">
        <AlertCircleIcon className={`mt-0.5 flex-shrink-0 ${iconStyles[type]}`} />
        <div className="flex-1">
          {title && <h3 className="font-medium mb-1">{title}</h3>}
          <div className="text-sm">{children}</div>
        </div>
      </div>
    </div>
  )
}

function AlertCircleIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      xmlns="http://www.w3.org/2000/svg"
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <circle cx="12" cy="12" r="10" />
      <line x1="12" y1="8" x2="12" y2="12" />
      <line x1="12" y1="16" x2="12.01" y2="16" />
    </svg>
  )
}
