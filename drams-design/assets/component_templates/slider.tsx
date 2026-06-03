import React from 'react'
import * as SliderPrimitive from '@radix-ui/react-slider'

// DRAMS Principles: Useful, Understandable, Honest
// - Clear purpose with aria-label
// - Accurate value display
// - Visual feedback for interaction

interface SliderProps {
  value: number[]
  onChange: (value: number[]) => void
  min?: number
  max?: number
  step?: number
  ariaLabel?: string
}

export function Slider({
  value,
  onChange,
  min = 0,
  max = 100,
  step = 1,
  ariaLabel = 'Slider'
}: SliderProps) {
  return (
    <SliderPrimitive.Root
      value={value}
      onValueChange={onChange}
      min={min}
      max={max}
      step={step}
      aria-label={ariaLabel}
      className="relative flex items-center w-full h-2 select-none touch-none"
    >
      <SliderPrimitive.Track className="bg-slate-200 rounded-full grow h-2">
        <SliderPrimitive.Range className="absolute bg-slate-900 rounded-full h-full" />
      </SliderPrimitive.Track>
      <SliderPrimitive.Thumb className="block w-5 h-5 bg-white border-2 border-slate-900 rounded-full hover:scale-110 focus:outline-none focus:ring-2 focus:ring-slate-400 transition-transform cursor-grab" />
    </SliderPrimitive.Root>
  )
}
