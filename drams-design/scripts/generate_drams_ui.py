#!/usr/bin/env python3
"""
Generate DRAMS-aligned component boilerplate.

Usage:
  python3 generate_drams_ui.py button --variant primary
  python3 generate_drams_ui.py input --type email
  python3 generate_drams_ui.py list
"""

import sys
import argparse
from pathlib import Path

# Component templates
TEMPLATES = {
    "button": """import React from 'react'
import { motion } from 'framer-motion'

interface ButtonProps {
  children: React.ReactNode
  onClick?: () => void
  isLoading?: boolean
  disabled?: boolean
  variant?: 'primary' | 'secondary' | 'text' | 'icon'
  ariaLabel?: string
}

export function Button({
  children,
  onClick,
  isLoading = false,
  disabled = false,
  variant = 'primary',
  ariaLabel
}: ButtonProps) {
  const baseClasses = 'rounded-full font-medium transition-all duration-300 focus:outline-none focus-visible:ring-2 focus-visible:ring-[rgb(255,97,26)]'

  const variantClasses = {
    primary: 'bg-[rgb(255,97,26)] text-white hover:shadow-[0_2px_8px_rgba(255,97,26,0.3)]',
    secondary: 'bg-[rgb(238,238,238)] text-[#333] hover:bg-[rgb(232,232,232)]',
    text: 'text-[#333] hover:text-[rgb(255,97,26)]',
    icon: 'p-2 hover:bg-[rgb(238,238,238)]'
  }

  return (
    <motion.button
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      onClick={onClick}
      disabled={disabled || isLoading}
      aria-busy={isLoading}
      aria-label={ariaLabel}
      className={`
        ${baseClasses}
        ${variantClasses[variant]}
        ${(disabled || isLoading) ? 'opacity-50 cursor-not-allowed' : ''}
      `}
    >
      {isLoading ? (
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          className="h-4 w-4 border-2 border-current border-t-transparent rounded-full"
        />
      ) : children}
    </motion.button>
  )
}

// DRAMS Principles:
// - Useful: Clear purpose, action-driven
// - Understandable: Optional aria-label for icon buttons
// - Aesthetic: Slate palette, minimal design
// - Unobtrusive: Subtle hover (scale-105)
// - Honest: Accurate loading state
// - Environmentally friendly: Tree-shakeable imports
""",
    "input": r"""import React from 'react'

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
        <label
          htmlFor={inputId}
          className="block text-sm font-medium text-[#333]"
        >
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
        className={`
          w-full px-3 py-2 rounded-md border
          focus:ring-2 focus:ring-[rgb(255,97,26)] focus:border-transparent
          disabled:opacity-50 disabled:bg-[rgb(238,238,238)]
          ${error ? 'border-[rgb(255,97,26)]' : 'border-[rgb(238,238,238)]'}
        `}
      />

      {description && !error && (
        <p id={descriptionId} className="text-sm text-[#999]">
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

// DRAMS Principles:
// - Useful: Clear labels, helpful placeholders
// - Understandable: ARIA descriptions, semantic HTML
// - Honest: Accurate error and disabled states
// - Thorough: Handles error, disabled, description states
""",
    "card": """import React from 'react'

interface CardProps {
  children: React.ReactNode
  onClick?: () => void
  className?: string
}

export function Card({ children, onClick, className = '' }: CardProps) {
  const baseClasses = 'border border-[rgb(238,238,238)] rounded-[20px] p-6 space-y-4 bg-white shadow-[0_4px_16px_rgba(0,0,0,0.06)] transition-all duration-300 hover:shadow-[0_8px_24px_rgba(0,0,0,0.1)] hover:-translate-y-1'

  return (
    <div
      onClick={onClick}
      className={`
        ${baseClasses}
        ${onClick ? 'cursor-pointer hover:shadow-md transition-shadow' : ''}
        ${className}
      `}
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
  return <h3 className="text-lg font-medium text-[#333]">{children}</h3>
}

interface CardDescriptionProps {
  children: React.ReactNode
}

export function CardDescription({ children }: CardDescriptionProps) {
  return <p className="text-sm text-[#999]">{children}</p>
}

interface CardContentProps {
  children: React.ReactNode
}

export function CardContent({ children }: CardContentProps) {
  return <div className="pt-4">{children}</div>
}

// DRAMS Principles:
// - Aesthetic: Minimal borders, neutral palette
// - Little design: Essential structure only
// - Understandable: Semantic heading hierarchy
""",
    "loading": """import React from 'react'
import { motion } from 'framer-motion'

interface LoadingProps {
  size?: 'sm' | 'md' | 'lg'
  type?: 'spinner' | 'skeleton' | 'dots'
  label?: string
}

export function Loading({
  size = 'md',
  type = 'spinner',
  label = 'Loading...'
}: LoadingProps) {
  const sizes = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8'
  }

  if (type === 'spinner') {
    return (
      <div className="flex items-center gap-2">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          className={`border-2 border-[rgb(238,238,238)] border-t-[rgb(255,97,26)] rounded-full ${sizes[size]}`}
          aria-hidden="true"
        />
        <span className="sr-only">{label}</span>
      </div>
    )
  }

  if (type === 'skeleton') {
    return (
      <div className="animate-pulse bg-[rgb(238,238,238)] rounded" aria-hidden="true">
        <div className="h-4 w-full" />
      </div>
    )
  }

  if (type === 'dots') {
    return (
      <div className="flex items-center gap-1" aria-hidden="true">
        {[0, 1, 2].map((i) => (
          <motion.div
            key={i}
            animate={{ opacity: [0, 1, 0] }}
            transition={{
              duration: 1.4,
              repeat: Infinity,
              ease: 'easeInOut',
              delay: i * 0.2
            }}
            className="w-2 h-2 bg-[rgb(255,97,26)] rounded-full"
          />
        ))}
        <span className="sr-only">{label}</span>
      </div>
    )
  }

  return null
}

// DRAMS Principles:
// - Honest: Accurate loading indication
// - Unobtrusive: Subtle animations
// - Understandable: Screen reader announcements
""",
    "alert": """import React from 'react'
import { AlertCircle } from 'lucide-react'

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
          {title && (
            <h3 className="font-medium mb-1">{title}</h3>
          )}
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

// DRAMS Principles:
// - Honest: Accurate alert type and message
// - Understandable: ARIA alert role, icon + text
// - Thorough: Handles all alert types
""",
}

def list_components():
    """List available component templates."""
    print("\n🎨 Available DRAMS Component Templates:\n")
    for component in sorted(TEMPLATES.keys()):
        print(f"  • {component}")
    print()

def generate_component(component: str, options: dict):
    """Generate component from template."""
    if component not in TEMPLATES:
        print(f"❌ Error: Component '{component}' not found")
        print(f"   Run 'list' to see available components")
        return 1

    template = TEMPLATES[component]

    # Apply options (future: modify template based on options)
    output = template

    # Print to stdout
    print(output)
    return 0

def main():
    parser = argparse.ArgumentParser(
        description='Generate DRAMS-aligned component boilerplate'
    )
    parser.add_argument('component', help='Component type (or "list")')
    parser.add_argument('--variant', help='Component variant')
    parser.add_argument('--type', help='Component type')
    parser.add_argument('--output', '-o', help='Output file')

    args = parser.parse_args()

    if args.component == 'list':
        list_components()
        return 0

    options = {
        'variant': args.variant,
        'type': args.type
    }

    exit_code = generate_component(args.component, options)

    return exit_code

if __name__ == '__main__':
    sys.exit(main())
