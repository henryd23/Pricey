import React from 'react';

/**
 * Lightweight SVG Price History Chart.
 * Renders an area line chart with data points and price tooltips.
 */
export default function PriceChart({ history = [], currency = 'EUR' }) {
  if (!history || history.length === 0) {
    return (
      <div style={{ padding: '1.5rem', textAlign: 'center', color: '#888' }}>
        Nessun dato di storico disponibile.
      </div>
    );
  }

  // If only 1 price point exists, show a single baseline
  if (history.length === 1) {
    const single = history[0];
    return (
      <div style={{ padding: '1rem', textAlign: 'center', background: '#f8fafc', borderRadius: '8px' }}>
        <p style={{ margin: 0, fontSize: '0.9rem', color: '#64748b' }}>
          Monitoraggio avviato a <strong>{single.price.toFixed(2)} {currency}</strong>
        </p>
        <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
          {new Date(single.timestamp).toLocaleString('it-IT')}
        </span>
      </div>
    );
  }

  const prices = history.map((h) => h.price);
  const minPrice = Math.min(...prices);
  const maxPrice = Math.max(...prices);
  const priceRange = maxPrice === minPrice ? 1 : maxPrice - minPrice;

  const width = 450;
  const height = 140;
  const paddingX = 35;
  const paddingY = 25;

  const chartWidth = width - paddingX * 2;
  const chartHeight = height - paddingY * 2;

  // Map each point to X, Y coordinates
  const points = history.map((item, idx) => {
    const x = paddingX + (idx / (history.length - 1)) * chartWidth;
    const normalizedY = (item.price - minPrice) / priceRange;
    const y = height - paddingY - normalizedY * chartHeight;
    return { x, y, price: item.price, date: item.timestamp };
  });

  const pathData = points.reduce(
    (acc, pt, idx) => (idx === 0 ? `M ${pt.x} ${pt.y}` : `${acc} L ${pt.x} ${pt.y}`),
    ''
  );

  const areaData = `${pathData} L ${points[points.length - 1].x} ${height - paddingY} L ${points[0].x} ${height - paddingY} Z`;

  return (
    <div style={{ width: '100%', overflowX: 'auto' }}>
      <svg
        viewBox={`0 0 ${width} ${height}`}
        style={{ width: '100%', height: 'auto', display: 'block' }}
      >
        <defs>
          <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.35" />
            <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.0" />
          </linearGradient>
        </defs>

        {/* Horizontal grid lines for Min and Max */}
        <line
          x1={paddingX}
          y1={paddingY}
          x2={width - paddingX}
          y2={paddingY}
          stroke="#e2e8f0"
          strokeDasharray="4 4"
        />
        <line
          x1={paddingX}
          y1={height - paddingY}
          x2={width - paddingX}
          y2={height - paddingY}
          stroke="#e2e8f0"
          strokeDasharray="4 4"
        />

        {/* Labels for Max and Min */}
        <text x={paddingX - 5} y={paddingY + 4} fontSize="10" fill="#94a3b8" textAnchor="end">
          {maxPrice.toFixed(2)}€
        </text>
        <text x={paddingX - 5} y={height - paddingY + 4} fontSize="10" fill="#94a3b8" textAnchor="end">
          {minPrice.toFixed(2)}€
        </text>

        {/* Gradient Area Fill */}
        <path d={areaData} fill="url(#chartGradient)" />

        {/* Line */}
        <path d={pathData} fill="none" stroke="#2563eb" strokeWidth="2.5" strokeLinecap="round" />

        {/* Data Circles */}
        {points.map((pt, idx) => (
          <g key={idx}>
            <circle cx={pt.x} cy={pt.y} r="4.5" fill="#ffffff" stroke="#2563eb" strokeWidth="2" />
            <title>
              {pt.price.toFixed(2)} {currency} - {new Date(pt.date).toLocaleString('it-IT')}
            </title>
          </g>
        ))}
      </svg>
    </div>
  );
}

