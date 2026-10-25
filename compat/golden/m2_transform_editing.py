"""Affine editable-mesh transforms and matrix-bearing primitive creation."""
HB_SYMBOLS={
'bmesh.ops.translate':'Translate editable vertices in nonsingular 3x3/4x4 space; returns None',
'bmesh.ops.scale':'Scale editable vertices in nonsingular 3x3/4x4 space; returns None',
'bmesh.ops.create_cube':'Cube creation with optional 3x3/4x4 matrix; no editable UV layers',
'bmesh.ops.create_grid':'Grid creation with optional 3x3/4x4 matrix; no editable UV layers',
'bmesh.ops.create_uvsphere':'UV-sphere creation with optional 3x3/4x4 matrix; no editable UV layers',
'bmesh.ops.create_cone':'Cone creation with optional 3x3/4x4 matrix; no editable UV layers',
'bmesh.ops.create_circle':'Circle creation with optional 3x3/4x4 matrix; no editable UV layers',
}
HB_EQUIVALENT_MESH_PREFIXES=('Transformed sphere 3','Transformed sphere 4')
import bpy,bmesh
from mathutils import Matrix

def save(bm,name):
    mesh=bpy.data.meshes.new(name);bm.to_mesh(mesh);bm.free()
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj)

for dimension in (3,4):
    matrix=Matrix.Rotation(.37,dimension,'Y')@Matrix.Scale(1.3,dimension)
    if dimension==4:matrix.translation=(1.2,-.4,2.1)
    for primitive in ('cube','grid','sphere','cone','circle'):
        bm=bmesh.new();old=bm.verts.new((7,8,9))
        if primitive=='cube':created=bmesh.ops.create_cube(bm,size=1.7,matrix=matrix)['verts']
        elif primitive=='grid':created=bmesh.ops.create_grid(bm,x_segments=3,y_segments=2,size=1.7,matrix=matrix)['verts']
        elif primitive=='sphere':created=bmesh.ops.create_uvsphere(bm,u_segments=12,v_segments=8,radius=1.7,matrix=matrix)['verts']
        elif primitive=='cone':created=bmesh.ops.create_cone(bm,segments=12,radius1=1.7,radius2=.6,depth=2.2,cap_ends=True,matrix=matrix)['verts']
        else:created=bmesh.ops.create_circle(bm,segments=12,radius=1.7,cap_ends=True,matrix=matrix)['verts']
        assert len(created)>0 and tuple(old.co)==(7,8,9)
        save(bm,'Transformed '+primitive+' '+str(dimension))

for space_kind in ('identity','translated','general'):
    space=Matrix.Identity(4)
    if space_kind=='translated':space.translation=(.7,-1.3,2.1)
    elif space_kind=='general':
        space=Matrix.Rotation(.23,4,'Z')@Matrix.Diagonal((1.4,.7,1.2,1));space.translation=(.7,-1.3,2.1)
    for op in ('translate','scale','rotate','transform'):
        bm=bmesh.new();verts=bmesh.ops.create_cube(bm,size=2)['verts'];untouched=bm.verts.new((7,8,9))
        matrix=Matrix.Rotation(.41,4,'X');matrix.translation=(.2,.3,-.4)
        if op=='translate':result=bmesh.ops.translate(bm,vec=(.3,-.4,1.2),verts=verts,space=space,use_shapekey=False)
        elif op=='scale':result=bmesh.ops.scale(bm,vec=(1.3,.6,-.8),verts=verts,space=space,use_shapekey=False)
        elif op=='rotate':result=bmesh.ops.rotate(bm,cent=(.2,-.4,.7),matrix=matrix,verts=verts,space=space,use_shapekey=False)
        else:result=bmesh.ops.transform(bm,matrix=matrix,verts=verts,space=space,use_shapekey=False)
        assert result is None and tuple(untouched.co)==(7,8,9)
        save(bm,op+' '+space_kind)

# BMesh operator buffers reject duplicate vertices before changing coordinates.
bm=bmesh.new();vertex=bm.verts.new((1,2,3))
try:bmesh.ops.translate(bm,verts=[vertex,vertex],vec=(2,3,4))
except ValueError:pass
else:raise AssertionError('Duplicate operator input accepted')
assert tuple(vertex.co)==(1,2,3);bm.free()
