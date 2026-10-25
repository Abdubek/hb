"""Opt-in comparisons for documented sphere indices and extrusion face order.

Sphere positions require a bijection within 1e-5. Extrusion comparison preserves
vertex indices and coordinates. Both check oriented faces and corner attributes;
non-opted-in meshes retain exact indexed comparison.
"""
import ast
import copy
import itertools
import math

def declarations(script, field='HB_EQUIVALENT_MESH_PREFIXES'):
    for node in ast.parse(script.read_text()).body:
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id==field for t in node.targets):
            return tuple(ast.literal_eval(node.value))
    return ()

def align(reference,native,prefixes):
    native=copy.deepcopy(native)
    by_name={m['name']:m for m in native['meshes']}
    refs={o['name']:o for o in reference['objects']}
    aligned=set()
    for obj in native['objects']:
        mesh=obj['mesh']
        if mesh is None or not any(mesh['name']==p or mesh['name'].startswith(p+'.') for p in prefixes):continue
        ref=refs[obj['name']]['mesh'];vs=mesh['vertices'];rv=ref['vertices']
        assert len(vs)==len(rv),(obj['name'],'vertex count')
        eps=1e-5;cells={}
        def cell(v):return tuple(math.floor(x/eps) for x in v)
        for i,v in enumerate(rv):cells.setdefault(cell(v),[]).append(i)
        mapping={};used=set()
        for i,v in enumerate(vs):
            c=cell(v);candidates=[]
            for d in itertools.product((-1,0,1),repeat=3):
                for j in cells.get(tuple(c[k]+d[k] for k in range(3)),[]):
                    if j not in used and all(abs(a-b)<=eps for a,b in zip(v,rv[j])):candidates.append(j)
            assert candidates,(obj['name'],'unmatched vertex',i,v)
            j=min(candidates,key=lambda j:sum((a-b)**2 for a,b in zip(v,rv[j])))
            mapping[i]=j;used.add(j)
        ordered=[None]*len(vs)
        for i,j in mapping.items():ordered[j]=vs[i]
        def key(face):
            i=face.index(min(face));return tuple(face[i:]+face[:i])
        rf={key(f):i for i,f in enumerate(ref['faces'])}
        assert len(rf)==len(ref['faces']),'Equivalent sphere faces must be unique'
        assert len(mesh['faces'])==len(ref['faces']),(obj['name'],'face count')
        face_order=[None]*len(rf);corner_order=[None]*len(rf);offset=0
        for i,face in enumerate(mesh['faces']):
            mapped=[mapping[v] for v in face];k=key(mapped)
            assert k in rf,(obj['name'],'connectivity/winding',mapped)
            j=rf[k];assert face_order[j] is None,'Duplicate face'
            start=mapped.index(ref['faces'][j][0]);order=list(range(len(face)));order=order[start:]+order[:start]
            face_order[j]=i;corner_order[j]=[offset+t for t in order];offset+=len(face)
        corners=[c for group in corner_order for c in group]
        mesh['vertices']=ordered;mesh['faces']=copy.deepcopy(ref['faces'])
        if mesh['uv']:mesh['uv']=[mesh['uv'][i] for i in corners]
        if mesh['name'] not in aligned:
            record=by_name[mesh['name']]
            if record.get('deform_weights'):
                weights=[None]*len(vs)
                for i,j in mapping.items():weights[j]=record['deform_weights'][i]
                record['deform_weights']=weights
            for field in ('material_indices','smooth'):record[field]=[record[field][i] for i in face_order]
            for layer in record['uv_layers']:layer['data']=[layer['data'][i] for i in corners]
            aligned.add(mesh['name'])
    return native


def align_faces(reference,native,prefixes):
    """Only face order/cyclic corner starts may change; vertex indices stay exact."""
    native=copy.deepcopy(native);refs={o['name']:o for o in reference['objects']}
    records={m['name']:m for m in native['meshes']};done=set()
    def key(face):
        start=face.index(min(face));return tuple(face[start:]+face[:start])
    for obj in native['objects']:
        mesh=obj['mesh']
        if mesh is None or not any(mesh['name']==p or mesh['name'].startswith(p+'.') for p in prefixes):continue
        ref=refs[obj['name']]['mesh']
        assert len(mesh['vertices'])==len(ref['vertices']),'Vertex count changed'
        assert len(mesh['faces'])==len(ref['faces']),'Face count changed'
        lookup={key(f):i for i,f in enumerate(ref['faces'])}
        assert len(lookup)==len(ref['faces']),'Duplicate reference face'
        order=[None]*len(lookup);corners=[None]*len(lookup);oriented=[None]*len(lookup);offset=0
        for i,face in enumerate(mesh['faces']):
            k=key(face);assert k in lookup,'Connectivity or winding changed'
            j=lookup[k];assert order[j] is None,'Duplicate native face'
            start=face.index(ref['faces'][j][0]);ids=list(range(offset,offset+len(face)))
            order[j]=i;corners[j]=ids[start:]+ids[:start];oriented[j]=face[start:]+face[:start];offset+=len(face)
        indices=[c for group in corners for c in group]
        mesh['faces']=oriented
        if mesh['uv']:mesh['uv']=[mesh['uv'][i] for i in indices]
        if mesh['name'] not in done:
            record=records[mesh['name']]
            for field in ('material_indices','smooth'):record[field]=[record[field][i] for i in order]
            for layer in record['uv_layers']:layer['data']=[layer['data'][i] for i in indices]
            done.add(mesh['name'])
    return native
