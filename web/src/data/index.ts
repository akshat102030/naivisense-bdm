import raw from './dashboard.json';
import type { Dashboard, Group } from './types';

export const data = raw as unknown as Dashboard;

export const GROUPS: Group[] = ['Thriving', 'Efficient', 'Under-served', 'At-risk'];

export const GROUP_COLOR: Record<Group, string> = {
  Thriving: 'var(--c-thriving)',
  Efficient: 'var(--c-efficient)',
  'Under-served': 'var(--c-under)',
  'At-risk': 'var(--c-risk)',
};

export const GROUP_HINT: Record<Group, string> = {
  Thriving: 'High fees, high progress',
  Efficient: 'Lower fees, high progress',
  'Under-served': 'High fees, low progress',
  'At-risk': 'Lower fees, low progress',
};

export const INVOLVEMENT_COLOR: Record<string, string> = {
  low: 'var(--c-under)',
  medium: 'var(--c-warn)',
  high: 'var(--c-efficient)',
};
