import bpy,bmesh
for mode in ('co','basis','raised','translate_false','translate_true','new_layer'):
 bpy.ops.mesh.primitive_cube_add();o=bpy.context.object;o.name=mode;m=o.data;o.shape_key_add(name='Basis');k=o.shape_key_add(name='Raised');k.data[0].co.z+=1
 bm=bmesh.new();bm.from_mesh(m);bm.verts.ensure_lookup_table()
 if mode=='co':bm.verts[0].co.z+=2
 if mode=='basis':bm.verts[0][bm.verts.layers.shape['Basis']].z+=2
 if mode=='raised':bm.verts[0][bm.verts.layers.shape['Raised']].z+=2
 if mode.startswith('translate'):bmesh.ops.translate(bm,verts=[bm.verts[0]],vec=(0,0,2),use_shapekey=mode.endswith('true'))
 if mode=='new_layer':
  layer=bm.verts.layers.shape.new('New');bm.verts.ensure_lookup_table();bm.verts[0][layer]=(2,3,4)
 bm.to_mesh(m)
