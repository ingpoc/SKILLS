import { ReactNode } from 'react';

interface ProductCardProps {
  name: string;
  category: string;
  price: string;
  badge?: string;
  image?: ReactNode;
  onAdd?: () => void;
  ariaLabel?: string;
}

export function ProductCard({
  name,
  category,
  price,
  badge,
  image,
  onAdd,
  ariaLabel
}: ProductCardProps) {
  return (
    <div className="product-card">
      <div className="product-image">
        {badge && <span className="product-badge">{badge}</span>}
        {image || <div className="product-placeholder" />}
      </div>
      <div className="product-details">
        <div className="product-name">{name}</div>
        <div className="product-category">{category}</div>
        <div className="product-footer">
          <span className="product-price">{price}</span>
          <button
            className="product-add-btn"
            onClick={onAdd}
            aria-label={ariaLabel || `Add ${name} to cart`}
          >
            <svg viewBox="0 0 256 256">
              <path d="M224,128a8,8,0,0,1-8,8H136v80a8,8,0,0,1-16,0V136H40a8,8,0,0,1,0-16h80V40a8,8,0,0,1,16,0v80h80A8,8,0,0,1,224,128Z"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}

/*
.product-card {
  background: white; border-radius: 20px; overflow: hidden;
  box-shadow: 0 4px 16px rgba(0,0,0,0.06);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.product-card:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0,0,0,0.1); }
.product-image {
  width: 100%; height: 180px;
  background: linear-gradient(135deg, #f5f5f5 0%, #ebebeb 100%);
  display: flex; align-items: center; justify-content: center; position: relative;
}
.product-badge {
  position: absolute; top: 12px; left: 12px; padding: 6px 12px;
  background: rgb(255, 97, 26); color: white; font-size: 11px;
  font-weight: 500; border-radius: 20px; text-transform: uppercase; letter-spacing: 0.5px;
}
.product-placeholder {
  width: 80px; height: 80px;
  background: radial-gradient(50% 50% at 30% 30%, rgb(255, 150, 102) 0%, rgb(255, 97, 26) 100%);
  border-radius: 50%;
  box-shadow: rgba(232, 61, 23, 0.4) 0px 0px 2px -1px inset, 0 4px 12px rgba(255, 97, 26, 0.2);
}
.product-details { padding: 20px; }
.product-name { font-size: 16px; font-weight: 500; color: #333; margin-bottom: 8px; }
.product-category { font-size: 13px; color: #999; margin-bottom: 12px; }
.product-footer { display: flex; align-items: center; justify-content: space-between; }
.product-price { font-size: 20px; font-weight: 600; color: #333; }
.product-add-btn {
  width: 44px; height: 44px; border-radius: 50%; border: none;
  background: radial-gradient(50% 50% at 30% 30%, rgb(255, 150, 102) 0%, rgb(255, 97, 26) 100%);
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: transform 0.2s ease;
  box-shadow: rgba(232, 61, 23, 0.4) 0px 0px 2px -1px inset, 0 2px 8px rgba(255, 97, 26, 0.3);
}
.product-add-btn:hover { transform: scale(1.05); }
.product-add-btn:active { transform: scale(0.95); }
.product-add-btn svg { width: 20px; height: 20px; fill: white; }
*/
