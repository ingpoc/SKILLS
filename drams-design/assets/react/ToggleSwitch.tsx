import { useState } from 'react';

interface ToggleSwitchProps {
  checked?: boolean;
  onChange?: (checked: boolean) => void;
  label?: string;
  ariaLabel?: string;
}

export function ToggleSwitch({
  checked: controlledChecked,
  onChange,
  label = 'Toggle',
  ariaLabel
}: ToggleSwitchProps) {
  const [internalChecked, setInternalChecked] = useState(false);
  const checked = controlledChecked ?? internalChecked;

  const toggle = () => {
    const newChecked = !checked;
    setInternalChecked(newChecked);
    onChange?.(newChecked);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      toggle();
    }
  };

  return (
    <div className="toggle-container">
      {label && <span className="toggle-label">{label}</span>}
      <div
        className={`toggle-switch ${checked ? 'active' : ''}`}
        onClick={toggle}
        onKeyDown={handleKeyDown}
        role="switch"
        aria-checked={checked}
        aria-label={ariaLabel || label}
        tabIndex={0}
      >
        <div className="toggle-ball" />
      </div>
    </div>
  );
}

/*
.toggle-container { display: flex; align-items: center; gap: 16px; }
.toggle-label { font-size: 15px; color: #333; }
.toggle-switch {
  width: 56px; height: 32px; background: rgb(238, 238, 238);
  border-radius: 48px; position: relative; cursor: pointer;
  transition: background 0.3s ease;
}
.toggle-switch.active { background: rgb(255, 97, 26); }
.toggle-ball {
  position: absolute; width: 26px; height: 26px; background: white;
  border-radius: 50%; top: 3px; left: 3px;
  transition: left 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 2px 6px rgba(0,0,0,0.15);
}
.toggle-switch.active .toggle-ball { left: 27px; }
*/
