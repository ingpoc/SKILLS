import { useState, ReactNode } from 'react';

interface Spec {
  dot?: boolean;
  text: string;
}

interface Stat {
  label: string;
  value: string;
}

interface FlipCardProps {
  title: string;
  subtitle: string;
  stats: Stat[];
  specs: Spec[];
  ariaLabel?: string;
}

export function FlipCard({
  title,
  subtitle,
  stats,
  specs,
  ariaLabel = 'Flip card to see more details'
}: FlipCardProps) {
  const [flipped, setFlipped] = useState(false);

  const toggleFlip = () => setFlipped(!flipped);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      toggleFlip();
    }
  };

  return (
    <div className="flip-card-container">
      <div
        className={`flip-card ${flipped ? 'flipped' : ''}`}
        onClick={toggleFlip}
        onKeyDown={handleKeyDown}
        role="button"
        tabIndex={0}
        aria-label={ariaLabel}
        aria-pressed={flipped}
      >
        <div className="flip-card-front">
          <div className="flip-header">
            <div className="flip-title">{title}</div>
            <div className="flip-subtitle">{subtitle}</div>
          </div>
          <div className="flip-body">
            {stats.map((stat, i) => (
              <div key={i} className="flip-stat">
                <span className="flip-stat-label">{stat.label}</span>
                <span className="flip-stat-value">{stat.value}</span>
              </div>
            ))}
          </div>
          <div className="flip-hint">Click to see specs</div>
        </div>
        <div className="flip-card-back">
          <div className="flip-back-title">Specifications</div>
          {specs.map((spec, i) => (
            <div key={i} className="flip-spec">
              {spec.dot !== false && <div className="flip-spec-dot" />}
              <span className="flip-spec-text">{spec.text}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/*
.flip-card-container { perspective: 1000px; width: 100%; height: 240px; }
.flip-card {
  position: relative; width: 100%; height: 100%;
  transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  transform-style: preserve-3d; cursor: pointer;
}
.flip-card.flipped { transform: rotateY(180deg); }
.flip-card-front, .flip-card-back {
  position: absolute; width: 100%; height: 100%;
  backface-visibility: hidden; border-radius: 20px;
  overflow: hidden; box-shadow: 0 4px 16px rgba(0,0,0,0.06);
}
.flip-card-front { background: white; }
.flip-card-back {
  background: rgb(238, 238, 238); transform: rotateY(180deg);
  padding: 24px; display: flex; flex-direction: column; justify-content: center;
}
.flip-header { padding: 20px; }
.flip-title { font-size: 18px; font-weight: 500; color: #333; margin-bottom: 4px; }
.flip-subtitle { font-size: 13px; color: #999; }
.flip-body { padding: 0 20px 20px; }
.flip-stat { display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid rgba(0,0,0,0.06); }
.flip-stat-label { font-size: 14px; color: #666; }
.flip-stat-value { font-size: 14px; font-weight: 500; color: #333; }
.flip-hint { text-align: center; font-size: 12px; color: #999; padding: 16px; background: rgb(238, 238, 238); }
.flip-back-title { font-size: 16px; font-weight: 500; color: #333; margin-bottom: 16px; }
.flip-spec { display: flex; align-items: center; gap: 12px; padding: 8px 0; }
.flip-spec-dot { width: 8px; height: 8px; border-radius: 50%; background: rgb(255, 97, 26); }
.flip-spec-text { font-size: 14px; color: #555; }
*/
