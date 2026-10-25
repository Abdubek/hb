"""PLY reference checks preserve topology/UVs and measure color/normal precision."""
import json,math
from pathlib import Path
import subprocess,tempfile
from normalize import revision
ROOT=Path(__file__).resolve().parent

def close(a,b,tolerance=1e-6):
    if isinstance(a,(int,float)):
        assert math.isclose(a,b,abs_tol=tolerance,rel_tol=0),(a,b,tolerance)
    elif isinstance(a,list):
        assert len(a)==len(b),(len(a),len(b))
        for x,y in zip(a,b):close(x,y,tolerance)
    elif isinstance(a,dict):
        assert set(a)==set(b)
        for key in a:close(a[key],b[key],tolerance)
    else:assert a==b,(a,b)

def compare(snapshot,expected):
    mesh=snapshot['meshes'][0]
    assert snapshot['objects'][0]['name']==expected['name']
    assert mesh['name']==expected['mesh_name']
    for field in ('vertices','faces','smooth'):assert mesh[field]==expected[field],field
    assert {tuple(sorted(e)) for e in mesh['edges']}=={tuple(sorted(e)) for e in expected['edges']}
    close(mesh['uv_layers'],expected['uv_layers'])
    if expected['custom_normals']:close(mesh['loop_normals'],expected['normals'],5e-5)
    else:assert not mesh['loop_normals']
    if expected['colors']:
        points=expected['colors'][0]['data'];close(mesh['colors'],[points[i] for face in mesh['faces'] for i in face])
    else:assert not mesh['colors']

def verify(hb,blender):
    def run(args):
        result=subprocess.run(list(map(str,args)),capture_output=True,text=True,timeout=120)
        assert result.returncode==0,(args,result.stdout,result.stderr)
    with tempfile.TemporaryDirectory() as directory:
        temp=Path(directory);reference=temp/'reference.json'
        run([blender,'-b','-t','1','--python-exit-code','1','--python',ROOT/'ply_reference.py','--',reference])
        oracle=json.loads(reference.read_text())
        for name,expected in oracle.items():
            scene=temp/(name+'.hb')
            run([hb,'import',ROOT/'fixtures/ply'/(name+'.ply'),'--scene',scene])
            compare(revision(scene)['scene'],expected)
    return {'fixtures':len(oracle),'checks':['exact float32 positions, indexed oriented polygons and undirected edges','UV corners','sRGB vertex colors within 1e-6','custom normals within 5e-5 of Blender quantization','cleanup retains loose edges','ASCII and both binary byte orders']}

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--hb',required=True);parser.add_argument('--blender',required=True);parser.add_argument('--out')
    args=parser.parse_args();result=verify(str(Path(args.hb).resolve()),args.blender)
    if args.out:Path(args.out).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
