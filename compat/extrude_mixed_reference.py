import bpy,bmesh,json,itertools
from pathlib import Path
out={}
for shape,selection,keep in itertools.product(('quad','cube','wire'),('faces','face_edges','all','edges','verts','edge0','vert0'),(False,True)):
 bm=bmesh.new()
 if shape=='quad':bmesh.ops.create_grid(bm,x_segments=1,y_segments=1,size=1)
 elif shape=='cube':bmesh.ops.create_cube(bm,size=2)
 else:
  vs=[bm.verts.new(p) for p in ((0,0,0),(1,0,0),(1,1,0),(3,0,0))];bm.edges.new(vs[:2]);bm.edges.new(vs[1:3])
 for seq in (bm.verts,bm.edges,bm.faces):seq.ensure_lookup_table();seq.index_update()
 faces=list(bm.faces)[:1]
 if selection=='faces':geom=faces
 elif selection=='face_edges':geom=faces+list(faces[0].edges) if faces else []
 elif selection=='all':geom=list(bm.verts)+list(bm.edges)+faces
 elif selection=='edges':geom=list(bm.edges)
 elif selection=='verts':geom=list(bm.verts)
 elif selection=='edge0':geom=list(bm.edges)[:1]
 else:geom=list(bm.verts)[:1]
 source=dict(vertices=[list(v.co) for v in bm.verts],edges=[[v.index for v in e.verts] for e in bm.edges],faces=[[v.index for v in f.verts] for f in bm.faces],geom=[('v' if isinstance(g,bmesh.types.BMVert) else 'e' if isinstance(g,bmesh.types.BMEdge) else 'f',g.index) for g in geom])
 result=bmesh.ops.extrude_face_region(bm,geom=geom,use_keep_orig=keep)
 moved=[v for v in result['geom'] if isinstance(v,bmesh.types.BMVert)];bmesh.ops.translate(bm,verts=moved,vec=(.2,.3,1))
 for seq in (bm.verts,bm.edges,bm.faces):seq.index_update()
 out[f'{shape}_{selection}_{keep}']=dict(source=source,vertices=[list(v.co) for v in bm.verts],edges=[[v.index for v in e.verts] for e in bm.edges],faces=[[v.index for v in f.verts] for f in bm.faces],result={kind:[g.index for g in result['geom'] if isinstance(g,cls)] for kind,cls in (('verts',bmesh.types.BMVert),('edges',bmesh.types.BMEdge),('faces',bmesh.types.BMFace))})
 bm.free()
Path('/results/reference.json').write_text(json.dumps(out,indent=2)+'\n')
print({k:(len(v['vertices']),len(v['edges']),len(v['faces'])) for k,v in out.items()})
