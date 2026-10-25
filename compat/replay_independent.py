"""Rerun hb against immutable, exact-source Blender reference exports.

Run inside a networkless, read-only-root container with only --out writable.
Never drop Blender failures, rewrite inputs or replace previous attempts.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time
from independent_semantics import compare

p = argparse.ArgumentParser()
p.add_argument('--hb', required=True)
p.add_argument('--reference', required=True, help='Directory containing the Blender assessment report.json')
p.add_argument('--out', required=True)
p.add_argument('--timeout', type=int, default=120)
a = p.parse_args()
root = Path(__file__).resolve().parents[1]
reference = Path(a.reference).resolve()
prior = json.loads((reference / 'report.json').read_text())
out = Path(a.out).resolve()
out.mkdir(parents=True, exist_ok=True)
if any(out.iterdir()):
    raise SystemExit('Output must be empty; preserve earlier attempts in their own directory.')
binary = Path(a.hb).resolve()
engine_hash = hashlib.sha256(binary.read_bytes()).hexdigest()
sources = {str(path.relative_to(root)) for path in (root / 'compat/independent').glob('*.py')}
if sources != {row['file'] for row in prior['rows']}:
    raise SystemExit('Reference source population differs from the current corpus.')


def run(command, folder, label):
    start = time.monotonic()
    with (folder / (label + '.stdout')).open('w') as stdout, (folder / (label + '.stderr')).open('w') as stderr:
        try:
            result = subprocess.run(command, cwd=folder, stdout=stdout, stderr=stderr, timeout=a.timeout)
            status = result.returncode
        except subprocess.TimeoutExpired:
            status = 'timeout'
    return {'returncode': status, 'elapsed_seconds': time.monotonic() - start}


rows = []
for previous in prior['rows']:
    source = root / previous['file']
    if hashlib.sha256(source.read_bytes()).hexdigest() != previous['source_sha256']:
        raise SystemExit(f'Source differs from Blender reference: {source}')
    folder = out / source.stem
    folder.mkdir()
    row = {key: previous[key] for key in ('file', 'source_sha256', 'blender', 'blender_pass', 'blender_process')}
    row['engine_sha256'] = engine_hash
    row['check'] = run([str(binary), 'check', str(source)], folder, 'check')
    row['hb'] = run([str(binary), 'run', str(source), '--scene', str(folder / 'scene.hb'), '--out', str(folder / 'hb.glb')], folder, 'hb')
    row['static_pass'] = row['check']['returncode'] == 0
    row['runtime_pass'] = row['hb']['returncode'] == 0
    row['compatible_execution'] = row['runtime_pass'] and row['blender_pass']
    if row['compatible_execution']:
        try:
            row['semantics'] = compare(reference / previous['artifacts'] / 'blender.glb', folder / 'hb.glb')
        except (AssertionError, KeyError, ValueError, TypeError, IndexError) as exc:
            row['semantics'] = {'passed': False, 'error': str(exc)}
    row['semantic_pass'] = row.get('semantics', {}).get('passed', False)
    row['artifacts'] = source.stem
    rows.append(row)
    (folder / 'record.json').write_text(json.dumps(row, indent=2) + '\n')
    print(json.dumps({'file': source.name, 'runtime': row['runtime_pass'], 'semantic': row['semantic_pass']}), flush=True)
report = {'kind': prior['kind'], 'engine_sha256': engine_hash,
          'reference_report_sha256': hashlib.sha256((reference / 'report.json').read_bytes()).hexdigest(),
          'runner_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'reference_policy': 'Reuse Blender exports only after exact source hash match; rerun hb check, execution and export in fresh folders.',
          'scripts': len(rows), 'rows': rows}
for key in ('blender_pass', 'static_pass', 'runtime_pass', 'compatible_execution', 'semantic_pass'):
    report[key] = sum(row[key] for row in rows)
report['static_accepted_runtime_failed'] = [row['file'] for row in rows if row['static_pass'] and not row['runtime_pass']]
(out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({key: value for key, value in report.items() if key != 'rows'}))
