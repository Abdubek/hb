"""Resolve OBJ indices before comparing oriented polygons and corner attributes."""
from pathlib import Path
import math

def observe(path):
    path=Path(path);vertices=[];uvs=[];normals=[];materials={};objects={};current=None;material=None;smooth=False
    for raw in path.read_text().splitlines():
        words=raw.split()
        if not words or words[0].startswith('#'):continue
        op,args=words[0],words[1:]
        if op=='mtllib':
            name=None
            for line in path.with_name(' '.join(args)).read_text().splitlines():
                terms=line.split()
                if not terms or terms[0].startswith('#'):continue
                if terms[0]=='newmtl':name=' '.join(terms[1:]);materials[name]={}
                elif name is not None:materials[name][terms[0]]=[float(x) for x in terms[1:]]
        elif op=='o':current=' '.join(args);objects[current]={'vertices':0,'faces':[]}
        elif op=='v':vertices.append(tuple(map(float,args)));objects[current]['vertices']+=1
        elif op=='vt':uvs.append(tuple(map(float,args)))
        elif op=='vn':normals.append(tuple(map(float,args)))
        elif op=='usemtl':material=' '.join(args)
        elif op=='s':smooth=args[0] not in ('off','0')
        elif op=='f':
            corners=[]
            for token in args:
                refs=token.split('/')
                corners.append([vertices[int(refs[0])-1],uvs[int(refs[1])-1] if len(refs)>1 and refs[1] else None,normals[int(refs[2])-1] if len(refs)>2 and refs[2] else None])
            objects[current]['faces'].append({'corners':corners,'material':materials.get(material),'smooth':smooth})
    return objects

def compare(reference,actual):
    def close(a,b):
        if isinstance(a,(int,float)) and isinstance(b,(int,float)):return math.isclose(a,b,abs_tol=2e-5,rel_tol=0)
        if isinstance(a,(list,tuple)) and isinstance(b,(list,tuple)):return len(a)==len(b) and all(close(x,y) for x,y in zip(a,b))
        if isinstance(a,dict) and isinstance(b,dict):return set(a)==set(b) and all(close(a[k],b[k]) for k in a)
        return a==b
    assert set(reference)==set(actual),(set(reference),set(actual))
    for name,mesh in reference.items():
        other=actual[name];assert mesh['vertices']==other['vertices'],(name,'vertex count')
        remaining=list(other['faces']);assert len(mesh['faces'])==len(remaining),(name,'face count')
        for face in mesh['faces']:
            found=None
            for i,candidate in enumerate(remaining):
                if not close(face['material'],candidate['material']) or face['smooth']!=candidate['smooth']:continue
                corners=candidate['corners']
                if any(close(face['corners'],corners[j:]+corners[:j]) for j in range(len(corners))):found=i;break
            assert found is not None,(name,'oriented polygon/corner attributes',face)
            remaining.pop(found)
