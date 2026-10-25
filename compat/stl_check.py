"""Fresh Blender versus CLI STL imports, including cleanup and corner normals."""
import json
from pathlib import Path
import subprocess
import tempfile
from normalize import revision
ROOT=Path(__file__).resolve().parent

def verify(hb,blender):
    def run(args):
        result=subprocess.run(list(map(str,args)),capture_output=True,text=True,timeout=120)
        assert result.returncode==0,(args,result.stdout,result.stderr)
    with tempfile.TemporaryDirectory() as directory:
        temp=Path(directory);reference=temp/'reference.json'
        run([blender,'-b','-t','1','--python-exit-code','1','--python',ROOT/'stl_reference.py','--',reference])
        oracle=json.loads(reference.read_text())
        for name,expected in oracle.items():
            scene=temp/(name+'.hb')
            run([hb,'import',ROOT/'fixtures/stl'/(name+'.stl'),'--scene',scene])
            snapshot=revision(scene)['scene'];mesh=snapshot['meshes'][0]
            assert snapshot['objects'][0]['name']==expected['name']
            assert mesh['name']==expected['mesh_name']
            for field in ('vertices','faces','smooth'):assert mesh[field]==expected[field],(name,field)
            assert {tuple(sorted(e)) for e in mesh['edges']}=={tuple(sorted(e)) for e in expected['edges']}
            assert len(mesh['uv_layers'])==expected['uv_layers']
            assert mesh['loop_normals']==[n for n in expected['normals'] for _ in range(3)]
    return {'fixtures':len(oracle),'checks':['float32 vertices','oriented triangles','undirected edges','corner normals including collinear +Z fallback','duplicate/repeated-vertex cleanup and remaining loose vertices','names, smoothing, absent UVs']}

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--hb',required=True);parser.add_argument('--blender',required=True);parser.add_argument('--out')
    args=parser.parse_args();result=verify(str(Path(args.hb).resolve()),args.blender)
    if args.out:Path(args.out).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
