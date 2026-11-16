import type { TipState } from './tipUtils';

export function Tip({ tip }: { tip: TipState | null }) {
  if (!tip) return null;
  return (
    <div className="tip" style={{ left: tip.x, top: tip.y }} role="status">
      {tip.content}
    </div>
  );
}
