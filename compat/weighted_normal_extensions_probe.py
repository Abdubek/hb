import bpy
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='0';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=1;mod.thresh=0;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='1';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=1;mod.thresh=0;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='2';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=1;mod.thresh=0;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='3';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=1;mod.thresh=0;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='4';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=1;mod.thresh=0.01;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='5';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=1;mod.thresh=0.01;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='6';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=1;mod.thresh=0.01;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='7';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=1;mod.thresh=0.01;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='8';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=1;mod.thresh=10;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='9';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=1;mod.thresh=10;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='10';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=1;mod.thresh=10;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='11';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=1;mod.thresh=10;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='12';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=25;mod.thresh=0;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='13';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=25;mod.thresh=0;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='14';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=25;mod.thresh=0;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='15';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=25;mod.thresh=0;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='16';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=25;mod.thresh=0.01;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='17';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=25;mod.thresh=0.01;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='18';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=25;mod.thresh=0.01;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='19';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=25;mod.thresh=0.01;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='20';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=25;mod.thresh=10;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='21';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=25;mod.thresh=10;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='22';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=25;mod.thresh=10;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='23';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=25;mod.thresh=10;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='24';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=50;mod.thresh=0;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='25';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=50;mod.thresh=0;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='26';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=50;mod.thresh=0;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='27';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=50;mod.thresh=0;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='28';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=50;mod.thresh=0.01;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='29';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=50;mod.thresh=0.01;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='30';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=50;mod.thresh=0.01;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='31';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=50;mod.thresh=0.01;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='32';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=50;mod.thresh=10;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='33';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=50;mod.thresh=10;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='34';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=50;mod.thresh=10;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='35';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=50;mod.thresh=10;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='36';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=51;mod.thresh=0;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='37';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=51;mod.thresh=0;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='38';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=51;mod.thresh=0;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='39';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=51;mod.thresh=0;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='40';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=51;mod.thresh=0.01;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='41';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=51;mod.thresh=0.01;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='42';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=51;mod.thresh=0.01;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='43';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=51;mod.thresh=0.01;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='44';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=51;mod.thresh=10;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='45';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=51;mod.thresh=10;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='46';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=51;mod.thresh=10;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='47';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=51;mod.thresh=10;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='48';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=60;mod.thresh=0;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='49';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=60;mod.thresh=0;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='50';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=60;mod.thresh=0;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='51';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=60;mod.thresh=0;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='52';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=60;mod.thresh=0.01;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='53';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=60;mod.thresh=0.01;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='54';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=60;mod.thresh=0.01;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='55';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=60;mod.thresh=0.01;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='56';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=60;mod.thresh=10;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='57';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=60;mod.thresh=10;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='58';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=60;mod.thresh=10;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='59';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=60;mod.thresh=10;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='60';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='61';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='62';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='63';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='64';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.01;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='65';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.01;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='66';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.01;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='67';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.01;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='68';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=10;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='69';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=10;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='70';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=10;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='71';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=10;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='72';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=100;mod.thresh=0;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='73';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=100;mod.thresh=0;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='74';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=100;mod.thresh=0;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='75';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=100;mod.thresh=0;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='76';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=100;mod.thresh=0.01;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='77';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=100;mod.thresh=0.01;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='78';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=100;mod.thresh=0.01;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='79';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=100;mod.thresh=0.01;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='80';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=100;mod.thresh=10;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='81';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=100;mod.thresh=10;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='82';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=100;mod.thresh=10;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='83';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=100;mod.thresh=10;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='84';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=1;mod.thresh=0;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='85';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=1;mod.thresh=0;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='86';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=1;mod.thresh=0;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='87';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=1;mod.thresh=0;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='88';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=1;mod.thresh=0.01;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='89';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=1;mod.thresh=0.01;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='90';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=1;mod.thresh=0.01;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='91';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=1;mod.thresh=0.01;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='92';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=1;mod.thresh=10;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='93';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=1;mod.thresh=10;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='94';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=1;mod.thresh=10;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='95';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=1;mod.thresh=10;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='96';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=25;mod.thresh=0;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='97';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=25;mod.thresh=0;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='98';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=25;mod.thresh=0;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='99';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=25;mod.thresh=0;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='100';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=25;mod.thresh=0.01;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='101';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=25;mod.thresh=0.01;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='102';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=25;mod.thresh=0.01;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='103';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=25;mod.thresh=0.01;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='104';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=25;mod.thresh=10;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='105';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=25;mod.thresh=10;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='106';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=25;mod.thresh=10;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='107';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=25;mod.thresh=10;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='108';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=50;mod.thresh=0;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='109';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=50;mod.thresh=0;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='110';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=50;mod.thresh=0;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='111';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=50;mod.thresh=0;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='112';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=50;mod.thresh=0.01;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='113';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=50;mod.thresh=0.01;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='114';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=50;mod.thresh=0.01;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='115';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=50;mod.thresh=0.01;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='116';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=50;mod.thresh=10;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='117';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=50;mod.thresh=10;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='118';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=50;mod.thresh=10;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='119';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=50;mod.thresh=10;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='120';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=51;mod.thresh=0;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='121';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=51;mod.thresh=0;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='122';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=51;mod.thresh=0;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='123';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=51;mod.thresh=0;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='124';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=51;mod.thresh=0.01;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='125';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=51;mod.thresh=0.01;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='126';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=51;mod.thresh=0.01;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='127';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=51;mod.thresh=0.01;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='128';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=51;mod.thresh=10;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='129';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=51;mod.thresh=10;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='130';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=51;mod.thresh=10;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='131';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=51;mod.thresh=10;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='132';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=60;mod.thresh=0;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='133';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=60;mod.thresh=0;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='134';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=60;mod.thresh=0;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='135';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=60;mod.thresh=0;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='136';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=60;mod.thresh=0.01;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='137';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=60;mod.thresh=0.01;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='138';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=60;mod.thresh=0.01;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='139';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=60;mod.thresh=0.01;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='140';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=60;mod.thresh=10;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='141';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=60;mod.thresh=10;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='142';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=60;mod.thresh=10;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='143';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=60;mod.thresh=10;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='144';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='145';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='146';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='147';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='148';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.01;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='149';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.01;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='150';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.01;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='151';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.01;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='152';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=10;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='153';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=10;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='154';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=10;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='155';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=10;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='156';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=100;mod.thresh=0;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='157';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=100;mod.thresh=0;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='158';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=100;mod.thresh=0;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='159';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=100;mod.thresh=0;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='160';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=100;mod.thresh=0.01;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='161';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=100;mod.thresh=0.01;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='162';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=100;mod.thresh=0.01;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='163';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=100;mod.thresh=0.01;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='164';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=100;mod.thresh=10;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='165';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=100;mod.thresh=10;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='166';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=100;mod.thresh=10;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='167';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=100;mod.thresh=10;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='168';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=1;mod.thresh=0;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='169';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=1;mod.thresh=0;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='170';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=1;mod.thresh=0;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='171';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=1;mod.thresh=0;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='172';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=1;mod.thresh=0.01;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='173';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=1;mod.thresh=0.01;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='174';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=1;mod.thresh=0.01;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='175';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=1;mod.thresh=0.01;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='176';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=1;mod.thresh=10;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='177';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=1;mod.thresh=10;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='178';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=1;mod.thresh=10;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='179';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=1;mod.thresh=10;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='180';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=25;mod.thresh=0;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='181';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=25;mod.thresh=0;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='182';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=25;mod.thresh=0;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='183';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=25;mod.thresh=0;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='184';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=25;mod.thresh=0.01;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='185';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=25;mod.thresh=0.01;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='186';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=25;mod.thresh=0.01;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='187';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=25;mod.thresh=0.01;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='188';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=25;mod.thresh=10;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='189';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=25;mod.thresh=10;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='190';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=25;mod.thresh=10;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='191';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=25;mod.thresh=10;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='192';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=50;mod.thresh=0;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='193';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=50;mod.thresh=0;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='194';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=50;mod.thresh=0;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='195';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=50;mod.thresh=0;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='196';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=50;mod.thresh=0.01;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='197';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=50;mod.thresh=0.01;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='198';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=50;mod.thresh=0.01;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='199';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=50;mod.thresh=0.01;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='200';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=50;mod.thresh=10;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='201';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=50;mod.thresh=10;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='202';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=50;mod.thresh=10;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='203';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=50;mod.thresh=10;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='204';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=51;mod.thresh=0;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='205';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=51;mod.thresh=0;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='206';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=51;mod.thresh=0;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='207';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=51;mod.thresh=0;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='208';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=51;mod.thresh=0.01;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='209';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=51;mod.thresh=0.01;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='210';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=51;mod.thresh=0.01;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='211';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=51;mod.thresh=0.01;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='212';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=51;mod.thresh=10;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='213';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=51;mod.thresh=10;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='214';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=51;mod.thresh=10;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='215';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=51;mod.thresh=10;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='216';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=60;mod.thresh=0;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='217';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=60;mod.thresh=0;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='218';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=60;mod.thresh=0;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='219';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=60;mod.thresh=0;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='220';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=60;mod.thresh=0.01;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='221';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=60;mod.thresh=0.01;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='222';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=60;mod.thresh=0.01;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='223';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=60;mod.thresh=0.01;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='224';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=60;mod.thresh=10;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='225';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=60;mod.thresh=10;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='226';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=60;mod.thresh=10;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='227';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=60;mod.thresh=10;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='228';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='229';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='230';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='231';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='232';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.01;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='233';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.01;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='234';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.01;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='235';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.01;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='236';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=10;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='237';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=10;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='238';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=10;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='239';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=10;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='240';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=100;mod.thresh=0;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='241';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=100;mod.thresh=0;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='242';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=100;mod.thresh=0;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='243';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=100;mod.thresh=0;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='244';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=100;mod.thresh=0.01;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='245';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=100;mod.thresh=0.01;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='246';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=100;mod.thresh=0.01;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='247';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=100;mod.thresh=0.01;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='248';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=100;mod.thresh=10;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='249';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=100;mod.thresh=10;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='250';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=100;mod.thresh=10;mod.keep_sharp=False;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='251';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=100;mod.thresh=10;mod.keep_sharp=True;mod.vertex_group='';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='252';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='253';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='254';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='255';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='256';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='257';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='258';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='259';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='260';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='261';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='262';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='263';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='264';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='265';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='266';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='267';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='268';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='269';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='270';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='271';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='272';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='273';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='274';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='275';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='276';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='277';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='278';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='279';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='280';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='281';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='282';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='283';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='284';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='285';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='286';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='287';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='288';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='289';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='290';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='291';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='292';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='293';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='294';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='295';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='296';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='297';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='298';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='299';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='300';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='301';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='302';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='303';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='304';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='305';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='306';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='307';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='308';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='309';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='310';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='311';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='312';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='313';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='314';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='315';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='316';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='317';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='318';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='319';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='320';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='321';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='322';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='323';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='324';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='325';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='326';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='327';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='328';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='329';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='330';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='331';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='332';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='333';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='334';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='335';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='336';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='337';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='338';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='339';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='340';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='341';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='342';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='343';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='344';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='345';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='346';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='347';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='348';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='349';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='350';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='351';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='352';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='353';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='354';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='355';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='356';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='357';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='358';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='359';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='360';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='361';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='362';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='363';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='364';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='365';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='366';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='367';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='368';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='369';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='370';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='371';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='372';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='373';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='374';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='375';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='376';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='377';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='378';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='379';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='CORNER_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='380';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='381';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='382';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='383';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='384';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='385';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='386';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='387';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='388';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='389';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='390';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='391';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='392';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='393';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='394';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='395';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='396';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='397';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='398';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='399';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='400';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='401';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='402';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='403';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='404';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='405';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='406';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='407';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='408';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='409';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='410';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='411';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=False
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='412';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='413';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='414';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='415';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='416';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='417';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='418';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='419';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='420';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='421';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='422';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='423';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='424';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='425';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='426';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='427';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=False;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='428';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='429';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='430';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='431';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='432';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='433';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='434';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='435';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='436';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='437';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='438';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='439';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Mask';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='440';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='441';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=False;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='442';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='443';mesh=obj.data
for v,co in zip(mesh.vertices,[[-3.0, -2.0, -1.0], [-3.0, -2.0, 1.0], [-3.0, 2.0, -1.0], [-3.0, 2.0, 1.0], [3.0, -2.0, -1.0], [3.0, -2.0, 1.0], [3.0, 2.0, -0.699999988079071], [3.0, 2.0, 1.0]]):v.co=co
for f in mesh.polygons:f.use_smooth=True
group=obj.vertex_groups.new(name='Mask')
for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
for k,v in enumerate(attr.data):v.value=k%3
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=75;mod.thresh=0.2;mod.keep_sharp=True;mod.vertex_group='Missing';mod.invert_vertex_group=True;mod.use_face_influence=True
bpy.ops.object.modifier_apply(modifier=mod.name)
