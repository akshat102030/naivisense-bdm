import { useState, type ReactNode } from 'react';
import { useWidth } from '../../hooks/useWidth';
import { linreg, niceRange } from '../../lib/stats';
import { Tip } from './Tip';
import { tipFromElement, tipFromPointer, type TipState } from './tipUtils';

export interface Point {
  id: string;
  x: number;
  y: number;
  color: string;
  r?: number;
  tip: ReactNode;
  selected?: boolean;
}

interface Props {
  points: Point[];
  xTitle: string;
  yTitle: string;
  xFormat: (v: number) => string;
  yFormat?: (v: number) => string;
  ariaLabel: string;
  medianX?: number;
  medianY?: number;
  trend?: boolean;
  height?: number;
  onSelect?: (id: string) => void;
  yFromZero?: boolean;
}

/** Scatter plot with optional median guides, trend line, keyboard-selectable points. */
export function Scatter({
  points,
  xTitle,
  yTitle,
  xFormat,
  yFormat = String,
  ariaLabel,
  medianX,
  medianY,
  trend,
  height = 340,
  onSelect,
  yFromZero,
}: Props) {
  const [ref, w] = useWidth<HTMLDivElement>();
  const [tip, setTip] = useState<TipState | null>(null);
  const width = w || 600;
  const m = { t: 14, r: 16, b: 46, l: 58 };
  const xs = points.map((p) => p.x);
  const ys = points.map((p) => p.y);
  const xt = niceRange(Math.min(...xs, medianX ?? Infinity), Math.max(...xs, medianX ?? -Infinity), 6);
  const yt = niceRange(yFromZero ? 0 : Math.min(...ys, medianY ?? Infinity), Math.max(...ys, medianY ?? -Infinity), 5);
  const [xlo, xhi, ylo, yhi] = [xt[0], xt[xt.length - 1], yt[0], yt[yt.length - 1]];
  const x = (v: number) => m.l + ((v - xlo) / (xhi - xlo || 1)) * (width - m.l - m.r);
  const y = (v: number) => m.t + (1 - (v - ylo) / (yhi - ylo || 1)) * (height - m.t - m.b);
  const line = trend && points.length > 2 ? linreg(points) : null;

  return (
    <div className="chart" ref={ref} onMouseLeave={() => setTip(null)}>
      {w > 0 && (
        <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label={ariaLabel}>
          {xt.map((t) => (
            <g key={`x${t}`}>
              <line className="tick-line" x1={x(t)} x2={x(t)} y1={m.t} y2={height - m.b} />
              <text x={x(t)} y={height - m.b + 16} textAnchor="middle">
                {xFormat(t)}
              </text>
            </g>
          ))}
          {yt.map((t) => (
            <g key={`y${t}`}>
              <line className="tick-line" x1={m.l} x2={width - m.r} y1={y(t)} y2={y(t)} />
              <text x={m.l - 8} y={y(t) + 4} textAnchor="end">
                {yFormat(t)}
              </text>
            </g>
          ))}
          <text className="axis-title" x={(m.l + width - m.r) / 2} y={height - 6} textAnchor="middle">
            {xTitle}
          </text>
          <text
            className="axis-title"
            transform={`translate(13 ${(m.t + height - m.b) / 2}) rotate(-90)`}
            textAnchor="middle"
          >
            {yTitle}
          </text>
          {medianX != null && <line className="ref" x1={x(medianX)} x2={x(medianX)} y1={m.t} y2={height - m.b} />}
          {medianY != null && <line className="ref" x1={m.l} x2={width - m.r} y1={y(medianY)} y2={y(medianY)} />}
          {line && (
            <line
              className="ref"
              x1={x(xlo)}
              x2={x(xhi)}
              y1={y(line.slope * xlo + line.intercept)}
              y2={y(line.slope * xhi + line.intercept)}
              style={{ stroke: 'var(--theme-accent)', opacity: 0.8 }}
            />
          )}
          {points.map((p) => (
            <circle
              key={p.id}
              className="hit"
              cx={x(p.x)}
              cy={y(p.y)}
              r={p.r ?? 6}
              style={{
                fill: p.color,
                fillOpacity: 0.86,
                stroke: p.selected ? 'var(--theme-text-primary)' : 'var(--theme-surface)',
                strokeWidth: p.selected ? 2.5 : 1.5,
              }}
              tabIndex={onSelect ? 0 : -1}
              role={onSelect ? 'button' : undefined}
              aria-label={`${p.id}: ${xTitle} ${xFormat(p.x)}, ${yTitle} ${yFormat(p.y)}`}
              onMouseMove={(e) => setTip(tipFromPointer(ref, e, p.tip))}
              onFocus={(e) => setTip(tipFromElement(ref, e.currentTarget, p.tip))}
              onBlur={() => setTip(null)}
              onClick={() => onSelect?.(p.id)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  onSelect?.(p.id);
                }
              }}
            />
          ))}
        </svg>
      )}
      <Tip tip={tip} />
    </div>
  );
}
