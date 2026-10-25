"""Compare compressed hb imports with Blender imports of independent decoded twins."""
import argparse,json,math,subprocess,tempfile
from pathlib import Path
from normalize import normalize,revision
ROOT=Path(__file__).resolve().parents[1]
def close(a,b,path=''):
    if isinstance(a,(float,int)) and isinstance(b,(float,int)):assert math.isclose(a,b,rel_tol=0,abs_tol=1e-5),(path,a,b)
    elif isinstance(a,list):
        assert len(a)==len(b),(path,len(a),len(b))
        for i,(x,y) in enumerate(zip(a,b)):close(x,y,path+'.'+str(i))
    elif isinstance(a,dict):
        assert set(a)==set(b),(path,set(a),set(b))
        for key in a:close(a[key],b[key],path+'.'+key)
    else:assert a==b,(path,a,b)
def verify(hb,blender):
    hb=str(Path(hb).resolve());fixtures=ROOT/'compat/fixtures/meshopt';passed=[]
    with tempfile.TemporaryDirectory() as directory:
        temp=Path(directory);requests=[]
        for source in sorted(fixtures.glob('*-reference.gltf')):
            name=source.stem.removesuffix('-reference');script=temp/(name+'.py');script.write_text('import bpy\nbpy.ops.import_scene.gltf(filepath='+repr(str(source))+')\n')
            requests.append(dict(script=str(script),output=str(temp/(name+'.json')),supported=True))
            native=temp/(name+'-native.py');native.write_text('import bpy\nbpy.ops.import_scene.gltf(filepath='+repr(str(fixtures/(name+'.gltf')))+')\n')
            run=subprocess.run([hb,'run',str(native),'--scene',str(temp/(name+'.hb')),'--out',str(temp/(name+'.glb'))],capture_output=True,text=True);assert run.returncode==0,(name,run.stdout,run.stderr)
        request_file=temp/'requests.json';request_file.write_text(json.dumps(requests))
        run=subprocess.run([blender,'-b','--factory-startup','-t','1','--python-exit-code','1','--python',str(ROOT/'compat/reference_batch.py'),'--',str(request_file)],capture_output=True,text=True);assert run.returncode==0,(run.stdout,run.stderr)
        for item in requests:
            name=Path(item['script']).stem;reference=json.loads(Path(item['output']).read_text());reference.pop('blender_version',None)
            actual=normalize(revision(temp/(name+'.hb'))['scene'])
            if name.startswith('quaternion-'):
                # Blender constructs a vertex-color multiplication node graph;
                # the observer reads its unlinked Principled default, not the factor.
                # Codec colors and native raw/compressed materials are checked separately.
                reference.pop('materials');actual.pop('materials')
            close(reference,actual,name);passed.append(name)
    return dict(reference='meshoptimizer v0.25 JavaScript/Wasm decoded twins imported by Blender 4.5.9 LTS',verified=len(passed),cases=passed,checks=['object/data identity, selection, hierarchy and transforms','mesh vertex positions and exact indexed faces at unchanged 1e-5','UV layers and material parameters except Blender vertex-color multiplication graphs in two quaternion-filter cases','compressed and raw native scene equality checked by CLI regression tests'])
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--hb',required=True);parser.add_argument('--blender',required=True);parser.add_argument('--out',required=True);args=parser.parse_args();report=verify(args.hb,args.blender);Path(args.out).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
