import React from 'react'
import * as DialogPrimitive from '@radix-ui/react-dialog'
import { motion } from 'framer-motion'

// DRAMS Principles: Thorough, Honest, Unobtrusive
// - Focus trap for accessibility
// - Escape key to close
// - Subtle scale-in animation

interface ModalProps {
  isOpen: boolean
  onClose: () => void
  title: string
  description?: string
  children: React.ReactNode
}

export function Modal({
  isOpen,
  onClose,
  title,
  description,
  children
}: ModalProps) {
  return (
    <DialogPrimitive.Root open={isOpen} onOpenChange={onClose}>
      <DialogPrimitive.Portal>
        <DialogPrimitive.Overlay className="fixed inset-0 bg-black/50 z-40" />

        <DialogPrimitive.Content
          aria-labelledby="dialog-title"
          aria-describedby={description ? 'dialog-description' : undefined}
          className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 bg-white rounded-lg shadow-xl p-6 max-w-md w-full z-50"
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.15 }}
          >
            <div className="flex items-start justify-between mb-4">
              <DialogPrimitive.Title
                id="dialog-title"
                className="text-lg font-medium text-slate-900"
              >
                {title}
              </DialogPrimitive.Title>

              <DialogPrimitive.Close
                onClick={onClose}
                className="text-slate-400 hover:text-slate-600"
              >
                <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M4 4l12 12M16 4l-12 12" stroke="currentColor" strokeWidth="2" />
                </svg>
              </DialogPrimitive.Close>
            </div>

            {description && (
              <DialogPrimitive.Description
                id="dialog-description"
                className="text-sm text-slate-600 mb-4"
              >
                {description}
              </DialogPrimitive.Description>
            )}

            {children}
          </motion.div>
        </DialogPrimitive.Content>
      </DialogPrimitive.Portal>
    </DialogPrimitive.Root>
  )
}
