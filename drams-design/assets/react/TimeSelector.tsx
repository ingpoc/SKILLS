import { useState } from 'react';

interface TimeSelectorProps {
  initialHours?: number;
  initialMinutes?: number;
  onTimeChange?: (hours: number, minutes: number) => void;
  ariaLabel?: string;
}

export function TimeSelector({
  initialHours = 2,
  initialMinutes = 30,
  onTimeChange,
  ariaLabel = 'Time selector'
}: TimeSelectorProps) {
  const [hours, setHours] = useState(initialHours);
  const [minutes, setMinutes] = useState(initialMinutes);

  const adjustTime = (unit: 'hours' | 'minutes', delta: number) => {
    if (unit === 'hours') {
      const newHours = Math.max(0, Math.min(12, hours + delta));
      setHours(newHours);
      onTimeChange?.(newHours, minutes);
    } else {
      const newMinutes = Math.max(0, Math.min(59, minutes + delta));
      setMinutes(newMinutes);
      onTimeChange?.(hours, newMinutes);
    }
  };

  return (
    <div className="time-selector" aria-label={ariaLabel}>
      <div className="time-unit active">
        <span className="time-label">Hours</span>
        <div className="time-display">
          <span className="time-value hours">{String(hours).padStart(2, '0')}</span>
        </div>
        <div className="time-controls">
          <button
            className="time-btn time-up"
            onClick={() => adjustTime('hours', 1)}
            aria-label="Increase hours"
          >
            +
          </button>
          <button
            className="time-btn time-down"
            onClick={() => adjustTime('hours', -1)}
            aria-label="Decrease hours"
          >
            −
          </button>
        </div>
      </div>
      <span className="time-separator">:</span>
      <div className="time-unit active">
        <span className="time-label">Minutes</span>
        <div className="time-display">
          <span className="time-value minutes">{String(minutes).padStart(2, '0')}</span>
        </div>
        <div className="time-controls">
          <button
            className="time-btn time-up"
            onClick={() => adjustTime('minutes', 15)}
            aria-label="Increase minutes"
          >
            +
          </button>
          <button
            className="time-btn time-down"
            onClick={() => adjustTime('minutes', -15)}
            aria-label="Decrease minutes"
          >
            −
          </button>
        </div>
      </div>
    </div>
  );
}

/*
.time-selector { display: flex; align-items: center; gap: 12px; }
.time-unit { display: flex; flex-direction: column; align-items: center; }
.time-label { font-size: 11px; color: #999; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
.time-display {
  width: 80px; height: 80px; background: rgb(238, 238, 238); border-radius: 50%;
  display: flex; align-items: center; justify-content: center; font-size: 28px;
  font-weight: 300; color: #333; position: relative;
  box-shadow: inset 0 2px 4px rgba(255,255,255,0.8), 0 2px 8px rgba(0,0,0,0.08);
}
.time-unit.active .time-display::before {
  content: ''; position: absolute; width: 100%; height: 100%;
  border-radius: 50%; border: 2px solid rgb(255, 97, 26); transition: border-color 0.3s ease;
}
.time-controls { display: flex; gap: 8px; margin-top: 12px; }
.time-btn {
  width: 32px; height: 32px; border-radius: 50%; border: none;
  background: rgb(255, 97, 26); color: white; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  font-size: 18px; transition: transform 0.2s ease;
  box-shadow: 0 2px 8px rgba(255, 97, 26, 0.3);
}
.time-btn:hover { transform: scale(1.05); }
.time-btn:active { transform: scale(0.95); }
.time-separator { font-size: 24px; color: #999; font-weight: 300; }
*/
