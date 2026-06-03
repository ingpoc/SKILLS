import React from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import * as ToastPrimitive from '@radix-ui/react-toast'

// DRAMS Principles: Unobtrusive, Honest
// - Non-intrusive placement (bottom-right)
// - Auto-dismiss after timeout
// - Smooth slide-in animation

interface ToastProps {
  id: string
  title?: string
  message: string
  type?: 'success' | 'error' | 'info'
  duration?: number
  onClose: (id: string) => void
}

export function Toast({
  id,
  title,
  message,
  type = 'info',
  duration = 5000,
  onClose
}: ToastProps) {
  React.useEffect(() => {
    const timer = setTimeout(() => onClose(id), duration)
    return () => clearTimeout(timer)
  }, [id, duration, onClose])

  const typeStyles = {
    success: 'bg-green-600',
    error: 'bg-red-600',
    info: 'bg-slate-900'
  }

  return (
    <AnimatePresence>
      <ToastPrimitive.Root
        forceMount
        asChild
      >
        <motion.div
          initial={{ opacity: 0, x: '100%' }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: '100%' }}
          transition={{ duration: 0.2 }}
          className={`fixed bottom-4 right-4 ${typeStyles[type]} text-white px-4 py-3 rounded-md shadow-lg max-w-sm z-50`}
        >
          <div className="flex items-start gap-3">
            <div className="flex-1">
              {title && <p className="font-medium">{title}</p>}
              <p className="text-sm opacity-90">{message}</p>
            </div>
            <ToastPrimitive.Close
              onClick={() => onClose(id)}
              className="opacity-70 hover:opacity-100"
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                <path d="M4 4l8 8M12 4l-8 8" stroke="currentColor" strokeWidth="2" />
              </svg>
            </ToastPrimitive.Close>
          </div>
        </motion.div>
      </ToastPrimitive.Root>
    </AnimatePresence>
  )
}
