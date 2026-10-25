"""DISPLACE positions, unchanged topology and remapped corner-normal checks."""
def compare(reference,scene):
    meshes={m['id']:m for m in scene['meshes']};objects={o['name']:o for o in scene['objects']};failures=[]
    for name,ref in reference.items():
     try:
      m=meshes[objects[name]['data']['id']]
      for field,other in [('vertices',m['vertices']),('normals',m['loop_normals'])]:
       assert len(ref[field])==len(other),(field,'count')
       delta=max([0]+[abs(x-y) for a,b in zip(ref[field],other) for x,y in zip(a,b)])
       assert delta<=(1e-4 if field=='normals' else 1e-5),(field,delta)
      assert m['faces']==ref['faces']
      pass
     except Exception as e:failures.append((name,str(e)))
    assert not failures,failures
