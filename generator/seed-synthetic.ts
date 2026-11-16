/**
 * Sample-data seeder + analytics exporter.
 *
 *   npm run seed                           # generate + CSV export only (no DB writes)
 *   npm run seed:write                     # also write to MongoDB (DB: naivisense_synthetic)
 *   npm run seed:write -- --db=naivisense --allow-app-db   # app DB (explicit opt-in)
 *   --students=50   --out=../01_Data (default)
 *
 * Safety: every document carries `synthetic: true`. Re-runs delete only those
 * documents (never drop collections). Processed collections are `proc_*`.
 */
import 'dotenv/config';
import fs from 'fs';
import path from 'path';
import { generate, Row } from './synthetic/generate';
import { process as buildProcessed } from './synthetic/process';

const arg = (k: string) => process.argv.find((a) => a.startsWith(`--${k}=`))?.split('=')[1];
const flag = (k: string) => process.argv.includes(`--${k}`);

const students = Number(arg('students') ?? 50);
const dbName = arg('db') ?? 'naivisense_synthetic';
const outDir = path.resolve(__dirname, arg('out') ?? '../01_Data');

function flatten(row: Row, prefix = '', acc: Record<string, string> = {}): Record<string, string> {
  for (const [k, v] of Object.entries(row)) {
    const key = prefix ? `${prefix}.${k}` : k;
    if (v == null) acc[key] = '';
    else if (v instanceof Date) acc[key] = v.toISOString();
    else if (Array.isArray(v)) acc[key] = v.every((x) => typeof x !== 'object' || x == null || (x as object).constructor?.name === 'ObjectId') ? v.join('|') : JSON.stringify(v);
    else if (typeof v === 'object' && (v as object).constructor?.name !== 'ObjectId') flatten(v as Row, key, acc);
    else acc[key] = String(v);
  }
  return acc;
}
const csvCell = (s: string) => (/[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s);

function writeCsv(dir: string, name: string, rows: Row[], drop: string[] = []) {
  fs.mkdirSync(dir, { recursive: true });
  const flat = rows.map((r) => flatten(r)).map((r) => { drop.forEach((d) => delete r[d]); return r; });
  const cols = [...new Set(flat.flatMap((r) => Object.keys(r)))];
  const body = flat.map((r) => cols.map((c) => csvCell(r[c] ?? '')).join(','));
  fs.writeFileSync(path.join(dir, `${name}.csv`), [cols.join(','), ...body].join('\n') + '\n');
}

async function main() {
  // bcrypt/mongoose are loaded lazily: only needed when writing to the DB.
  const write = flag('write');
  const hash = write ? await (await import('bcrypt')).default.hash('Synthetic@123', 10) : 'not-a-real-hash';
  const raw = generate(hash, students);
  const processed = buildProcessed(raw);

  for (const [name, rows] of Object.entries(raw)) writeCsv(path.join(outDir, 'raw'), name, rows, ['password_hash', 'synthetic']);
  for (const [name, rows] of Object.entries(processed)) writeCsv(path.join(outDir, 'processed'), name, rows);
  console.log(`CSV written to ${outDir}`);
  for (const [n, r] of Object.entries(raw)) console.log(`  raw/${n}.csv`.padEnd(34), r.length);
  for (const [n, r] of Object.entries(processed)) console.log(`  processed/${n}.csv`.padEnd(34), r.length);

  if (!flag('write')) { console.log('\nDry run: no database writes. Add --write to seed MongoDB.'); return; }
  if (dbName === 'naivisense' && !flag('allow-app-db')) {
    throw new Error('Refusing to write into the app database "naivisense" without --allow-app-db');
  }
  const mongoose = (await import('mongoose')).default;
  await mongoose.connect(process.env.MONGO_URL!, { dbName });
  const db = mongoose.connection.db!;
  console.log(`\nWriting to MongoDB database "${dbName}"`);
  const rawMap: Record<string, string> = {
    users: 'users', parent_profiles: 'parentprofiles', children: 'children', sessions: 'sessions', attendances: 'attendances',
    assessments: 'assessments', assessment_history: 'assessment_history', goals: 'goals', alerts: 'alerts', concerns: 'concerns',
    payments: 'payments', meal_logs: 'meallogs', home_task_logs: 'hometasklogs',
  };
  for (const [k, rows] of Object.entries(raw)) {
    const col = db.collection(rawMap[k]);
    await col.deleteMany({ synthetic: true });
    await col.insertMany(rows as never[]);
    console.log(`  ${rawMap[k]}`.padEnd(24), rows.length);
  }
  for (const [k, rows] of Object.entries(processed)) {
    const col = db.collection(`proc_${k}`);
    await col.deleteMany({});
    await col.insertMany(rows.map((r) => ({ ...r })) as never[]);
    console.log(`  proc_${k}`.padEnd(24), rows.length);
  }
  await mongoose.disconnect();
}

main().catch((e) => { console.error(e); process.exit(1); });
