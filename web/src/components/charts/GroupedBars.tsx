import { useState } from 'react';
import { useWidth } from '../../hooks/useWidth';
import { niceTicks } from '../../lib/stats';
import { Tip } from './Tip';
import { tipFromElement, tipFromPointer, type TipState } from './tipUtils';

export interface Series {
  key: string;
  label: string;
  color: string;
}
export interface GroupRow {
  label: string;
  values: Record<string, number>;
}

interface Props {
  rows: GroupRow[];
  series: Series[];
  format: (v: number) => string;
  ariaLabel: string;
  height?: number;
  yTitle?: string;
  showValues?: boolean;
}

/** Side-by-side bars per category (e.g. billed vs collected, acknowledge vs resolve). */
export function GroupedBars({ rows, series, format, ariaLabel, height = 300, yTitle, showValues = false }: Props) {
  const [ref, w] = useWidth<HTMLDivElement>();
  const [tip, setTip] = useState<TipState | null>(null);
  const width = w || 600;
  const m = { t: 20, r: 10, b: 34, l: yTitle ? 54 : 44 };
  const max = Math.max(...rows.flatMap((r) => series.map((s) => r.values[s.key] ?? 0)));
  const ticks = niceTicks(max * 1.08, 5);
  const top = ticks[ticks.length - 1];
  const y = (v: number) => m.t + (1 - v / top) * (height - m.t - m.b);
  const band = (width - m.l - m.r) / rows.length;
  const gw = Math.min(band * 0.78, series.length * 40);
  const bw = gw / series.length - 3;

  return (
    <div className="chart" ref={ref} onMouseLeave={() => setTip(null)}>
      {w > 0 && (
        <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label={ariaLabel}>
          {ticks.map((t) => (
            <g key={t}>
              <line className="tick-line" x1={m.l} x2={width - m.r} y1={y(t)} y2={y(t)} />
              <text x={m.l - 8} y={y(t) + 4} textAnchor="end">
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
          {rows.map((r, i) => {
            const cx = m.l + band * i + band / 2;
            return (
              <g key={r.label}>
                {series.map((s, j) => {
                  const v = r.values[s.key] ?? 0;
                  const bx = cx - gw / 2 + j * (gw / series.length) + 1.5;
                  const content = (
                    <>
                      <b>{r.label}</b>
                      <br />
                      {s.label}: {format(v)}
                    </>
                  );
                  return (
                    <g key={s.key}>
                      <rect
                        className="hit"
                        x={bx}
                        y={y(v)}
                        width={bw}
                        height={Math.max(0, y(0) - y(v))}
                        rx={4}
                        style={{ fill: s.color }}
                        tabIndex={0}
                        aria-label={`${r.label}, ${s.label}: ${format(v)}`}
                        onMouseMove={(e) => setTip(tipFromPointer(ref, e, content))}
                        onFocus={(e) => setTip(tipFromElement(ref, e.currentTarget, content))}
                        onBlur={() => setTip(null)}
                      />
                      {showValues && (
                        <text className="val" x={bx + bw / 2} y={y(v) - 5} textAnchor="middle">
                          {format(v)}
                        </text>
                      )}
                    </g>
                  );
                })}
                <text x={cx} y={height - m.b + 18} textAnchor="middle">
                  {r.label}
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
