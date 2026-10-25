"""Exact indexed cuboid-bevel geometry, edges and corner UV reference checks."""
def compare(reference,scene):
    meshes={m['id']:m for m in scene['meshes']};objects={o['name']:o for o in scene['objects']};errors=[]
    for name,expected in reference.items():
     affect,segments,width,clamp=name.split('_')
     if (clamp=='False' and float(width)>=1) or (affect=='VERTICES' and int(segments)>1 and int(segments)%2):continue
     try:
      mesh=meshes[objects[name]['data']['id']]
      actual=dict(vertices=mesh['vertices'],faces=mesh['faces'],uv=mesh['uv_layers'][0]['data'],edges=mesh['edges'])
      for field in ('vertices','faces','uv'):
       a,b=expected[field],actual[field];assert len(a)==len(b),(field,len(a),len(b));delta=max([0]+[abs(x-y) for row,other in zip(a,b) for x,y in zip(row,other)])
       assert all(len(row)==len(other) for row,other in zip(a,b)),field
       assert delta<=(0 if field=='faces' else 1e-5),(field,delta)
      assert sorted(sorted(e) for e in expected['edges'])==sorted(sorted(e) for e in actual['edges']),'edges'
      pass
     except Exception as e:errors.append((name,str(e)))
    assert not errors,errors
