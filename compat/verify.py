"""Compare actual hb outputs with real Blender, including both GLB exports."""
import argparse
import json
import math
from pathlib import Path
import struct
import subprocess
import tempfile
from normalize import revision, normalize
from equivalent import align, align_faces, declarations
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--hb',default='target/release/hb');p.add_argument('--blender',required=True);p.add_argument('--legacy-blender',default='/opt/blender-legacy/blender');p.add_argument('--corpus',action='store_true');p.add_argument('--script',action='append',type=Path,help='Run a specific golden; repeat for a focused increment');p.add_argument('--out',default='compat/golden-report.json');a=p.parse_args()
hb=str(Path(a.hb).resolve())
def close(a,b,path=''):
    if isinstance(a,(float,int)) and isinstance(b,(float,int)):
        assert math.isclose(a,b,rel_tol=0,abs_tol=1e-5),(path,a,b)
    elif isinstance(a,list):
        assert len(a)==len(b),(path,len(a),len(b))
        for i,(x,y) in enumerate(zip(a,b)):close(x,y,path+f'[{i}]')
    elif isinstance(a,dict):
        assert set(a)==set(b),(path,set(a),set(b))
        for k in a:close(a[k],b[k],path+'.'+k)
    else: assert a==b,(path,a,b)
def glb(path):
    data=Path(path).read_bytes();length=struct.unpack_from('<I',data,12)[0];return json.loads(data[20:20+length])
def glb_summary(doc):
    result={}
    for n in doc.get('nodes',[]):
        if 'matrix' in n:matrix=n['matrix']
        else:
            x,y,z,w=n.get('rotation',[0,0,0,1]);sc=n.get('scale',[1,1,1]);t=n.get('translation',[0,0,0])
            rows=[[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w),t[0]],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w),t[1]],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y),t[2]],[0,0,0,1]]
            for i in range(3):
                for j in range(3):rows[i][j]*=sc[j]
            matrix=[rows[i%4][i//4] for i in range(16)]
        node=dict(matrix=matrix,children=sorted(doc['nodes'][i]['name'] for i in n.get('children',[])))
        if 'mesh' in n:
            prims=[]
            for prim in doc['meshes'][n['mesh']]['primitives']:
                pos=doc['accessors'][prim['attributes']['POSITION']]
                count=doc['accessors'][prim['indices']]['count'] if 'indices' in prim else pos['count']
                prims.append(dict(vertices=pos['count'],indices=count,min=pos['min'],max=pos['max']))
            node['mesh']=prims
        result[n['name']]=node
    return result
def glb_material_summary(doc,names):
    materials={m.get('name'):m for m in doc.get('materials',[])}
    result={}
    for name in names:
        assert name in materials,('missing exported material',name)
        m=materials[name];p=m.get('pbrMetallicRoughness',{})
        strength=m.get('extensions',{}).get('KHR_materials_emissive_strength',{}).get('emissiveStrength',1)
        result[name]=dict(base=p.get('baseColorFactor',[1,1,1,1]),metallic=p.get('metallicFactor',1),roughness=p.get('roughnessFactor',1),alpha_mode=m.get('alphaMode','OPAQUE'),cutoff=m.get('alphaCutoff',.5),double_sided=m.get('doubleSided',False),emission=[x*strength for x in m.get('emissiveFactor',[0,0,0])])
    return result
scripts=[s.resolve() for s in a.script] if a.script else list(sorted((ROOT/'compat/golden').glob('*.py')))
if a.corpus:scripts+=list(sorted((ROOT/'compat/seed-corpus').glob('*.py')))
verified=[];unsupported=[];reference_versions={}
with tempfile.TemporaryDirectory() as temp:
    tmp=Path(temp);requests=[]
    for script in scripts:
        output=tmp/(script.stem+'.json')
        checked=subprocess.run([hb,'check',str(script)],capture_output=True,text=True)
        if script.parent.name=='seed-corpus' and checked.returncode:
            unsupported.append(script.name)
            requests.append(dict(script=str(script),output=str(output),supported=False))
            continue
        run=subprocess.run([hb,'run',str(script),'--scene',str(tmp/(script.stem+'.hb')),'--out',str(tmp/(script.stem+'.glb'))],capture_output=True,text=True)
        assert run.returncode==0,(script,run.stdout,run.stderr)
        requests.append(dict(script=str(script),output=str(output),supported=True))
    for version,binary in [('current',a.blender),('3.6',a.legacy_blender)]:
        group=[item for item in requests if ('3.6' in declarations(Path(item['script']),'HB_BLENDER_REFERENCE'))==(version=='3.6')]
        if not group:continue
        request_file=tmp/(version+'-requests.json');request_file.write_text(json.dumps(group))
        ref=subprocess.run([binary,'-b','--factory-startup','--python-exit-code','1','--python',str(ROOT/'compat/reference_batch.py'),'--',str(request_file)],capture_output=True,text=True)
        if ref.returncode:raise RuntimeError(ref.stdout+'\n'+ref.stderr)
    for item in requests:
        reference=json.loads(Path(item['output']).read_text())
        if not item['supported']: continue
        name=Path(item['script']).stem
        snapshot=revision(tmp/(name+'.hb'))['scene']
        reference_versions[Path(item['script']).name]=reference.pop('blender_version',None)
        normalized=align(reference,normalize(snapshot),declarations(Path(item['script'])))
        normalized=align_faces(reference,normalized,declarations(Path(item['script']),'HB_FACE_ORDER_MESH_PREFIXES'))
        close(reference,normalized,name)
        def f32_tree(v):
            if isinstance(v,float):return struct.unpack('f',struct.pack('f',v))[0]
            if isinstance(v,list):return [f32_tree(x) for x in v]
            if isinstance(v,dict):return {k:f32_tree(x) for k,x in v.items()}
            return v
        assert f32_tree(reference['materials'])==f32_tree(normalized['materials']),(name,'float32 material parameters')
        reference_glb=glb_summary(glb(item['output']+'.glb'));native_glb=glb_summary(glb(tmp/(name+'.glb')))
        text_nodes=declarations(Path(item['script']),'HB_GLTF_TEXT_NODES')
        if text_nodes:
            from text_glb_check import verify as verify_text_glb
            verify_text_glb(item['output']+'.glb',tmp/(name+'.glb'),text_nodes)
            # Full Text geometry/UV/normal comparison above permits only splits
            # caused by normals on zero-area triangles, not arbitrary count drift.
            for node in text_nodes:
                for part in reference_glb[node]['mesh']+native_glb[node]['mesh']:part.pop('vertices')
        close(reference_glb,native_glb,name+'.glb')
        material_names=declarations(Path(item['script']),'HB_GLTF_MATERIAL_NAMES')
        if material_names:close(glb_material_summary(glb(item['output']+'.glb'),material_names),glb_material_summary(glb(tmp/(name+'.glb')),material_names),name+'.glb.materials')
        verified.append(Path(item['script']).name)
report=dict(blender_version='4.5.9 LTS',blender_reference_versions=reference_versions,blender_reference_runs=len(requests),verified=len(verified),unsupported=len(unsupported),verified_scripts=verified,unsupported_scripts=unsupported,checks=['object names and linked membership','selection','persistent ARRAY/MIRROR/SOLIDIFY/TRIANGULATE/BEVEL/WELD/BOOLEAN/SUBSURF descriptors and evaluated GLB export (Blender export_apply=True)','float32 transforms at 1e-5','exact indexed topology/UV loops except documented mesh-index and extrusion face-order equivalence; connectivity, winding and attributes remain checked','bit-exact float32 material/node parameters; cameras, lights, collections and image pixels','GLB node names/hierarchy/transforms and vertex/index counts/bounds'])
if any(s.name=='m3_format_usdz.py' for s in scripts):
    from usdz_check import verify as verify_usdz
    report['usdz_interoperability']=verify_usdz(hb,a.blender)
if not a.script:
    from stl_check import verify as verify_stl
    report['stl_interoperability']=verify_stl(hb,a.blender)
    from ply_check import verify as verify_ply
    report['ply_interoperability']=verify_ply(hb,a.blender)
Path(a.out).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if not k.endswith('_scripts')}))
