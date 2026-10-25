"""Check positions, oriented topology, UVs, colors, crease values and normals.

The preserved reference includes three explicitly rejected normal combinations.
All positive probes retain 1e-5 geometry/color/crease and 1e-4 normal tolerances.
"""
import itertools,math
def compare(reference,scene):
    meshes={m['id']:m for m in scene['meshes']};objects={o['name']:o for o in scene['objects']}
    failures=[];max_normal=0
    for name,r in reference.items():
     if name in ('custom_4_False_preserve','custom_4_True_preserve','smooth_preserved'):continue
     try:
      m=meshes[objects[name]['data']['id']];vs=m['vertices'];rv=r['vertices'];assert len(vs)==len(rv),('vertex count',len(vs),len(rv));eps=1e-5;cells={}
      def cell(v):return tuple(math.floor(x/eps) for x in v)
      for i,v in enumerate(rv):cells.setdefault(cell(v),[]).append(i)
      mapping={};used=set()
      for i,v in enumerate(vs):
       c=cell(v);candidates=[]
       for d in itertools.product((-1,0,1),repeat=3):
        for j in cells.get(tuple(c[k]+d[k] for k in range(3)),[]):
         if j not in used and all(abs(a-b)<=eps for a,b in zip(v,rv[j])):candidates.append(j)
       assert candidates,('position',i,v)
       j=min(candidates,key=lambda j:sum((a-b)**2 for a,b in zip(v,rv[j])));mapping[i]=j;used.add(j)
      def facekey(f):
       i=f.index(min(f));return tuple(f[i:]+f[:i])
      rf={facekey(f):i for i,f in enumerate(r['faces'])};assert len(m['faces'])==len(rf),'face count';starts=[];offset=0
      for f in r['faces']:starts.append(offset);offset+=len(f)
      used=set();offset=0
      for f in m['faces']:
       mapped=[mapping[v] for v in f];key=facekey(mapped);assert key in rf,('face winding',mapped)
       j=rf[key];assert j not in used;used.add(j);start=mapped.index(r['faces'][j][0])
       for k in range(len(f)):
        a=offset+(start+k)%len(f);b=starts[j]+k
        for field,values in [('uv',m['uv_layers'][0]['data'] if m['uv_layers'] else []),('normals',m['loop_normals']),('colors',m['colors'])]:
         if r[field]:
          assert values,('missing',field)
          delta=max(abs(x-y) for x,y in zip(values[a],r[field][b]))
          if field=='normals':max_normal=max(max_normal,delta)
          assert delta<=(1e-4 if field=='normals' else 1e-5),(field,delta,values[a],r[field][b])
       offset+=len(f)
      actual_edges={tuple(sorted(mapping[v] for v in e)):i for i,e in enumerate(m['edges'])};expected_edges={tuple(sorted(e)):i for i,e in enumerate(r['edges'])};assert actual_edges.keys()==expected_edges.keys(),'edge connectivity'
      if 'crease_vert' in r['creases']:
       for i,j in mapping.items():assert abs(m['crease_vert'][i]-r['creases']['crease_vert'][j])<=1e-5,'vertex crease'
      if 'crease_edge' in r['creases']:
       for edge,i in actual_edges.items():assert abs(m['crease_edge'][i]-r['creases']['crease_edge'][expected_edges[edge]])<=1e-5,'edge crease'
      pass
     except Exception as e:failures.append((name,str(e)))
    assert not failures,failures
    return max_normal
