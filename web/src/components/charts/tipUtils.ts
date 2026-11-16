import type { ReactNode, RefObject } from 'react';

export interface TipState {
  x: number;
  y: number;
  content: ReactNode;
}

/** Tooltip anchored to a pointer position inside `container`. */
export function tipFromPointer(
  container: RefObject<HTMLElement>,
  e: { clientX: number; clientY: number },
  content: ReactNode,
): TipState | null {
  const r = container.current?.getBoundingClientRect();
  if (!r) return null;
  const x = Math.min(Math.max(e.clientX - r.left, 70), Math.max(70, r.width - 70));
  return { x, y: e.clientY - r.top, content };
}

/** Tooltip anchored to the centre-top of a focused element, for keyboard users. */
export function tipFromElement(container: RefObject<HTMLElement>, el: Element, content: ReactNode): TipState | null {
  const c = container.current?.getBoundingClientRect();
  if (!c) return null;
  const r = el.getBoundingClientRect();
  return {
    x: Math.min(Math.max(r.left - c.left + r.width / 2, 70), Math.max(70, c.width - 70)),
    y: r.top - c.top,
    content,
  };
}
