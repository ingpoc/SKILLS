interface TextBoxProps {
  placeholder?: string;
  value?: string;
  onChange?: (value: string) => void;
  type?: string;
  ariaLabel?: string;
}

export function TextBox({
  placeholder = 'Enter your email...',
  value,
  onChange,
  type = 'text',
  ariaLabel
}: TextBoxProps) {
  const id = `text-box-${Math.random().toString(36).substr(2, 9)}`;

  return (
    <div className="text-box">
      <div className="text-box-track">
        <input
          id={id}
          type={type}
          className="text-box-input"
          placeholder={placeholder}
          value={value}
          onChange={(e) => onChange?.(e.target.value)}
          aria-label={ariaLabel || placeholder}
        />
        <div className="text-box-indicator" />
      </div>
    </div>
  );
}

/*
.text-box { position: relative; width: 100%; }
.text-box-track {
  height: 48px; background: rgb(238, 238, 238); border-radius: 48px;
  padding: 0 20px; display: flex; align-items: center;
  transition: all 0.3s ease;
}
.text-box-track:focus-within {
  background: rgb(230, 230, 230);
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
.text-box-input { flex: 1; border: none; background: transparent; font-size: 15px; color: #333; outline: none; caret-color: rgb(255, 97, 26); }
.text-box-indicator { width: 12px; height: 12px; border-radius: 50%; background: rgb(255, 97, 26); opacity: 0; transition: opacity 0.3s ease; }
.text-box-track:focus-within .text-box-indicator { opacity: 1; }
*/
