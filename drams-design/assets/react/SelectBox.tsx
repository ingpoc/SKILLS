import { useState } from 'react';

interface SelectBoxProps {
  min?: number;
  max?: number;
  initial?: number;
  onChange?: (value: number) => void;
  ariaLabel?: string;
}

export function SelectBox({
  min = 1,
  max = 99,
  initial = 1,
  onChange,
  ariaLabel = 'Quantity selector'
}: SelectBoxProps) {
  const [value, setValue] = useState(initial);

  const increment = () => {
    if (value < max) {
      const newValue = value + 1;
      setValue(newValue);
      onChange?.(newValue);
    }
  };

  const decrement = () => {
    if (value > min) {
      const newValue = value - 1;
      setValue(newValue);
      onChange?.(newValue);
    }
  };

  return (
    <div
      className="select-box"
      role="spinbutton"
      aria-valuenow={value}
      aria-valuemin={min}
      aria-valuemax={max}
      aria-label={ariaLabel}
    >
      <button
        className="select-btn minus-btn"
        onClick={decrement}
        aria-label="Decrease"
        disabled={value <= min}
      >
        <svg viewBox="0 0 256 256">
          <path d="M216,128a8,8,0,0,1-8,8H48a8,8,0,0,1,0-16H208A8,8,0,0,1,216,128Z"/>
        </svg>
      </button>
      <span className="select-value">{value}</span>
      <button
        className="select-btn plus-btn"
        onClick={increment}
        aria-label="Increase"
        disabled={value >= max}
      >
        <svg viewBox="0 0 256 256">
          <path d="M224,128a8,8,0,0,1-8,8H136v80a8,8,0,0,1-16,0V136H40a8,8,0,0,1,0-16h80V40a8,8,0,0,1,16,0v80h80A8,8,0,0,1,224,128Z"/>
        </svg>
      </button>
    </div>
  );
}

/*
.select-box { display: inline-flex; align-items: center; background: rgb(238, 238, 238); border-radius: 48px; padding: 4px; }
.select-btn { width: 40px; height: 40px; border-radius: 50%; border: none; background: transparent; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s ease; }
.select-btn:hover { background: rgba(255, 97, 26, 0.1); }
.select-btn:active { transform: scale(0.95); }
.select-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.select-btn svg { width: 16px; height: 16px; fill: #333; transition: fill 0.2s ease; }
.select-btn:hover:not(:disabled) svg { fill: rgb(255, 97, 26); }
.select-value { width: 60px; text-align: center; font-size: 16px; font-weight: 500; color: #333; }
*/
