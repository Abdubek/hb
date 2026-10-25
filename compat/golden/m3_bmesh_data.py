"""Editable UV, float color, shape layers and custom-normal round trips."""
import bpy,bmesh
for mode in ('roundtrip','uv_edit','uv_new','color_new','shape_edit','shape_transform','normal_roundtrip'):
 bpy.ops.mesh.primitive_cube_add();obj=bpy.context.object;obj.name=mode;mesh=obj.data
 if mode=='normal_roundtrip':mesh.normals_split_custom_set([(.2,.3,1)]*24)
 if mode.startswith('shape'):
  obj.shape_key_add(name='Basis');key=obj.shape_key_add(name='Raised');key.data[0].co.z+=1
 bm=bmesh.new();bm.from_mesh(mesh)
 if mode.startswith('uv'):
  layer=bm.loops.layers.uv.new('Second') if mode=='uv_new' else bm.loops.layers.uv.active
  for fi,face in enumerate(bm.faces):
   for i,loop in enumerate(face.loops):loop[layer].uv=(fi*.1,i*.2)
 if mode=='color_new':
  layer=bm.loops.layers.float_color.new('Paint')
  for fi,face in enumerate(bm.faces):
   for i,loop in enumerate(face.loops):loop[layer]=(fi*.1,i*.2,.25,.8)
 if mode=='shape_edit':
  layer=bm.verts.layers.shape['Raised'];bm.verts.ensure_lookup_table();bm.verts[0][layer].z+=2
 if mode=='shape_transform':
  bm.verts.ensure_lookup_table();bmesh.ops.translate(bm,verts=[bm.verts[0]],vec=(0,0,.5),use_shapekey=True)
 bm.to_mesh(mesh)

# Creation defaults and explicit layer lifecycle.
bm=bmesh.new();bmesh.ops.create_cube(bm,size=2)
uv=bm.loops.layers.uv.verify();assert uv.name=='Float2'
assert bm.loops.layers.uv.get('missing') is None
assert bm.loops.layers.uv.keys()==['Float2']
for face in bm.faces:
    for loop in face.loops:
        assert tuple(loop[uv].uv)==(0,0)
        assert loop.face is face and loop.vert in face.verts and loop.edge in face.edges
bm.loops.layers.uv.remove(uv)
color=bm.loops.layers.float_color.new('White')
for face in bm.faces:
    for loop in face.loops:assert tuple(loop[color])==(1,1,1,1)
bm.free()
