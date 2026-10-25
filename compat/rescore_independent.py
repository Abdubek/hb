"""Recheck preserved GLBs without rerunning or editing independent sources.

The original execution report stays intact. The output records the scoring
module hash, preserves execution provenance and references the original report.
"""
import argparse
import hashlib
import json
from pathlib import Path
from independent_semantics import compare

p=argparse.ArgumentParser();p.add_argument('--report',required=True);p.add_argument('--out',required=True);a=p.parse_args()
source=Path(a.report).resolve();destination=Path(a.out).resolve()
if source==destination:raise SystemExit('Choose a separate output to preserve the original assessment')
report=json.loads(source.read_text())
for row in report['rows']:
    if row['compatible_execution']:
        folder=source.parent/row['artifacts']
        row['semantics']=compare(folder/'blender.glb',folder/'hb.glb')
    row['semantic_pass']=row.get('semantics',{}).get('passed',False)
report['semantic_pass']=sum(row['semantic_pass'] for row in report['rows'])
report['scoring']={'source_report':str(source),'source_report_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
    'module_sha256':hashlib.sha256(Path(__file__).with_name('independent_semantics.py').read_bytes()).hexdigest(),
    'note':'Recomputed from preserved GLBs; exporter-specific camera/light extras are editing metadata and excluded; standard properties remain checked.'}
destination.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='rows'}))
