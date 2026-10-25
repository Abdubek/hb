"""Measure the synthetic regression seed with the actual executable."""
import argparse
import ast
import collections
import json
import subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--hb',default='target/release/hb');p.add_argument('--out',default='compat/coverage.json');p.add_argument('--golden',default='compat/golden-report.json');p.add_argument('--minimum',type=float,default=0);a=p.parse_args()
root=Path(__file__).resolve().parents[1]
results=[];symbols=collections.Counter();unsupported=collections.Counter()
for script in sorted((root/'compat/seed-corpus').glob('*.py')):
    run=subprocess.run([a.hb,'check',str(script)],capture_output=True,text=True)
    try: check=json.loads(run.stdout)
    except ValueError: raise RuntimeError(f'{script}: {run.stderr}\n{run.stdout}')
    for node in ast.walk(ast.parse(script.read_text())):
        if isinstance(node,ast.Attribute):
            text=ast.unparse(node)
            if text.startswith(('bpy.','bmesh.','mathutils.')):symbols[text]+=1
    for issue in check.get('errors',[]):unsupported[issue['message'].split(':',1)[0]]+=1
    results.append(dict(script=script.name,static_pass=check.get('ok',False),errors=check.get('errors',[check.get('error')]) if not check.get('ok') else []))
report=dict(corpus_kind='synthetic seed, 25 families with 8 parameter variants; not an independent production corpus',scripts=len(results),static_pass=sum(r['static_pass'] for r in results),runtime_pass=None,blender_golden_pass=None,symbol_frequency=dict(symbols.most_common()),unsupported_frequency=dict(unsupported.most_common()),results=results)
golden=Path(a.golden)
if golden.exists():
    verified=set(json.loads(golden.read_text())['verified_scripts'])
    passed=[r['script'] for r in results if r['static_pass']]
    report['runtime_pass']=sum(name in verified for name in passed)
    report['blender_golden_pass']=report['runtime_pass']
    report['static_pass_runtime_rejected']=[r['script'] for r in results if r['static_pass'] and r['script'] not in verified]
    report['runtime_evidence']=str(golden)+'; regenerate after source or corpus changes'
Path(a.out).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('results','symbol_frequency')}))

if a.minimum and (report["runtime_pass"] or 0)/max(1,report["scripts"])<a.minimum:raise SystemExit("Corpus runtime coverage below required threshold")
