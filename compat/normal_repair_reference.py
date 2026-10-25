import bpy,bmesh,json,itertools
from pathlib import Path
out={}
for shape,flip,selection in itertools.product(('quad','grid','open_cube','cube'),('none','all','alternating'),('all','first','first2')):
 bm=bmesh.new()
 if shape in ('quad','grid'):bmesh.ops.create_grid(bm,x_segments=1 if shape=='quad' else 2,y_segments=1 if shape=='quad' else 2,size=1)
 else:bmesh.ops.create_cube(bm,size=2)
 if shape=='open_cube':bmesh.ops.delete(bm,geom=[list(bm.faces)[-1]],context='FACES_ONLY')
 for i,f in enumerate(bm.faces):
  if flip=='all' or (flip=='alternating' and i%2):f.normal_flip()
 for seq in (bm.verts,bm.edges,bm.faces):seq.index_update()
 fs=list(bm.faces);sel=fs if selection=='all' else fs[:1] if selection=='first' else fs[:2]
 src=dict(vertices=[list(v.co) for v in bm.verts],edges=[[v.index for v in e.verts] for e in bm.edges],faces=[[v.index for v in f.verts] for f in bm.faces],selected=[f.index for f in sel])
 bmesh.ops.recalc_face_normals(bm,faces=sel)
 out[f'{shape}_{flip}_{selection}']=dict(source=src,faces=[[v.index for v in f.verts] for f in bm.faces],normals=[list(f.normal) for f in bm.faces])
 bm.free()
Path('/results/reference.json').write_text(json.dumps(out,indent=2)+'\n')
