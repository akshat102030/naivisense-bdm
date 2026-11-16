import { useState } from 'react';
import { useWidth } from '../../hooks/useWidth';
import { niceTicks } from '../../lib/stats';
import { Tip } from './Tip';
import { tipFromElement, tipFromPointer, type TipState } from './tipUtils';

export interface Bar {
  label: string;
  value: number;
  color?: string;
  tip?: string;
}

interface Props {
  data: Bar[];
  format: (v: number) => string;
  ariaLabel: string;
  refLine?: { value: number; label: string };
  height?: number;
  yTitle?: string;
}

/** Vertical bar chart with gridlines, value labels, optional dashed reference line and keyboard-reachable bars. */
export function BarChart({ data, format, ariaLabel, refLine, height = 300, yTitle }: Props) {
  const [ref, w] = useWidth<HTMLDivElement>();
  const [tip, setTip] = useState<TipState | null>(null);
  const width = w || 600;
  const crowded = width / Math.max(1, data.length) < 78;
  const m = { t: 24, r: 10, b: crowded ? 76 : 34, l: yTitle ? 54 : 44 };
  const max = Math.max(refLine?.value ?? 0, ...data.map((d) => d.value));
  const ticks = niceTicks(max * 1.08, 5);
  const top = ticks[ticks.length - 1];
  const x0 = m.l;
  const x1 = width - m.r;
  const y = (v: number) => m.t + (1 - v / top) * (height - m.t - m.b);
  const band = (x1 - x0) / data.length;
  const bw = Math.min(64, band * 0.68);

  return (
    <div className="chart" ref={ref} onMouseLeave={() => setTip(null)}>
      {w > 0 && (
        <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label={ariaLabel}>
          {ticks.map((t) => (
            <g key={t}>
              <line className="tick-line" x1={x0} x2={x1} y1={y(t)} y2={y(t)} />
              <text x={x0 - 8} y={y(t) + 4} textAnchor="end">
                {format(t)}
              </text>
            </g>
          ))}
          {yTitle && (
            <text
              className="axis-title"
              transform={`translate(12 ${(m.t + height - m.b) / 2}) rotate(-90)`}
              textAnchor="middle"
            >
              {yTitle}
            </text>
          )}
          {data.map((d, i) => {
            const cx = x0 + band * i + band / 2;
            const tipContent = d.tip ?? `${d.label}: ${format(d.value)}`;
            return (
              <g key={d.label}>
                <rect
                  className="hit"
                  x={cx - bw / 2}
                  y={y(d.value)}
                  width={bw}
                  height={Math.max(0, y(0) - y(d.value))}
                  rx={5}
                  style={{ fill: d.color ?? 'var(--theme-accent)' }}
                  tabIndex={0}
                  aria-label={`${d.label}: ${format(d.value)}`}
                  onMouseMove={(e) => setTip(tipFromPointer(ref, e, tipContent))}
                  onFocus={(e) => setTip(tipFromElement(ref, e.currentTarget, tipContent))}
                  onBlur={() => setTip(null)}
                />
                <text className="val" x={cx} y={y(d.value) - 6} textAnchor="middle">
                  {format(d.value)}
                </text>
                <text
                  x={cx}
                  y={height - m.b + 18}
                  textAnchor={crowded ? 'end' : 'middle'}
                  transform={crowded ? `rotate(-32 ${cx} ${height - m.b + 18})` : undefined}
                >
                  {d.label}
                </text>
              </g>
            );
          })}
          {refLine && (
            <g>
              <line className="ref" x1={x0} x2={x1} y1={y(refLine.value)} y2={y(refLine.value)} />
              <text
                x={x1}
                y={y(refLine.value) - 6}
                textAnchor="end"
                style={{
                  fill: 'var(--theme-text-secondary)',
                  stroke: 'var(--theme-surface)',
                  strokeWidth: 4,
                  paintOrder: 'stroke',
                }}
              >
                {refLine.label}
              </text>
            </g>
          )}
        </svg>
      )}
      <Tip tip={tip} />
    </div>
  );
}
