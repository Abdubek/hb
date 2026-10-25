"""Independent corpus export checks; never executes a source script.

Checks named scene structure, transforms, material parameters/assignments and
evaluated triangle counts/bounds. This is not a pixel or full topology oracle.
"""
import json
import math
import struct
from pathlib import Path

def read(path):
    data=Path(path).read_bytes()
    assert data[:4]==b'glTF' and struct.unpack_from('<I',data,4)[0]==2,'Invalid GLB'
    size=struct.unpack_from('<I',data,12)[0]
    return json.loads(data[20:20+size])

def matrix(node):
    if 'matrix' in node:return node['matrix']
    x,y,z,w=node.get('rotation',[0,0,0,1]);scale=node.get('scale',[1,1,1]);t=node.get('translation',[0,0,0])
    rows=[[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w),t[0]],
          [2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w),t[1]],
          [2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y),t[2]],
          [0,0,0,1]]
    for i in range(3):
        for j in range(3):rows[i][j]*=scale[j]
    return [rows[i%4][i//4] for i in range(16)]

def summary(doc):
    materials={}
    names=[]
    for m in doc.get('materials',[]):
        name=m.get('name','');assert name not in materials,'Duplicate material name'
        p=m.get('pbrMetallicRoughness',{})
        value=dict(base_color=p.get('baseColorFactor',[1,1,1,1]),metallic=p.get('metallicFactor',1),
                   roughness=p.get('roughnessFactor',1),emission=m.get('emissiveFactor',[0,0,0]),
                   alpha=m.get('alphaMode','OPAQUE'),double_sided=m.get('doubleSided',False),
                   extensions=m.get('extensions',{}))
        if value['alpha']=='MASK':value['alpha_cutoff']=m.get('alphaCutoff',.5)
        materials[name]=value;names.append(name)
    nodes={}
    for n in doc.get('nodes',[]):
        name=n.get('name','');assert name not in nodes,'Duplicate object name'
        node=dict(matrix=matrix(n),children=sorted(doc['nodes'][i].get('name','') for i in n.get('children',[])))
        if 'mesh' in n:
            primitives=[]
            for p in doc['meshes'][n['mesh']]['primitives']:
                position=doc['accessors'][p['attributes']['POSITION']]
                count=doc['accessors'][p['indices']]['count'] if 'indices' in p else position['count']
                primitives.append(dict(material=names[p['material']] if 'material' in p else None,
                    vertices=position['count'],indices=count,mode=p.get('mode',4),min=position['min'],max=position['max']))
            node['mesh']=sorted(primitives,key=lambda p:p['material'] or '')
        # Exporter-specific extras preserve editing metadata, not glTF behavior.
        if 'camera' in n:node['camera']={k:v for k,v in doc['cameras'][n['camera']].items() if k!='extras'}
        light=n.get('extensions',{}).get('KHR_lights_punctual')
        if light is not None:node['light']={k:v for k,v in doc['extensions']['KHR_lights_punctual']['lights'][light['light']].items() if k!='extras'}
        nodes[name]=node
    return dict(nodes=nodes,materials=materials)

def compare(reference,actual):
    errors=[]
    def visit(a,b,path):
        if isinstance(a,(float,int)) and isinstance(b,(float,int)):
            same=a==b if path.endswith(('.vertices','.indices','.mode')) else math.isclose(a,b,rel_tol=0,abs_tol=1e-5)
            if not same:errors.append(dict(path=path,reference=a,actual=b))
        elif isinstance(a,dict) and isinstance(b,dict):
            if set(a)!=set(b):errors.append(dict(path=path,missing=sorted(set(a)-set(b)),extra=sorted(set(b)-set(a))))
            for key in sorted(set(a)&set(b)):visit(a[key],b[key],path+'.'+key)
        elif isinstance(a,list) and isinstance(b,list):
            if len(a)!=len(b):errors.append(dict(path=path,reference_length=len(a),actual_length=len(b)))
            for i,(x,y) in enumerate(zip(a,b)):visit(x,y,path+f'[{i}]')
        elif a!=b:errors.append(dict(path=path,reference=a,actual=b))
    visit(summary(read(reference)),summary(read(actual)),'export')
    return dict(passed=not errors,mismatch_count=len(errors),mismatches=errors[:100])
