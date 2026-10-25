"""Verify exact-input normals separately from composed BEVEL → WEIGHTED_NORMAL."""
import argparse,json,subprocess,tempfile,hashlib
from pathlib import Path
from normalize import revision
p=argparse.ArgumentParser();p.add_argument('--hb',required=True);p.add_argument('--reference',required=True);p.add_argument('--out',required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[1];binary=Path(a.hb).resolve()
reference=json.loads(Path(a.reference).read_text())

def run(code):
    with tempfile.TemporaryDirectory() as tmp:
        script=Path(tmp)/'weighted.py';script.write_text(code);scene=Path(tmp)/'scene.hb'
        result=subprocess.run([str(binary),'run',str(script),'--scene',str(scene)],capture_output=True,text=True)
        assert result.returncode==0,(result.stdout,result.stderr)
        return {m['name']:m['loop_normals'] for m in revision(scene)['scene']['meshes']}

def compare(actual,tolerance):
    assert set(actual)==set(reference['normals'])
    errors=[];count=0;maximum=0.
    for name,expected in reference['normals'].items():
        got=actual[name];assert len(got)==len(expected),(name,len(got),len(expected))
        for i,(x,y) in enumerate(zip(got,expected)):
            count+=1;error=max(abs(a-b) for a,b in zip(x,y));maximum=max(maximum,error)
            if error>tolerance:errors.append(dict(mesh=name,corner=i,error=error,reference=y,actual=x))
    return dict(meshes=len(actual),corners=count,max_absolute_error=maximum,tolerance=tolerance,passed=not errors,mismatch_count=len(errors),mismatches=errors[:100])

code='import bpy\n'
for case in reference['inputs']:
    code+=f"m=bpy.data.meshes.new({case['name']!r});m.from_pydata({case['vertices']!r},[],{case['faces']!r})\n"
    code+="o=bpy.data.objects.new(m.name,m);bpy.context.collection.objects.link(o);bpy.context.view_layer.objects.active=o\n"
    code+=f"for f,s in zip(m.polygons,{case['smooth']!r}):f.use_smooth=s\n"
    code+=f"w=o.modifiers.new('Weight','WEIGHTED_NORMAL');w.mode={case['mode']!r};w.keep_sharp={case['keep_sharp']!r};bpy.ops.object.modifier_apply(modifier=w.name)\n"
exact=compare(run(code),1e-5)
code=(root/'compat/golden/m2_weighted_normals.py').read_text()+'''
for obj in bpy.data.objects:
    bpy.context.view_layer.objects.active=obj
    while obj.modifiers:bpy.ops.object.modifier_apply(modifier=obj.modifiers[0].name)
'''
# Upstream bevel coordinates are approximate at float32 precision; packing
# normals can move a quantization step at these boundaries. The exact-input
# test isolates this modifier at 1e-5; composed normals use 1e-4. The separate
# golden verifier still requires exact exported vertex/index counts.
composed=compare(run(code),1e-4)
report=dict(blender=reference['blender'],engine_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),reference_sha256=hashlib.sha256(Path(a.reference).read_bytes()).hexdigest(),exact_input=exact,composed=composed,passed=exact['passed'] and composed['passed'])
Path(a.out).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:({x:y for x,y in v.items() if x!='mismatches'} if isinstance(v,dict) else v) for k,v in report.items()}))
raise SystemExit(0 if report['passed'] else 1)
