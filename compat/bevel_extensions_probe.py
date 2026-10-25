import bpy
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='EDGES_1_0.1_True'
for v in obj.data.vertices:v.co.y*=2;v.co.z*=3
mod=obj.modifiers.new('Bevel','BEVEL')
mod.affect='EDGES';mod.width=0.1;mod.segments=1;mod.use_clamp_overlap=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='EDGES_1_0.1_False'
for v in obj.data.vertices:v.co.y*=2;v.co.z*=3
mod=obj.modifiers.new('Bevel','BEVEL')
mod.affect='EDGES';mod.width=0.1;mod.segments=1;mod.use_clamp_overlap=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='EDGES_1_1.0_True'
for v in obj.data.vertices:v.co.y*=2;v.co.z*=3
mod=obj.modifiers.new('Bevel','BEVEL')
mod.affect='EDGES';mod.width=1.0;mod.segments=1;mod.use_clamp_overlap=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='EDGES_1_3.0_True'
for v in obj.data.vertices:v.co.y*=2;v.co.z*=3
mod=obj.modifiers.new('Bevel','BEVEL')
mod.affect='EDGES';mod.width=3.0;mod.segments=1;mod.use_clamp_overlap=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='EDGES_2_0.1_True'
for v in obj.data.vertices:v.co.y*=2;v.co.z*=3
mod=obj.modifiers.new('Bevel','BEVEL')
mod.affect='EDGES';mod.width=0.1;mod.segments=2;mod.use_clamp_overlap=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='EDGES_2_0.1_False'
for v in obj.data.vertices:v.co.y*=2;v.co.z*=3
mod=obj.modifiers.new('Bevel','BEVEL')
mod.affect='EDGES';mod.width=0.1;mod.segments=2;mod.use_clamp_overlap=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='EDGES_2_1.0_True'
for v in obj.data.vertices:v.co.y*=2;v.co.z*=3
mod=obj.modifiers.new('Bevel','BEVEL')
mod.affect='EDGES';mod.width=1.0;mod.segments=2;mod.use_clamp_overlap=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='EDGES_2_3.0_True'
for v in obj.data.vertices:v.co.y*=2;v.co.z*=3
mod=obj.modifiers.new('Bevel','BEVEL')
mod.affect='EDGES';mod.width=3.0;mod.segments=2;mod.use_clamp_overlap=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='EDGES_3_0.1_True'
for v in obj.data.vertices:v.co.y*=2;v.co.z*=3
mod=obj.modifiers.new('Bevel','BEVEL')
mod.affect='EDGES';mod.width=0.1;mod.segments=3;mod.use_clamp_overlap=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='EDGES_3_0.1_False'
for v in obj.data.vertices:v.co.y*=2;v.co.z*=3
mod=obj.modifiers.new('Bevel','BEVEL')
mod.affect='EDGES';mod.width=0.1;mod.segments=3;mod.use_clamp_overlap=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='EDGES_3_1.0_True'
for v in obj.data.vertices:v.co.y*=2;v.co.z*=3
mod=obj.modifiers.new('Bevel','BEVEL')
mod.affect='EDGES';mod.width=1.0;mod.segments=3;mod.use_clamp_overlap=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='EDGES_3_3.0_True'
for v in obj.data.vertices:v.co.y*=2;v.co.z*=3
mod=obj.modifiers.new('Bevel','BEVEL')
mod.affect='EDGES';mod.width=3.0;mod.segments=3;mod.use_clamp_overlap=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='EDGES_4_0.1_True'
for v in obj.data.vertices:v.co.y*=2;v.co.z*=3
mod=obj.modifiers.new('Bevel','BEVEL')
mod.affect='EDGES';mod.width=0.1;mod.segments=4;mod.use_clamp_overlap=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='EDGES_4_0.1_False'
for v in obj.data.vertices:v.co.y*=2;v.co.z*=3
mod=obj.modifiers.new('Bevel','BEVEL')
mod.affect='EDGES';mod.width=0.1;mod.segments=4;mod.use_clamp_overlap=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='EDGES_4_1.0_True'
for v in obj.data.vertices:v.co.y*=2;v.co.z*=3
mod=obj.modifiers.new('Bevel','BEVEL')
mod.affect='EDGES';mod.width=1.0;mod.segments=4;mod.use_clamp_overlap=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='EDGES_4_3.0_True'
for v in obj.data.vertices:v.co.y*=2;v.co.z*=3
mod=obj.modifiers.new('Bevel','BEVEL')
mod.affect='EDGES';mod.width=3.0;mod.segments=4;mod.use_clamp_overlap=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='EDGES_8_0.1_True'
for v in obj.data.vertices:v.co.y*=2;v.co.z*=3
mod=obj.modifiers.new('Bevel','BEVEL')
mod.affect='EDGES';mod.width=0.1;mod.segments=8;mod.use_clamp_overlap=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='EDGES_8_0.1_False'
for v in obj.data.vertices:v.co.y*=2;v.co.z*=3
mod=obj.modifiers.new('Bevel','BEVEL')
mod.affect='EDGES';mod.width=0.1;mod.segments=8;mod.use_clamp_overlap=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='EDGES_8_1.0_True'
for v in obj.data.vertices:v.co.y*=2;v.co.z*=3
mod=obj.modifiers.new('Bevel','BEVEL')
mod.affect='EDGES';mod.width=1.0;mod.segments=8;mod.use_clamp_overlap=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='EDGES_8_3.0_True'
for v in obj.data.vertices:v.co.y*=2;v.co.z*=3
mod=obj.modifiers.new('Bevel','BEVEL')
mod.affect='EDGES';mod.width=3.0;mod.segments=8;mod.use_clamp_overlap=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='VERTICES_1_0.1_True'
for v in obj.data.vertices:v.co.y*=2;v.co.z*=3
mod=obj.modifiers.new('Bevel','BEVEL')
mod.affect='VERTICES';mod.width=0.1;mod.segments=1;mod.use_clamp_overlap=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='VERTICES_1_0.1_False'
for v in obj.data.vertices:v.co.y*=2;v.co.z*=3
mod=obj.modifiers.new('Bevel','BEVEL')
mod.affect='VERTICES';mod.width=0.1;mod.segments=1;mod.use_clamp_overlap=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='VERTICES_1_1.0_True'
for v in obj.data.vertices:v.co.y*=2;v.co.z*=3
mod=obj.modifiers.new('Bevel','BEVEL')
mod.affect='VERTICES';mod.width=1.0;mod.segments=1;mod.use_clamp_overlap=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='VERTICES_1_3.0_True'
for v in obj.data.vertices:v.co.y*=2;v.co.z*=3
mod=obj.modifiers.new('Bevel','BEVEL')
mod.affect='VERTICES';mod.width=3.0;mod.segments=1;mod.use_clamp_overlap=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='VERTICES_2_0.1_True'
for v in obj.data.vertices:v.co.y*=2;v.co.z*=3
mod=obj.modifiers.new('Bevel','BEVEL')
mod.affect='VERTICES';mod.width=0.1;mod.segments=2;mod.use_clamp_overlap=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='VERTICES_2_0.1_False'
for v in obj.data.vertices:v.co.y*=2;v.co.z*=3
mod=obj.modifiers.new('Bevel','BEVEL')
mod.affect='VERTICES';mod.width=0.1;mod.segments=2;mod.use_clamp_overlap=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='VERTICES_2_1.0_True'
for v in obj.data.vertices:v.co.y*=2;v.co.z*=3
mod=obj.modifiers.new('Bevel','BEVEL')
mod.affect='VERTICES';mod.width=1.0;mod.segments=2;mod.use_clamp_overlap=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='VERTICES_2_3.0_True'
for v in obj.data.vertices:v.co.y*=2;v.co.z*=3
mod=obj.modifiers.new('Bevel','BEVEL')
mod.affect='VERTICES';mod.width=3.0;mod.segments=2;mod.use_clamp_overlap=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='VERTICES_4_0.1_True'
for v in obj.data.vertices:v.co.y*=2;v.co.z*=3
mod=obj.modifiers.new('Bevel','BEVEL')
mod.affect='VERTICES';mod.width=0.1;mod.segments=4;mod.use_clamp_overlap=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='VERTICES_4_0.1_False'
for v in obj.data.vertices:v.co.y*=2;v.co.z*=3
mod=obj.modifiers.new('Bevel','BEVEL')
mod.affect='VERTICES';mod.width=0.1;mod.segments=4;mod.use_clamp_overlap=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='VERTICES_4_1.0_True'
for v in obj.data.vertices:v.co.y*=2;v.co.z*=3
mod=obj.modifiers.new('Bevel','BEVEL')
mod.affect='VERTICES';mod.width=1.0;mod.segments=4;mod.use_clamp_overlap=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='VERTICES_4_3.0_True'
for v in obj.data.vertices:v.co.y*=2;v.co.z*=3
mod=obj.modifiers.new('Bevel','BEVEL')
mod.affect='VERTICES';mod.width=3.0;mod.segments=4;mod.use_clamp_overlap=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='VERTICES_8_0.1_True'
for v in obj.data.vertices:v.co.y*=2;v.co.z*=3
mod=obj.modifiers.new('Bevel','BEVEL')
mod.affect='VERTICES';mod.width=0.1;mod.segments=8;mod.use_clamp_overlap=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='VERTICES_8_0.1_False'
for v in obj.data.vertices:v.co.y*=2;v.co.z*=3
mod=obj.modifiers.new('Bevel','BEVEL')
mod.affect='VERTICES';mod.width=0.1;mod.segments=8;mod.use_clamp_overlap=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='VERTICES_8_1.0_True'
for v in obj.data.vertices:v.co.y*=2;v.co.z*=3
mod=obj.modifiers.new('Bevel','BEVEL')
mod.affect='VERTICES';mod.width=1.0;mod.segments=8;mod.use_clamp_overlap=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='VERTICES_8_3.0_True'
for v in obj.data.vertices:v.co.y*=2;v.co.z*=3
mod=obj.modifiers.new('Bevel','BEVEL')
mod.affect='VERTICES';mod.width=3.0;mod.segments=8;mod.use_clamp_overlap=True
bpy.ops.object.modifier_apply(modifier=mod.name)
