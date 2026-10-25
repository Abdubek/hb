import bpy
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='NORMAL__False_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='NORMAL';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='NORMAL__False_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='NORMAL';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='NORMAL__True_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='NORMAL';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='NORMAL__True_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='NORMAL';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='NORMAL_Mask_False_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='NORMAL';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Mask';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='NORMAL_Mask_False_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='NORMAL';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Mask';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='NORMAL_Mask_True_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='NORMAL';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Mask';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='NORMAL_Mask_True_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='NORMAL';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Mask';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='NORMAL_Missing_False_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='NORMAL';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Missing';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='NORMAL_Missing_False_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='NORMAL';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Missing';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='NORMAL_Missing_True_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='NORMAL';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Missing';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='NORMAL_Missing_True_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='NORMAL';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Missing';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='X__False_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='X';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='X__False_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='X';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='X__True_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='X';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='X__True_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='X';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='X_Mask_False_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='X';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Mask';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='X_Mask_False_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='X';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Mask';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='X_Mask_True_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='X';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Mask';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='X_Mask_True_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='X';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Mask';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='X_Missing_False_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='X';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Missing';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='X_Missing_False_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='X';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Missing';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='X_Missing_True_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='X';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Missing';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='X_Missing_True_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='X';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Missing';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='Y__False_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='Y';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='Y__False_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='Y';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='Y__True_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='Y';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='Y__True_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='Y';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='Y_Mask_False_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='Y';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Mask';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='Y_Mask_False_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='Y';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Mask';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='Y_Mask_True_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='Y';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Mask';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='Y_Mask_True_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='Y';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Mask';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='Y_Missing_False_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='Y';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Missing';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='Y_Missing_False_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='Y';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Missing';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='Y_Missing_True_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='Y';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Missing';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='Y_Missing_True_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='Y';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Missing';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='Z__False_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='Z';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='Z__False_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='Z';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='Z__True_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='Z';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='Z__True_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='Z';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='Z_Mask_False_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='Z';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Mask';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='Z_Mask_False_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='Z';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Mask';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='Z_Mask_True_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='Z';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Mask';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='Z_Mask_True_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='Z';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Mask';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='Z_Missing_False_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='Z';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Missing';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='Z_Missing_False_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='Z';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Missing';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='Z_Missing_True_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='Z';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Missing';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='Z_Missing_True_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
mod=obj.modifiers.new('Displace','DISPLACE')
mod.direction='Z';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Missing';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)

import bpy
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_NORMAL__False_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='NORMAL';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_NORMAL__False_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='NORMAL';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_NORMAL__True_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='NORMAL';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_NORMAL__True_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='NORMAL';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_NORMAL_Mask_False_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='NORMAL';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Mask';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_NORMAL_Mask_False_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='NORMAL';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Mask';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_NORMAL_Mask_True_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='NORMAL';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Mask';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_NORMAL_Mask_True_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='NORMAL';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Mask';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_NORMAL_Missing_False_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='NORMAL';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Missing';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_NORMAL_Missing_False_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='NORMAL';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Missing';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_NORMAL_Missing_True_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='NORMAL';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Missing';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_NORMAL_Missing_True_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='NORMAL';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Missing';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_X__False_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='X';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_X__False_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='X';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_X__True_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='X';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_X__True_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='X';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_X_Mask_False_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='X';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Mask';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_X_Mask_False_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='X';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Mask';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_X_Mask_True_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='X';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Mask';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_X_Mask_True_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='X';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Mask';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_X_Missing_False_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='X';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Missing';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_X_Missing_False_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='X';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Missing';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_X_Missing_True_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='X';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Missing';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_X_Missing_True_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='X';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Missing';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_Y__False_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='Y';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_Y__False_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='Y';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_Y__True_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='Y';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_Y__True_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='Y';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_Y_Mask_False_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='Y';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Mask';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_Y_Mask_False_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='Y';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Mask';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_Y_Mask_True_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='Y';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Mask';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_Y_Mask_True_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='Y';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Mask';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_Y_Missing_False_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='Y';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Missing';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_Y_Missing_False_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='Y';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Missing';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_Y_Missing_True_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='Y';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Missing';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_Y_Missing_True_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='Y';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Missing';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_Z__False_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='Z';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_Z__False_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='Z';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_Z__True_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='Z';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_Z__True_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='Z';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_Z_Mask_False_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='Z';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Mask';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_Z_Mask_False_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='Z';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Mask';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_Z_Mask_True_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='Z';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Mask';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_Z_Mask_True_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='Z';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Mask';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_Z_Missing_False_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='Z';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Missing';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_Z_Missing_False_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='Z';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Missing';mod.invert_vertex_group=False
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_Z_Missing_True_False';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='Z';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Missing';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='texture_Z_Missing_True_True';mesh=obj.data
weights=obj.vertex_groups.new(name='Mask')
for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
mesh.normals_split_custom_set([(.2,.3,1)]*24)
tex=bpy.data.textures.new('Cells',type='CLOUDS');tex.noise_basis='CELL_NOISE';tex.noise_depth=2;tex.noise_scale=.35
mod=obj.modifiers.new('Displace','DISPLACE');mod.texture=tex
mod.direction='Z';mod.strength=.4;mod.mid_level=.2;mod.vertex_group='Missing';mod.invert_vertex_group=True
bpy.ops.object.modifier_apply(modifier=mod.name)
