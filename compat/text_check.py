import math,itertools

def compare(meshes,refs):
    assert len(meshes)==len(refs)
    fail=[]
    for i,(m,r) in enumerate(zip(meshes,refs)):
     try:
      assert len(m['vertices'])==len(r['vertices']),('vertices',len(m['vertices']),len(r['vertices']))
      assert len(m['faces'])==len(r['faces']),('faces',len(m['faces']),len(r['faces']))
      cells={};eps=1e-5
      def cell(v):return tuple(math.floor(x/eps) for x in v)
      for j,v in enumerate(r['vertices']):cells.setdefault(cell(v),[]).append(j)
      mapping={};used=set()
      for j,v in enumerate(m['vertices']):
       candidates=[];c=cell(v)
       for d in itertools.product((-1,0,1),repeat=3):
        for k in cells.get(tuple(c[z]+d[z] for z in range(3)),[]):
         if k not in used and max(abs(a-b) for a,b in zip(v,r['vertices'][k]))<=eps:candidates.append(k)
       assert candidates,('unmatched vertex',j,v)
       k=min(candidates,key=lambda k:sum((a-b)**2 for a,b in zip(v,r['vertices'][k])));mapping[j]=k;used.add(k)
      def boundaries(vertices,faces):
       edge={};area=0.
       for face in faces:
        assert len(face)==3
        a,b,c=[vertices[j] for j in face];cross=(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);assert cross>=-1e-12,('winding',cross)
        area+=cross/2
        for a,b in zip(face,face[1:]+face[:1]):edge[(a,b)]=edge.get((a,b),0)+1
       boundary=[]
       for (a,b),count in edge.items():
        assert count==1,('duplicate oriented edge',a,b,count)
        if (b,a) not in edge:boundary.append((a,b))
       return sorted(boundary),area
      nf=[[mapping[j] for j in face] for face in m['faces']]
      nb,na=boundaries(r['vertices'],nf);rb,ra=boundaries(r['vertices'],r['faces']);assert nb==rb,'boundary';assert abs(na-ra)<1e-5,('area',na,ra)
      expected_uv={};k=0
      for face in r['faces']:
       for j in face:expected_uv[j]=r['uv'][k];k+=1
      uv=m['uv_layers'][0]['data'] if m['uv_layers'] else [];assert len(uv)==len(r['uv']);k=0
      for face in m['faces']:
       for j in face:
        assert max(abs(a-b) for a,b in zip(uv[k],expected_uv[mapping[j]]))<=1e-5,('UV',uv[k],expected_uv[mapping[j]]);k+=1
     except Exception as exc:fail.append(dict(i=i,body=r['body'],res=r['res'],error=str(exc)))
    return fail
