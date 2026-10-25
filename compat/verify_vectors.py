"""Compare the same 100,000 Vector operations in Blender and the embedded shim."""
import argparse,json,math,subprocess,tempfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--hb',default='target/release/hb');p.add_argument('--blender',required=True);p.add_argument('--out',default='compat/vector-report.json');a=p.parse_args()
root=Path(__file__).resolve().parents[1];hb=str(Path(a.hb).resolve());script=root/'compat/vector_fuzz.py'
operations=['add','subtract','component_multiply','scalar_multiply','scalar_divide','dot','length','normalized','lerp','project']
with tempfile.TemporaryDirectory() as directory:
    temp=Path(directory);reference=temp/'reference';reference.mkdir();native=temp/'native';native.mkdir()
    for command,cwd in [([a.blender,'-b','--factory-startup','--python-exit-code','1','--python',str(script)],reference),([hb,'run',str(script)],native)]:
        r=subprocess.run(command,cwd=cwd,capture_output=True,text=True)
        if r.returncode:raise RuntimeError(r.stdout+'\n'+r.stderr)
    ref=json.loads((reference/'vector-fuzz.json').read_text());got=json.loads((native/'vector-fuzz.json').read_text())
assert len(ref)==len(got)==10000
stats={name:dict(operations=0,within_tolerance=0,bit_exact=0,max_absolute_error=0.) for name in operations}
for index,(left,right) in enumerate(zip(ref,got)):
    assert len(left)==len(right)==10
    for name,x,y in zip(operations,left,right):
        if isinstance(x,list):assert len(x)==len(y)
        pairs=list(zip(x,y)) if isinstance(x,list) else [(x,y)]
        s=stats[name];s['operations']+=1
        s['bit_exact']+=all(a==b for a,b in pairs)
        s['within_tolerance']+=all(math.isclose(a,b,rel_tol=1e-6,abs_tol=1e-5) for a,b in pairs)
        s['max_absolute_error']=max(s['max_absolute_error'],*(abs(a-b) for a,b in pairs))
report=dict(reference='Blender 4.5.9 LTS',seed=20260908,scope='Vector only: 2D/3D/4D, finite randomized inputs in [-20,20]; not full mathutils parity',operations=100000,absolute_tolerance=1e-5,relative_tolerance=1e-6,passed=all(s['within_tolerance']==s['operations'] for s in stats.values()),bit_exact=sum(s['bit_exact'] for s in stats.values()),by_operation=stats)
Path(a.out).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
raise SystemExit(0 if report['passed'] else 1)
