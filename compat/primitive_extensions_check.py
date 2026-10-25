import math,itertools
from equivalent import align_faces

def compare(refs,scene):
    meshes={m['id']:m for m in scene['meshes']};failures=[];passed=[]
    by_object={o['name']:meshes[o['data']['id']] for o in scene['objects']}
    def vertex_mapping(native,reference):
     cells={};eps=1e-5
     def cell(v):return tuple(math.floor(x/eps) for x in v)
     for i,v in enumerate(reference):cells.setdefault(cell(v),[]).append(i)
     used=set();mapping={}
     for i,v in enumerate(native):
      c=cell(v);candidates=[]
      for d in itertools.product((-1,0,1),repeat=3):
       for j in cells.get(tuple(c[k]+d[k] for k in range(3)),[]):
        if j not in used and all(abs(a-b)<=eps for a,b in zip(v,reference[j])):candidates.append(j)
      assert candidates,('unmatched vertex',i,v)
      j=min(candidates,key=lambda j:sum((a-b)**2 for a,b in zip(v,reference[j])));mapping[i]=j;used.add(j)
     return mapping
    
    def close(a,b,path):
     if isinstance(b,list):
      assert len(a)==len(b),(path,len(a),len(b))
      for i,(x,y) in enumerate(zip(a,b)):close(x,y,path+'.'+str(i))
     elif isinstance(b,(float,int)):assert abs(a-b)<=1e-5,(path,a,b)
     else:assert a==b,(path,a,b)
    for obj in scene['objects']:
     key=obj['name']
     if key not in refs:continue
     row=refs[key];ref=row['mesh'];mesh=meshes[obj['data']['id']];actual=dict(name='Probe',vertices=mesh['vertices'],faces=mesh['faces'],uv=mesh['uv_layers'][mesh['active_uv']]['data'] if mesh['uv_layers'] else [])
     record={**mesh,'name':'Probe'};a=dict(objects=[dict(name=key,mesh={**ref,'name':'Probe'})],meshes=[]);b=dict(objects=[dict(name=key,mesh=actual)],meshes=[record])
     try:
      if row['kind'] in ('uv_sphere','ico_sphere'):
       template_key=key
       if row['zero'] or row['kwargs'].get('scale')==[0,0,0]:
        template_key=next(k for k,v in refs.items() if v['kind']==row['kind'] and v['edit']==row['edit'] and not v['zero'] and v['kwargs'].get('scale')==[1,1,1])
       mapping=vertex_mapping(by_object[template_key]['vertices'],refs[template_key]['mesh']['vertices'])
       ordered=[None]*len(actual['vertices'])
       for i,j in mapping.items():ordered[j]=actual['vertices'][i]
       actual['vertices']=ordered;actual['faces']=[[mapping[v] for v in face] for face in actual['faces']]
       b=align_faces(a,b,('Probe',));actual=b['objects'][0]['mesh']
       compared_edges=[[mapping[v] for v in edge] for edge in mesh['edges']]
      else:compared_edges=mesh['edges']
      close(actual['vertices'],ref['vertices'],key+'.vertices');close(actual['faces'],ref['faces'],key+'.faces');close(actual['uv'],ref['uv'],key+'.uv')
      assert sorted(tuple(sorted(e)) for e in compared_edges)==sorted(tuple(sorted(e)) for e in ref['edges']),(key,'edges')
      passed.append(key)
     except Exception as e:failures.append(dict(key=key,kind=row['kind'],edit=row['edit'],zero=row['zero'],scale=row['kwargs'].get('scale'),error=str(e)))
    return passed,failures
