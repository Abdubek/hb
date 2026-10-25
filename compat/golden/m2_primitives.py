"""Modeling primitive contract, authored before the implementation."""
HB_SYMBOLS = {
    'bpy.ops.mesh.primitive_plane_add': 'WORLD/CURSOR plane in object or single-mesh EDIT construction; size including zero, location/rotation, optional UVs; construction scale ignored',
    'bpy.ops.mesh.primitive_circle_add': 'WORLD/CURSOR circle in object or single-mesh EDIT construction; vertices/radius, NOTHING/NGON/TRIFAN; construction scale ignored; zero radius requires calc_uvs=False',
    'bpy.ops.mesh.primitive_cylinder_add': 'WORLD/CURSOR cylinder in object or single-mesh EDIT construction; vertices/radius/depth, NGON/TRIFAN/NOTHING caps, finite degenerate wire geometry; explicit scale including zero; negative scale requires calc_uvs=False',
}
import bpy
for n in (3,4,5,8,16,32):
    for fill in ('NGON','TRIFAN','NOTHING'):
        bpy.ops.mesh.primitive_cylinder_add(vertices=n, radius=.7, depth=1.3, end_fill_type=fill, location=(n,0,0))
        cylinder=bpy.context.object
        assert len(cylinder.data.vertices)==2*n+(2 if fill=='TRIFAN' else 0)
        assert len(cylinder.data.polygons)==n+(2 if fill=='NGON' else 2*n if fill=='TRIFAN' else 0)
        bpy.ops.mesh.primitive_circle_add(vertices=n,radius=.3,fill_type=fill,location=(n,2,0))
        circle=bpy.context.object
        assert len(circle.data.vertices)==n+(1 if fill=='TRIFAN' else 0)
        assert len(circle.data.polygons)==(1 if fill=='NGON' else n if fill=='TRIFAN' else 0)
        if fill!='NOTHING':assert len(circle.data.uv_layers)==1
bpy.ops.mesh.primitive_plane_add(size=3,scale=(2,.5,1),rotation=(.2,.3,.4),location=(0,0,2))
plane=bpy.context.object
assert tuple(plane.scale)==(1,1,1)
assert all(abs(a-b)<1e-5 for a,b in zip(plane.data.vertices[0].co,(-1.5,-1.5,0)))
bpy.ops.mesh.primitive_plane_add(calc_uvs=False)
assert len(bpy.context.object.data.uv_layers)==0
