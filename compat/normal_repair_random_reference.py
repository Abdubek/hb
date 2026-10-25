import bpy,bmesh,json,random
from mathutils import Matrix,Vector
from pathlib import Path
rng=random.Random(731)
out={}
for case in range(80):
 bm=bmesh.new();bmesh.ops.create_grid(bm,x_segments=2,y_segments=2,size=1)
 bmesh.ops.triangulate(bm,faces=list(bm.faces))
 mat=Matrix.Translation([rng.uniform(-5,5) for _ in range(3)]) @ Matrix.Rotation(rng.uniform(-3,3),4,'X') @ Matrix.Rotation(rng.uniform(-3,3),4,'Y')
 for v in bm.verts:
  v.co.z=rng.uniform(-.25,.25);v.co=mat@v.co
 for f in bm.faces:
  if rng.random()<.5:f.normal_flip()
 for seq in (bm.verts,bm.edges,bm.faces):seq.index_update()
 selected=[f for f in bm.faces if rng.random()<.6]
 source=dict(vertices=[list(v.co) for v in bm.verts],edges=[[v.index for v in e.verts] for e in bm.edges],faces=[[v.index for v in f.verts] for f in bm.faces],selected=[f.index for f in selected])
 bm.normal_update()
 bmesh.ops.recalc_face_normals(bm,faces=selected)
 out[str(case)]=dict(source=source,faces=[[v.index for v in f.verts] for f in bm.faces],normals=[list(f.normal) for f in bm.faces])
 bm.free()
Path('/results/random-reference.json').write_text(json.dumps(out,indent=2)+'\n')
