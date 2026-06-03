import { useState, useRef, useEffect } from 'react';

interface RollingSearchProps {
  placeholder?: string;
  onSearch?: (query: string) => void;
  ariaLabel?: string;
}

export function RollingSearch({
  placeholder = 'Search products...',
  onSearch,
  ariaLabel = 'Search'
}: RollingSearchProps) {
  const [expanded, setExpanded] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const expand = () => {
    setExpanded(true);
    inputRef.current?.focus();
  };

  const collapse = () => {
    setExpanded(false);
    if (inputRef.current) inputRef.current.value = '';
  };

  const handleBallClick = () => {
    if (expanded && inputRef.current) {
      onSearch?.(inputRef.current.value);
    } else {
      expand();
    }
  };

  return (
    <div className={`search-container ${expanded ? 'expanded' : ''}`}>
      <div className="gray-track" />
      <div className="shadow-layer-1" />
      <div className="shadow-layer-2" />
      <input
        ref={inputRef}
        type="text"
        className="search-input"
        placeholder={placeholder}
        onBlur={() => setTimeout(collapse, 150)}
        onKeyDown={(e) => e.key === 'Escape' && collapse()}
        aria-label={ariaLabel}
      />
      <div
        className="orange-ball"
        onClick={handleBallClick}
        role="button"
        tabIndex={0}
        aria-expanded={expanded}
        aria-label={expanded ? 'Submit search' : 'Open search'}
        onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && handleBallClick()}
      >
        <svg className="icon search-icon" viewBox="0 0 256 256">
          <path d="M232.49,215.51,185,168a92.12,92.12,0,1,0-17,17l47.53,47.54a12,12,0,0,0,17-17ZM44,112a68,68,0,1,1,68,68A68.07,68.07,0,0,1,44,112Z"/>
        </svg>
        <svg className="icon arrow-icon" viewBox="0 0 256 256">
          <path d="M224.49,136.49l-72,72a12,12,0,0,1-17-17L187,140H40a12,12,0,0,1,0-24H187L135.51,64.48a12,12,0,0,1,17-17l72,72A12,12,0,0,1,224.49,136.49Z"/>
        </svg>
      </div>
    </div>
  );
}

// Include CSS in your component or global styles
/*
.search-container { position: relative; width: 234px; height: 44px; }
.gray-track {
  position: absolute; width: 42px; height: 42px; top: 1px; left: 96px;
  border-radius: 48px; background: rgb(238, 238, 238);
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
.search-container.expanded .gray-track { width: 234px; height: 44px; top: 0; left: 0; }
.search-input {
  position: absolute; left: 52px; top: 50%; transform: translateY(-50%);
  width: calc(100% - 100px); border: none; background: transparent;
  font-size: 15px; color: #333; outline: none; opacity: 0; pointer-events: none;
  transition: opacity 0.3s ease; caret-color: rgb(255, 97, 26);
}
.search-container.expanded .search-input { opacity: 1; pointer-events: auto; }
.orange-ball {
  position: absolute; width: 42px; height: 42px; top: 0; left: 96px;
  border-radius: 50%; overflow: hidden; cursor: pointer;
  transition: left 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  background: radial-gradient(50% 50% at 29.1% 29.7%, rgb(255, 150, 102) 0%, rgb(255, 97, 26) 100%);
}
.search-container.expanded .orange-ball { left: 192px; }
*/
