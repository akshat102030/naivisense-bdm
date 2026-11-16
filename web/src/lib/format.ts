export const inr = (v: number) => '₹' + Math.round(v).toLocaleString('en-IN');
export const lakh = (v: number) => '₹' + (v / 1e5).toFixed(1) + ' L';
export const pct = (v: number, d = 0) => (v * 100).toFixed(d) + '%';
export const n1 = (v: number) => v.toFixed(1);
export const n2 = (v: number) => v.toFixed(2);
export const cap = (s: string) => (s ? s[0].toUpperCase() + s.slice(1) : s);
export const label = (s: string) => cap(s.replace(/_/g, ' '));

const SPECIAL: Record<string, string> = {
  ot: 'OT',
  adl: 'ADL',
  special_ed: 'Special education',
  behavior: 'Behaviour',
  speech: 'Speech',
};
/** Display name for therapy types and domains (OT, ADL, Special education). */
export const nice = (s: string) => SPECIAL[s.toLowerCase().replace(/ /g, '_')] ?? cap(s.replace(/_/g, ' '));
export const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
