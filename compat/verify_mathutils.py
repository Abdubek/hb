"""Compare 100,000 rotation/matrix operations against actual Blender."""
import argparse,json,math,subprocess,tempfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--hb',default='target/release/hb');p.add_argument('--blender');p.add_argument('--reference');p.add_argument('--out',default='compat/mathutils-report.json');a=p.parse_args()
root=Path(__file__).resolve().parents[1];hb=str(Path(a.hb).resolve());script=root/'compat/mathutils_fuzz.py'
names=['euler_matrix','matrix_inverse','track_matrix','quaternion_rotate','quaternion_normalized','quaternion_conjugate','axis_rotation','matrix_compose','directional_scale','euler_roundtrip']
with tempfile.TemporaryDirectory() as directory:
    temp=Path(directory);reference=temp/'reference';reference.mkdir();native=temp/'native';native.mkdir()
    if not a.reference and not a.blender:p.error('--blender or --reference is required')
    commands=[] if a.reference else [([a.blender,'-b','--factory-startup','--python-exit-code','1','--python',str(script)],reference)]
    commands.append(([hb,'run',str(script)],native))
    for command,cwd in commands:
        r=subprocess.run(command,cwd=cwd,capture_output=True,text=True)
        if r.returncode:raise RuntimeError(r.stdout+'\n'+r.stderr)
    ref=json.loads((Path(a.reference) if a.reference else reference/'mathutils-fuzz.json').read_text());got=json.loads((native/'mathutils-fuzz.json').read_text())
assert len(ref)==len(got)==10000
stats={name:dict(operations=0,within_tolerance=0,bit_exact=0,max_absolute_error=0.) for name in names}
for left,right in zip(ref,got):
    assert len(left)==len(right)==10
    for name,x,y in zip(names,left,right):
        assert len(x)==len(y)
        pairs=list(zip(x,y));s=stats[name];s['operations']+=1
        s['bit_exact']+=all(a==b for a,b in pairs)
        s['within_tolerance']+=all(math.isclose(a,b,rel_tol=1e-6,abs_tol=1e-5) for a,b in pairs)
        s['max_absolute_error']=max(s['max_absolute_error'],*(abs(a-b) for a,b in pairs))
report=dict(reference='Blender 4.5.9 LTS',seed=20260908,scope='Six Euler orders, square matrices and quaternion rotations; tracking compared as rotation matrices, since q and -q represent the same rotation. Not full mathutils API parity.',operations=100000,absolute_tolerance=1e-5,relative_tolerance=1e-6,passed=all(s['within_tolerance']==s['operations'] for s in stats.values()),bit_exact=sum(s['bit_exact'] for s in stats.values()),by_operation=stats)
Path(a.out).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
raise SystemExit(0 if report['passed'] else 1)
