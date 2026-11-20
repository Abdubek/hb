"""Primitive output dictionaries keep their vertex-list API provenance."""
import bpy,bmesh


def vertices(result):
    assert isinstance(result,dict)
    assert list(result.keys())==['verts']
    values=result.get('verts',())
    assert type(values) is list and values is result['verts']
    assert result.copy().get('verts') is values
    assert next(iter(result.values())) is values
    for key,group in result.items():
        assert key=='verts' and group is values
        for vertex in group:
            assert len(vertex.co)==3 and vertex.is_valid
    assert result.setdefault('verts',()) is values
    assert result.pop('verts') is values
    return values


bm=bmesh.new()
cube=vertices(bmesh.ops.create_cube(bm,size=2))
assert len(cube)==8
bmesh.ops.translate(bm,verts=cube,vec=(0,0,.5))
assert sorted({vertex.co.z for vertex in cube})==[-.5,1.5]
mesh=bpy.data.meshes.new('Mesh')
bm.to_mesh(mesh)
bm.free()
obj=bpy.data.objects.new('Result',mesh)
bpy.context.collection.objects.link(obj)

bm=bmesh.new()
assert len(vertices(bmesh.ops.create_grid(bm,x_segments=1,y_segments=1,size=1)))==4
bm.free()
bm=bmesh.new()
assert len(vertices(bmesh.ops.create_uvsphere(bm,u_segments=8,v_segments=4,radius=1)))>0
bm.free()
bm=bmesh.new()
assert len(vertices(bmesh.ops.create_cone(bm,segments=8,radius1=1,radius2=.5,depth=2,cap_ends=True)))>0
bm.free()
bm=bmesh.new()
assert len(vertices(bmesh.ops.create_circle(bm,segments=8,radius=1,cap_ends=True)))==8
bm.free()
