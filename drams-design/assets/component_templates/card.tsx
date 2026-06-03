import React from 'react'

// DRAMS Principles: Aesthetic, Little Design, Understandable
// - Minimal borders with neutral palette
// - Semantic heading hierarchy
// - Essential structure only, remove until breaks

interface CardProps {
  children: React.ReactNode
  onClick?: () => void
  className?: string
}

export function Card({ children, onClick, className = '' }: CardProps) {
  const baseClasses = 'border border-slate-200 rounded-lg p-6 space-y-4 bg-white'

  return (
    <div
      onClick={onClick}
      className={`${baseClasses} ${onClick ? 'cursor-pointer hover:shadow-md transition-shadow' : ''} ${className}`}
    >
      {children}
    </div>
  )
}

interface CardHeaderProps {
  children: React.ReactNode
}

export function CardHeader({ children }: CardHeaderProps) {
  return <div className="space-y-1">{children}</div>
}

interface CardTitleProps {
  children: React.ReactNode
}

export function CardTitle({ children }: CardTitleProps) {
  return <h3 className="text-lg font-medium text-slate-900">{children}</h3>
}

interface CardDescriptionProps {
  children: React.ReactNode
}

export function CardDescription({ children }: CardDescriptionProps) {
  return <p className="text-sm text-slate-600">{children}</p>
}

interface CardContentProps {
  children: React.ReactNode
}

export function CardContent({ children }: CardContentProps) {
  return <div className="pt-4">{children}</div>
}
