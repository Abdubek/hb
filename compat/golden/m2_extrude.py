"""Face-only region extrusion, authored against Blender before implementation."""
HB_SYMBOLS={
'bmesh.types.BMFace.is_valid':'Face handle validity, including after BMesh.free',
'bmesh.types.BMEdge.is_valid':'Edge handle validity, including after BMesh.free',
}
HB_FACE_ORDER_MESH_PREFIXES=('Extrude',)
import bpy,bmesh

def publish(bm):
    bm.normal_update();mesh=bpy.data.meshes.new('Extrude');bm.to_mesh(mesh)
    obj=bpy.data.objects.new('Extrude',mesh);bpy.context.collection.objects.link(obj)
    bm.free()

for x,y in ((1,1),(2,1),(3,2),(3,3)):
    for keep in (False,True):
        for flip in (False,):
            bm=bmesh.new();bmesh.ops.create_grid(bm,x_segments=x,y_segments=y,size=1)
            original=list(bm.faces)
            if x==3 and y==3:
                bm.faces.remove(original[4]);original=original[:4]+original[5:]
            for i,f in enumerate(original):f.material_index=i%2;f.smooth=bool(i%2)
            before=len(bm.verts)
            out=bmesh.ops.extrude_face_region(bm,geom=original[::-1],use_keep_orig=keep,use_normal_flip=flip)
            verts=[g for g in out['geom'] if isinstance(g,bmesh.types.BMVert)]
            edges=[g for g in out['geom'] if isinstance(g,bmesh.types.BMEdge)]
            faces=[g for g in out['geom'] if isinstance(g,bmesh.types.BMFace)]
            assert len(faces)==len(original) and len(bm.verts)==before+len(verts)
            assert all(f.is_valid for f in original) and all(e.is_valid for e in edges)
            bmesh.ops.translate(bm,verts=verts,vec=(.2,-.1,1.3))
            publish(bm)
            assert not faces[0].is_valid and not edges[0].is_valid
# Concave single-face profile and repeated extrusion with intermediate caps removed.
bm=bmesh.new();verts=[bm.verts.new(p) for p in ((0,0,0),(2,0,0),(2,1,0),(1,1,0),(1,2,0),(0,2,0))]
cap=bm.faces.new(verts)
for i in range(3):
    out=bmesh.ops.extrude_face_region(bm,geom=[cap])
    new_verts=[g for g in out['geom'] if isinstance(g,bmesh.types.BMVert)]
    new_faces=[g for g in out['geom'] if isinstance(g,bmesh.types.BMFace)]
    bmesh.ops.translate(bm,verts=new_verts,vec=(0,0,.5))
    if i:bm.faces.remove(cap)
    cap=new_faces[0]
publish(bm)
# No input is a successful, unchanged operation.
bm=bmesh.new();assert bmesh.ops.extrude_face_region(bm)=={'geom':[]};bm.free()
# Extending an existing solid requires removing the retained intermediate cap.
bm=bmesh.new();bmesh.ops.create_cube(bm,size=2);bm.normal_update()
cap=[f for f in bm.faces if f.normal.z>.9][0]
out=bmesh.ops.extrude_face_region(bm,geom=[cap])
bmesh.ops.translate(bm,verts=[g for g in out['geom'] if isinstance(g,bmesh.types.BMVert)],vec=(0,0,1))
bm.faces.remove(cap);publish(bm)
