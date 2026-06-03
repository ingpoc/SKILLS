import { useState } from 'react';

interface RadioOption {
  value: string;
  label: string;
}

interface RadioGroupProps {
  options: RadioOption[];
  value?: string;
  onChange?: (value: string) => void;
  name?: string;
  ariaLabel?: string;
}

export function RadioGroup({
  options,
  value: controlledValue,
  onChange,
  name = 'radio-group',
  ariaLabel
}: RadioGroupProps) {
  const [internalValue, setInternalValue] = useState<string | undefined>(controlledValue);
  const selectedValue = controlledValue ?? internalValue;

  const handleChange = (value: string) => {
    setInternalValue(value);
    onChange?.(value);
  };

  return (
    <div className="radio-group" role="radiogroup" aria-label={ariaLabel}>
      {options.map((option) => (
        <div key={option.value} className="radio-option">
          <input
            type="radio"
            name={name}
            id={`${name}-${option.value}`}
            checked={selectedValue === option.value}
            onChange={() => handleChange(option.value)}
            aria-label={option.label}
          />
          <label className="radio-label" htmlFor={`${name}-${option.value}`}>
            <div className="radio-dot" />
            <span className="radio-text">{option.label}</span>
          </label>
        </div>
      ))}
    </div>
  );
}

/*
.radio-group { display: flex; flex-wrap: wrap; gap: 12px; }
.radio-option { position: relative; }
.radio-option input { position: absolute; opacity: 0; pointer-events: none; }
.radio-label {
  display: flex; align-items: center; gap: 10px; padding: 12px 18px;
  background: rgb(238, 238, 238); border-radius: 48px;
  cursor: pointer; transition: all 0.3s ease;
}
.radio-label:hover { background: rgb(232, 232, 232); }
.radio-option input:checked + .radio-label {
  background: rgb(255, 97, 26); color: white;
}
.radio-dot { width: 16px; height: 16px; border-radius: 50%; border: 2px solid #999; transition: all 0.3s ease; }
.radio-option input:checked + .radio-label .radio-dot { border-color: white; background: white; }
.radio-text { font-size: 14px; }
*/
