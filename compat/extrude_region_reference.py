import bpy,bmesh,json,itertools
from pathlib import Path
out={}
for faces_count,edge_count,verts,keep in itertools.product((1,2,6),(0,1,2,4,12),(False,True),(False,True)):
 bm=bmesh.new();bmesh.ops.create_cube(bm,size=2)
 for seq in (bm.verts,bm.edges,bm.faces):seq.ensure_lookup_table();seq.index_update()
 geom=list(bm.faces)[:faces_count]+list(bm.edges)[:edge_count]+(list(bm.verts) if verts else [])
 source=dict(vertices=[list(v.co) for v in bm.verts],edges=[[v.index for v in e.verts] for e in bm.edges],faces=[[v.index for v in f.verts] for f in bm.faces],geom=[('v' if isinstance(g,bmesh.types.BMVert) else 'e' if isinstance(g,bmesh.types.BMEdge) else 'f',g.index) for g in geom])
 result=bmesh.ops.extrude_face_region(bm,geom=geom,use_keep_orig=keep);bmesh.ops.translate(bm,verts=[v for v in result['geom'] if isinstance(v,bmesh.types.BMVert)],vec=(.2,.3,1))
 for seq in (bm.verts,bm.edges,bm.faces):seq.index_update()
 out[f'{faces_count}_{edge_count}_{verts}_{keep}']=dict(source=source,vertices=[list(v.co) for v in bm.verts],edges=[[v.index for v in e.verts] for e in bm.edges],faces=[[v.index for v in f.verts] for f in bm.faces])
 bm.free()
Path('/results/region-reference.json').write_text(json.dumps(out,indent=2)+'\n')
print({k:(len(v['vertices']),len(v['edges']),len(v['faces'])) for k,v in out.items()})
