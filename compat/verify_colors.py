"""Check Color arithmetic and factory color-space behavior against Blender."""
import argparse,hashlib,json,math,subprocess,tempfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--hb',required=True);p.add_argument('--blender');p.add_argument('--reference');p.add_argument('--out',required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[1];script=root/'compat/color_fuzz.py';binary=Path(a.hb).resolve()
names=['rgb_hsv','hsv_rgb','hue_set','saturation_set','value_set','add','subtract','multiply','divide','aces_to_linear','linear_to_aces','rec709_to_linear','linear_to_rec709','xyz_to_linear','linear_to_xyz','srgb_to_linear','linear_to_srgb']
with tempfile.TemporaryDirectory() as tmp:
    tmp=Path(tmp);native=tmp/'native';native.mkdir();ref=tmp/'reference';ref.mkdir()
    commands=[]
    if not a.reference:
        if not a.blender:p.error('--blender or --reference required')
        commands.append(([a.blender,'-b','--factory-startup','--python-exit-code','1','--python',str(script)],ref))
    commands.append(([str(binary),'run',str(script)],native))
    for command,cwd in commands:
        result=subprocess.run(command,cwd=cwd,capture_output=True,text=True)
        assert result.returncode==0,(result.stdout,result.stderr)
    expected=json.loads((Path(a.reference) if a.reference else ref/'color-fuzz.json').read_text());actual=json.loads((native/'color-fuzz.json').read_text())
assert len(expected)==len(actual)==2000
stats={name:dict(operations=0,bit_exact=0,within_tolerance=0,max_absolute_error=0.) for name in names}
for reference,result in zip(expected,actual):
    assert len(reference)==len(result)==len(names)
    for name,x,y in zip(names,reference,result):
        assert len(x)==len(y)==3;s=stats[name];s['operations']+=1
        s['bit_exact']+=x==y;s['max_absolute_error']=max(s['max_absolute_error'],*(abs(a-b) for a,b in zip(x,y)))
        s['within_tolerance']+=all(math.isclose(a,b,abs_tol=1e-5,rel_tol=1e-6) for a,b in zip(x,y))
report=dict(reference='Blender 4.5.9 factory configuration',seed=20260908,engine_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),operations=34000,absolute_tolerance=1e-5,relative_tolerance=1e-6,passed=all(s['operations']==s['within_tolerance'] for s in stats.values()),by_operation=stats)
Path(a.out).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));raise SystemExit(0 if report['passed'] else 1)
