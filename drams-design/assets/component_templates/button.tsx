import React from 'react'
import { motion } from 'framer-motion'

// DRAMS Principles: Useful, Understandable, Unobtrusive, Honest
// - Clear purpose with action-driven labels
// - ARIA labels for icon-only buttons
// - Subtle hover animation (scale-105)
// - Accurate loading state

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
  const baseClasses = 'rounded-md font-medium transition-colors focus:ring-2 focus:ring-slate-400'

  const variantClasses = {
    primary: 'bg-slate-900 text-white hover:bg-slate-800',
    secondary: 'bg-slate-100 text-slate-900 hover:bg-slate-200',
    text: 'text-slate-700 hover:text-slate-900',
    icon: 'p-2 hover:bg-slate-100'
  }

  return (
    <motion.button
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      onClick={onClick}
      disabled={disabled || isLoading}
      aria-busy={isLoading}
      aria-label={ariaLabel}
      className={`${baseClasses} ${variantClasses[variant]} ${(disabled || isLoading) ? 'opacity-50 cursor-not-allowed' : ''}`}
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
