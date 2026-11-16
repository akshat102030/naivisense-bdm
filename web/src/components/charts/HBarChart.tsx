import { useState } from 'react';
import { useWidth } from '../../hooks/useWidth';
import { niceTicks } from '../../lib/stats';
import { Tip } from './Tip';
import { tipFromElement, tipFromPointer, type TipState } from './tipUtils';

export interface HBar {
  label: string;
  value: number;
  color: string;
  tip?: string;
}

interface Props {
  data: HBar[];
  format: (v: number) => string;
  ariaLabel: string;
  rowHeight?: number;
}

/** Horizontal bars for long category labels. */
export function HBarChart({ data, format, ariaLabel, rowHeight = 28 }: Props) {
  const [ref, w] = useWidth<HTMLDivElement>();
  const [tip, setTip] = useState<TipState | null>(null);
  const width = w || 600;
  const labelW = Math.min(190, Math.max(...data.map((d) => d.label.length)) * 6.6 + 14);
  const m = { t: 4, r: 46, b: 26, l: labelW };
  const height = m.t + m.b + data.length * rowHeight;
  const max = Math.max(...data.map((d) => d.value));
  const ticks = niceTicks(max * 1.05, 5);
  const top = ticks[ticks.length - 1];
  const x = (v: number) => m.l + (v / top) * (width - m.l - m.r);
  const bh = rowHeight * 0.62;

  return (
    <div className="chart" ref={ref} onMouseLeave={() => setTip(null)}>
      {w > 0 && (
        <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label={ariaLabel}>
          {ticks.map((t) => (
            <g key={t}>
              <line className="tick-line" x1={x(t)} x2={x(t)} y1={m.t} y2={height - m.b} />
              <text x={x(t)} y={height - m.b + 16} textAnchor="middle">
                {format(t)}
              </text>
            </g>
          ))}
          {data.map((d, i) => {
            const cy = m.t + rowHeight * i + rowHeight / 2;
            const content = d.tip ?? `${d.label}: ${format(d.value)}`;
            return (
              <g key={d.label}>
                <text x={m.l - 10} y={cy + 4} textAnchor="end" style={{ fill: 'var(--theme-text-secondary)' }}>
                  {d.label}
                </text>
                <rect
                  className="hit"
                  x={m.l}
                  y={cy - bh / 2}
                  width={Math.max(2, x(d.value) - m.l)}
                  height={bh}
                  rx={5}
                  style={{ fill: d.color }}
                  tabIndex={0}
                  aria-label={`${d.label}: ${format(d.value)}`}
                  onMouseMove={(e) => setTip(tipFromPointer(ref, e, content))}
                  onFocus={(e) => setTip(tipFromElement(ref, e.currentTarget, content))}
                  onBlur={() => setTip(null)}
                />
                <text className="val" x={x(d.value) + 7} y={cy + 4}>
                  {format(d.value)}
                </text>
              </g>
            );
          })}
        </svg>
      )}
      <Tip tip={tip} />
    </div>
  );
}
