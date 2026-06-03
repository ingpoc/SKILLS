import { useState, useRef, useEffect } from 'react';

interface DropdownOption {
  value: string;
  label: string;
}

interface DropdownProps {
  options: DropdownOption[];
  placeholder?: string;
  value?: string;
  onChange?: (value: string) => void;
  ariaLabel?: string;
}

export function Dropdown({
  options,
  placeholder = 'Select an option',
  value,
  onChange,
  ariaLabel
}: DropdownProps) {
  const [open, setOpen] = useState(false);
  const [selected, setSelected] = useState<string | undefined>(value);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (option: DropdownOption) => {
    setSelected(option.value);
    onChange?.(option.value);
    setOpen(false);
  };

  const selectedOption = options.find(o => o.value === selected);
  const displayValue = selectedOption?.label || placeholder;

  return (
    <div className="dropdown" ref={dropdownRef}>
      <div
        className={`dropdown-track ${open ? 'open' : ''}`}
        onClick={() => setOpen(!open)}
        tabIndex={0}
        role="combobox"
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-label={ariaLabel}
        onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && setOpen(!open)}
      >
        <span className={`dropdown-label ${!selected ? 'placeholder' : ''}`}>
          {displayValue}
        </span>
        <div className="dropdown-ball">
          <svg className="dropdown-arrow" viewBox="0 0 256 256">
            <path d="M128,168l-72-72a12,12,0,0,1,17-17l55,55,55-55a12,12,0,0,1,17,17Z"/>
          </svg>
        </div>
      </div>
      <div className="dropdown-menu" role="listbox">
        {options.map((option) => (
          <div
            key={option.value}
            className={`dropdown-item ${selected === option.value ? 'selected' : ''}`}
            onClick={() => handleSelect(option)}
            role="option"
            aria-selected={selected === option.value}
          >
            {option.label}
          </div>
        ))}
      </div>
    </div>
  );
}

/*
.dropdown { position: relative; width: 100%; }
.dropdown-track {
  height: 48px; background: rgb(238, 238, 238); border-radius: 48px;
  padding: 0 20px; display: flex; align-items: center; justify-content: space-between;
  cursor: pointer; transition: all 0.3s ease;
}
.dropdown-track:hover { background: rgb(232, 232, 232); }
.dropdown-ball { width: 32px; height: 32px; border-radius: 50%; background: radial-gradient(50% 50% at 30% 30%, rgb(255, 150, 102) 0%, rgb(255, 97, 26) 100%); transition: transform 0.3s ease; }
.dropdown.open .dropdown-ball { transform: rotate(180deg); }
.dropdown-menu {
  position: absolute; top: calc(100% + 8px); left: 0; right: 0;
  background: white; border-radius: 16px; box-shadow: 0 8px 32px rgba(0,0,0,0.1);
  opacity: 0; visibility: hidden; transform: translateY(-10px); transition: all 0.3s ease; z-index: 10;
}
.dropdown.open .dropdown-menu { opacity: 1; visibility: visible; transform: translateY(0); }
.dropdown-item { padding: 14px 20px; cursor: pointer; transition: background 0.2s ease; font-size: 15px; color: #333; }
.dropdown-item:hover { background: rgb(238, 238, 238); }
.dropdown-item.selected { color: rgb(255, 97, 26); }
*/
