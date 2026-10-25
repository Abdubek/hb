"""Compare actual Blender imports of reference and hb USDZ packages."""
import json
import math
from pathlib import Path
import subprocess
import tempfile
from obj_semantics import compare

ROOT = Path(__file__).resolve().parent

def verify(hb, blender):
    def run(args):
        result = subprocess.run(list(map(str,args)),capture_output=True,text=True,timeout=120)
        assert result.returncode == 0,(args,result.stdout,result.stderr)
    def reference(helper, *args):
        run([blender,'-b','-t','1','--python-exit-code','1','--python',ROOT/helper,'--',*args])
    def close(a,b):
        if isinstance(a,(int,float)):
            assert math.isclose(a,b,rel_tol=0,abs_tol=1e-5),(a,b)
        elif isinstance(a,list):
            assert len(a)==len(b)
            for x,y in zip(a,b):close(x,y)
        elif isinstance(a,dict):
            assert set(a)==set(b)
            for key in a:close(a[key],b[key])
        else:assert a==b,(a,b)
    with tempfile.TemporaryDirectory() as directory:
        temp=Path(directory)
        for name,fixture,observer in [('scene','m3_format_usdz.py','usdz_scene.py'),('texture','m3_format_usdz_texture.py','usdz_textures.py')]:
            source=ROOT/'golden'/fixture;oracle=temp/(name+'-reference.usdz');native=temp/(name+'-native.usdz')
            reference('usdz_export.py',source,oracle)
            run([hb,'run',source,'--scene',temp/(name+'.hb'),'--out',native])
            left=temp/(name+'-reference.json');right=temp/(name+'-native.json')
            reference(observer,oracle,left);reference(observer,native,right)
            a=json.loads(left.read_text());b=json.loads(right.read_text())
            if name=='scene':
                compare({k:v for k,v in a.items() if k.startswith('mesh')},{k:v for k,v in b.items() if k.startswith('mesh')})
                assert set(a)==set(b)
                for key in a:
                    close(a[key]['world'],b[key]['world'])
                    if not key.startswith('mesh'):close(a[key],b[key])
            else:
                close(a['Base Color'],b['Base Color'])
                close(a['Alpha']['size'],b['Alpha']['size'])
                close(a['Alpha']['pixels'][3::4],b['Alpha']['pixels'][3::4])
        ortho=temp/'ortho.usdz';observed=temp/'ortho.json'
        run([hb,'run',ROOT/'golden/m3_format_usdz_ortho.py','--scene',temp/'ortho.hb','--out',ortho])
        reference('usdz_scene.py',ortho,observed)
        camera=json.loads(observed.read_text())['camera_ORTHO']
        close(camera['ortho_scale'],60)  # Blender 4.5's measured 10x import-unit defect.
        close(camera['shift_x'],.1);close(camera['shift_y'],-.2)
        close(camera['near'],.2);close(camera['far'],300)
    return {'packages':3,'blender_imports':5,'orthographic':'standard USD units; measured Blender 4.5 10x import deviation', 'checks':['mesh world transforms and oriented polygons','UV/normal corners and scalar materials','camera/light values','embedded float PNG color and alpha pixels']}

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--hb',required=True);parser.add_argument('--blender',required=True);parser.add_argument('--out')
    args=parser.parse_args();result=verify(str(Path(args.hb).resolve()),args.blender)
    if args.out:Path(args.out).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
