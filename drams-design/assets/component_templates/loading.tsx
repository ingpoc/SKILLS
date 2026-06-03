import React from 'react'
import { motion } from 'framer-motion'

// DRAMS Principles: Honest, Unobtrusive, Understandable
// - Accurate loading indication
// - Subtle animations
// - Screen reader announcements

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
          className={`border-2 border-slate-200 border-t-slate-900 rounded-full ${sizes[size]}`}
          aria-hidden="true"
        />
        <span className="sr-only">{label}</span>
      </div>
    )
  }

  if (type === 'skeleton') {
    return (
      <div className="animate-pulse bg-slate-200 rounded" aria-hidden="true">
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
            className="w-2 h-2 bg-slate-900 rounded-full"
          />
        ))}
        <span className="sr-only">{label}</span>
      </div>
    )
  }

  return null
}
