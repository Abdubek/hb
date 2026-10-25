"""Text GLB comparison: filled topology and UVs, ignoring only zero-area normals."""
import json,struct
from pathlib import Path
from text_check import compare

def meshes(path,names):
    data=Path(path).read_bytes();length=struct.unpack_from('<I',data,12)[0];doc=json.loads(data[20:20+length]);buffer=data[28+length:]
    def read(index):
        a=doc['accessors'][index];v=doc['bufferViews'][a['bufferView']];n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];fmt={5121:'B',5123:'H',5125:'I',5126:'f'}[a['componentType']];size=struct.calcsize(fmt)*n;stride=v.get('byteStride',size);start=v.get('byteOffset',0)+a.get('byteOffset',0)
        return [struct.unpack_from('<'+fmt*n,buffer,start+i*stride) for i in range(a['count'])]
    output={}
    for node in doc['nodes']:
        if node.get('name') not in names:continue
        parts=[]
        for primitive in doc['meshes'][node['mesh']]['primitives']:
            positions=read(primitive['attributes']['POSITION']);normals=read(primitive['attributes']['NORMAL']);uv=read(primitive['attributes']['TEXCOORD_0']);indices=[v[0] for v in read(primitive['indices'])]
            vertices=[];mapping={};lookup={}
            for i,(p,t) in enumerate(zip(positions,uv)):
                key=(p,t)
                if key not in lookup:lookup[key]=len(vertices);vertices.append([p[0],-p[2],p[1]])
                mapping[i]=lookup[key]
            faces=[];corners=[]
            for start in range(0,len(indices),3):
                original=indices[start:start+3];face=[mapping[i] for i in original];a,b,c=[vertices[i] for i in face]
                area=(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
                if abs(area)>1e-12:
                    for i in original:assert max(abs(x-y) for x,y in zip(normals[i],(0.,1.,0.)))<=1e-5,('nondegenerate text normal',node['name'],normals[i])
                faces.append(face);corners += [list(uv[i]) for i in original]
            parts.append(dict(vertices=vertices,faces=faces,uv=corners,uv_layers=[dict(name='UVMap',data=corners)]))
        output[node['name']]=parts
    assert set(output)==set(names),'Missing declared Text GLB nodes'
    return output

def verify(reference,native,names):
    refs=meshes(reference,names);actual=meshes(native,names)
    for name in names:
        failures=compare(actual[name],[dict(r,body=name,res='GLB') for r in refs[name]])
        assert not failures,failures
