import bpy
mesh=bpy.data.meshes.new('cube_1_False')
mesh.from_pydata([[-1.0, -1.0, -1.0], [-1.0, -1.0, 1.0], [-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, -1.0, -1.0], [1.0, -1.0, 1.0], [1.0, 1.0, -1.0], [1.0, 1.0, 1.0]],[[2, 0], [0, 1], [1, 3], [3, 2], [6, 2], [3, 7], [7, 6], [4, 6], [7, 5], [5, 4], [0, 4], [5, 1]],[[0, 1, 3, 2], [2, 3, 7, 6], [6, 7, 5, 4], [4, 5, 1, 0], [2, 6, 4, 0], [7, 3, 1, 5]])
obj=bpy.data.objects.new('cube_1_False',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
uv=mesh.uv_layers.new(name='UVMap')
coords=[[0.375, 0.0], [0.625, 0.0], [0.625, 0.25], [0.375, 0.25], [0.375, 0.25], [0.625, 0.25], [0.625, 0.5], [0.375, 0.5], [0.375, 0.5], [0.625, 0.5], [0.625, 0.75], [0.375, 0.75], [0.375, 0.75], [0.625, 0.75], [0.625, 1.0], [0.375, 1.0], [0.125, 0.5], [0.375, 0.5], [0.375, 0.75], [0.125, 0.75], [0.625, 0.5], [0.875, 0.5], [0.875, 0.75], [0.625, 0.75]]
for i,d in enumerate(uv.data):d.uv=coords[i]
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=1;mod.subdivision_type='CATMULL_CLARK'
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('cube_1_True')
mesh.from_pydata([[-1.0, -1.0, -1.0], [-1.0, -1.0, 1.0], [-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, -1.0, -1.0], [1.0, -1.0, 1.0], [1.0, 1.0, -1.0], [1.0, 1.0, 1.0]],[[2, 0], [0, 1], [1, 3], [3, 2], [6, 2], [3, 7], [7, 6], [4, 6], [7, 5], [5, 4], [0, 4], [5, 1]],[[0, 1, 3, 2], [2, 3, 7, 6], [6, 7, 5, 4], [4, 5, 1, 0], [2, 6, 4, 0], [7, 3, 1, 5]])
obj=bpy.data.objects.new('cube_1_True',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
uv=mesh.uv_layers.new(name='UVMap')
coords=[[0.375, 0.0], [0.625, 0.0], [0.625, 0.25], [0.375, 0.25], [0.375, 0.25], [0.625, 0.25], [0.625, 0.5], [0.375, 0.5], [0.375, 0.5], [0.625, 0.5], [0.625, 0.75], [0.375, 0.75], [0.375, 0.75], [0.625, 0.75], [0.625, 1.0], [0.375, 1.0], [0.125, 0.5], [0.375, 0.5], [0.375, 0.75], [0.125, 0.75], [0.625, 0.5], [0.875, 0.5], [0.875, 0.75], [0.625, 0.75]]
for i,d in enumerate(uv.data):d.uv=coords[i]
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=1;mod.subdivision_type='SIMPLE'
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('cube_2_False')
mesh.from_pydata([[-1.0, -1.0, -1.0], [-1.0, -1.0, 1.0], [-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, -1.0, -1.0], [1.0, -1.0, 1.0], [1.0, 1.0, -1.0], [1.0, 1.0, 1.0]],[[2, 0], [0, 1], [1, 3], [3, 2], [6, 2], [3, 7], [7, 6], [4, 6], [7, 5], [5, 4], [0, 4], [5, 1]],[[0, 1, 3, 2], [2, 3, 7, 6], [6, 7, 5, 4], [4, 5, 1, 0], [2, 6, 4, 0], [7, 3, 1, 5]])
obj=bpy.data.objects.new('cube_2_False',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
uv=mesh.uv_layers.new(name='UVMap')
coords=[[0.375, 0.0], [0.625, 0.0], [0.625, 0.25], [0.375, 0.25], [0.375, 0.25], [0.625, 0.25], [0.625, 0.5], [0.375, 0.5], [0.375, 0.5], [0.625, 0.5], [0.625, 0.75], [0.375, 0.75], [0.375, 0.75], [0.625, 0.75], [0.625, 1.0], [0.375, 1.0], [0.125, 0.5], [0.375, 0.5], [0.375, 0.75], [0.125, 0.75], [0.625, 0.5], [0.875, 0.5], [0.875, 0.75], [0.625, 0.75]]
for i,d in enumerate(uv.data):d.uv=coords[i]
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=2;mod.subdivision_type='CATMULL_CLARK'
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('cube_2_True')
mesh.from_pydata([[-1.0, -1.0, -1.0], [-1.0, -1.0, 1.0], [-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, -1.0, -1.0], [1.0, -1.0, 1.0], [1.0, 1.0, -1.0], [1.0, 1.0, 1.0]],[[2, 0], [0, 1], [1, 3], [3, 2], [6, 2], [3, 7], [7, 6], [4, 6], [7, 5], [5, 4], [0, 4], [5, 1]],[[0, 1, 3, 2], [2, 3, 7, 6], [6, 7, 5, 4], [4, 5, 1, 0], [2, 6, 4, 0], [7, 3, 1, 5]])
obj=bpy.data.objects.new('cube_2_True',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
uv=mesh.uv_layers.new(name='UVMap')
coords=[[0.375, 0.0], [0.625, 0.0], [0.625, 0.25], [0.375, 0.25], [0.375, 0.25], [0.625, 0.25], [0.625, 0.5], [0.375, 0.5], [0.375, 0.5], [0.625, 0.5], [0.625, 0.75], [0.375, 0.75], [0.375, 0.75], [0.625, 0.75], [0.625, 1.0], [0.375, 1.0], [0.125, 0.5], [0.375, 0.5], [0.375, 0.75], [0.125, 0.75], [0.625, 0.5], [0.875, 0.5], [0.875, 0.75], [0.625, 0.75]]
for i,d in enumerate(uv.data):d.uv=coords[i]
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=2;mod.subdivision_type='SIMPLE'
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('cube_4_False')
mesh.from_pydata([[-1.0, -1.0, -1.0], [-1.0, -1.0, 1.0], [-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, -1.0, -1.0], [1.0, -1.0, 1.0], [1.0, 1.0, -1.0], [1.0, 1.0, 1.0]],[[2, 0], [0, 1], [1, 3], [3, 2], [6, 2], [3, 7], [7, 6], [4, 6], [7, 5], [5, 4], [0, 4], [5, 1]],[[0, 1, 3, 2], [2, 3, 7, 6], [6, 7, 5, 4], [4, 5, 1, 0], [2, 6, 4, 0], [7, 3, 1, 5]])
obj=bpy.data.objects.new('cube_4_False',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
uv=mesh.uv_layers.new(name='UVMap')
coords=[[0.375, 0.0], [0.625, 0.0], [0.625, 0.25], [0.375, 0.25], [0.375, 0.25], [0.625, 0.25], [0.625, 0.5], [0.375, 0.5], [0.375, 0.5], [0.625, 0.5], [0.625, 0.75], [0.375, 0.75], [0.375, 0.75], [0.625, 0.75], [0.625, 1.0], [0.375, 1.0], [0.125, 0.5], [0.375, 0.5], [0.375, 0.75], [0.125, 0.75], [0.625, 0.5], [0.875, 0.5], [0.875, 0.75], [0.625, 0.75]]
for i,d in enumerate(uv.data):d.uv=coords[i]
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=4;mod.subdivision_type='CATMULL_CLARK'
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('cube_4_True')
mesh.from_pydata([[-1.0, -1.0, -1.0], [-1.0, -1.0, 1.0], [-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, -1.0, -1.0], [1.0, -1.0, 1.0], [1.0, 1.0, -1.0], [1.0, 1.0, 1.0]],[[2, 0], [0, 1], [1, 3], [3, 2], [6, 2], [3, 7], [7, 6], [4, 6], [7, 5], [5, 4], [0, 4], [5, 1]],[[0, 1, 3, 2], [2, 3, 7, 6], [6, 7, 5, 4], [4, 5, 1, 0], [2, 6, 4, 0], [7, 3, 1, 5]])
obj=bpy.data.objects.new('cube_4_True',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
uv=mesh.uv_layers.new(name='UVMap')
coords=[[0.375, 0.0], [0.625, 0.0], [0.625, 0.25], [0.375, 0.25], [0.375, 0.25], [0.625, 0.25], [0.625, 0.5], [0.375, 0.5], [0.375, 0.5], [0.625, 0.5], [0.625, 0.75], [0.375, 0.75], [0.375, 0.75], [0.625, 0.75], [0.625, 1.0], [0.375, 1.0], [0.125, 0.5], [0.375, 0.5], [0.375, 0.75], [0.125, 0.75], [0.625, 0.5], [0.875, 0.5], [0.875, 0.75], [0.625, 0.75]]
for i,d in enumerate(uv.data):d.uv=coords[i]
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=4;mod.subdivision_type='SIMPLE'
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('crease_edge_1_False')
mesh.from_pydata([[-1.0, -1.0, -1.0], [-1.0, -1.0, 1.0], [-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, -1.0, -1.0], [1.0, -1.0, 1.0], [1.0, 1.0, -1.0], [1.0, 1.0, 1.0]],[[2, 0], [0, 1], [1, 3], [3, 2], [6, 2], [3, 7], [7, 6], [4, 6], [7, 5], [5, 4], [0, 4], [5, 1]],[[0, 1, 3, 2], [2, 3, 7, 6], [6, 7, 5, 4], [4, 5, 1, 0], [2, 6, 4, 0], [7, 3, 1, 5]])
obj=bpy.data.objects.new('crease_edge_1_False',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
uv=mesh.uv_layers.new(name='UVMap')
coords=[[0.375, 0.0], [0.625, 0.0], [0.625, 0.25], [0.375, 0.25], [0.375, 0.25], [0.625, 0.25], [0.625, 0.5], [0.375, 0.5], [0.375, 0.5], [0.625, 0.5], [0.625, 0.75], [0.375, 0.75], [0.375, 0.75], [0.625, 0.75], [0.625, 1.0], [0.375, 1.0], [0.125, 0.5], [0.375, 0.5], [0.375, 0.75], [0.125, 0.75], [0.625, 0.5], [0.875, 0.5], [0.875, 0.75], [0.625, 0.75]]
for i,d in enumerate(uv.data):d.uv=coords[i]
attr=mesh.attributes.new(name='crease_edge',type='FLOAT',domain='EDGE')
for i,d in enumerate(attr.data):d.value=(i%3)*.5
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=1;mod.subdivision_type='CATMULL_CLARK'
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('crease_edge_1_True')
mesh.from_pydata([[-1.0, -1.0, -1.0], [-1.0, -1.0, 1.0], [-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, -1.0, -1.0], [1.0, -1.0, 1.0], [1.0, 1.0, -1.0], [1.0, 1.0, 1.0]],[[2, 0], [0, 1], [1, 3], [3, 2], [6, 2], [3, 7], [7, 6], [4, 6], [7, 5], [5, 4], [0, 4], [5, 1]],[[0, 1, 3, 2], [2, 3, 7, 6], [6, 7, 5, 4], [4, 5, 1, 0], [2, 6, 4, 0], [7, 3, 1, 5]])
obj=bpy.data.objects.new('crease_edge_1_True',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
uv=mesh.uv_layers.new(name='UVMap')
coords=[[0.375, 0.0], [0.625, 0.0], [0.625, 0.25], [0.375, 0.25], [0.375, 0.25], [0.625, 0.25], [0.625, 0.5], [0.375, 0.5], [0.375, 0.5], [0.625, 0.5], [0.625, 0.75], [0.375, 0.75], [0.375, 0.75], [0.625, 0.75], [0.625, 1.0], [0.375, 1.0], [0.125, 0.5], [0.375, 0.5], [0.375, 0.75], [0.125, 0.75], [0.625, 0.5], [0.875, 0.5], [0.875, 0.75], [0.625, 0.75]]
for i,d in enumerate(uv.data):d.uv=coords[i]
attr=mesh.attributes.new(name='crease_edge',type='FLOAT',domain='EDGE')
for i,d in enumerate(attr.data):d.value=(i%3)*.5
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=1;mod.subdivision_type='SIMPLE'
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('crease_edge_2_False')
mesh.from_pydata([[-1.0, -1.0, -1.0], [-1.0, -1.0, 1.0], [-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, -1.0, -1.0], [1.0, -1.0, 1.0], [1.0, 1.0, -1.0], [1.0, 1.0, 1.0]],[[2, 0], [0, 1], [1, 3], [3, 2], [6, 2], [3, 7], [7, 6], [4, 6], [7, 5], [5, 4], [0, 4], [5, 1]],[[0, 1, 3, 2], [2, 3, 7, 6], [6, 7, 5, 4], [4, 5, 1, 0], [2, 6, 4, 0], [7, 3, 1, 5]])
obj=bpy.data.objects.new('crease_edge_2_False',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
uv=mesh.uv_layers.new(name='UVMap')
coords=[[0.375, 0.0], [0.625, 0.0], [0.625, 0.25], [0.375, 0.25], [0.375, 0.25], [0.625, 0.25], [0.625, 0.5], [0.375, 0.5], [0.375, 0.5], [0.625, 0.5], [0.625, 0.75], [0.375, 0.75], [0.375, 0.75], [0.625, 0.75], [0.625, 1.0], [0.375, 1.0], [0.125, 0.5], [0.375, 0.5], [0.375, 0.75], [0.125, 0.75], [0.625, 0.5], [0.875, 0.5], [0.875, 0.75], [0.625, 0.75]]
for i,d in enumerate(uv.data):d.uv=coords[i]
attr=mesh.attributes.new(name='crease_edge',type='FLOAT',domain='EDGE')
for i,d in enumerate(attr.data):d.value=(i%3)*.5
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=2;mod.subdivision_type='CATMULL_CLARK'
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('crease_edge_2_True')
mesh.from_pydata([[-1.0, -1.0, -1.0], [-1.0, -1.0, 1.0], [-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, -1.0, -1.0], [1.0, -1.0, 1.0], [1.0, 1.0, -1.0], [1.0, 1.0, 1.0]],[[2, 0], [0, 1], [1, 3], [3, 2], [6, 2], [3, 7], [7, 6], [4, 6], [7, 5], [5, 4], [0, 4], [5, 1]],[[0, 1, 3, 2], [2, 3, 7, 6], [6, 7, 5, 4], [4, 5, 1, 0], [2, 6, 4, 0], [7, 3, 1, 5]])
obj=bpy.data.objects.new('crease_edge_2_True',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
uv=mesh.uv_layers.new(name='UVMap')
coords=[[0.375, 0.0], [0.625, 0.0], [0.625, 0.25], [0.375, 0.25], [0.375, 0.25], [0.625, 0.25], [0.625, 0.5], [0.375, 0.5], [0.375, 0.5], [0.625, 0.5], [0.625, 0.75], [0.375, 0.75], [0.375, 0.75], [0.625, 0.75], [0.625, 1.0], [0.375, 1.0], [0.125, 0.5], [0.375, 0.5], [0.375, 0.75], [0.125, 0.75], [0.625, 0.5], [0.875, 0.5], [0.875, 0.75], [0.625, 0.75]]
for i,d in enumerate(uv.data):d.uv=coords[i]
attr=mesh.attributes.new(name='crease_edge',type='FLOAT',domain='EDGE')
for i,d in enumerate(attr.data):d.value=(i%3)*.5
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=2;mod.subdivision_type='SIMPLE'
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('crease_edge_4_False')
mesh.from_pydata([[-1.0, -1.0, -1.0], [-1.0, -1.0, 1.0], [-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, -1.0, -1.0], [1.0, -1.0, 1.0], [1.0, 1.0, -1.0], [1.0, 1.0, 1.0]],[[2, 0], [0, 1], [1, 3], [3, 2], [6, 2], [3, 7], [7, 6], [4, 6], [7, 5], [5, 4], [0, 4], [5, 1]],[[0, 1, 3, 2], [2, 3, 7, 6], [6, 7, 5, 4], [4, 5, 1, 0], [2, 6, 4, 0], [7, 3, 1, 5]])
obj=bpy.data.objects.new('crease_edge_4_False',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
uv=mesh.uv_layers.new(name='UVMap')
coords=[[0.375, 0.0], [0.625, 0.0], [0.625, 0.25], [0.375, 0.25], [0.375, 0.25], [0.625, 0.25], [0.625, 0.5], [0.375, 0.5], [0.375, 0.5], [0.625, 0.5], [0.625, 0.75], [0.375, 0.75], [0.375, 0.75], [0.625, 0.75], [0.625, 1.0], [0.375, 1.0], [0.125, 0.5], [0.375, 0.5], [0.375, 0.75], [0.125, 0.75], [0.625, 0.5], [0.875, 0.5], [0.875, 0.75], [0.625, 0.75]]
for i,d in enumerate(uv.data):d.uv=coords[i]
attr=mesh.attributes.new(name='crease_edge',type='FLOAT',domain='EDGE')
for i,d in enumerate(attr.data):d.value=(i%3)*.5
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=4;mod.subdivision_type='CATMULL_CLARK'
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('crease_edge_4_True')
mesh.from_pydata([[-1.0, -1.0, -1.0], [-1.0, -1.0, 1.0], [-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, -1.0, -1.0], [1.0, -1.0, 1.0], [1.0, 1.0, -1.0], [1.0, 1.0, 1.0]],[[2, 0], [0, 1], [1, 3], [3, 2], [6, 2], [3, 7], [7, 6], [4, 6], [7, 5], [5, 4], [0, 4], [5, 1]],[[0, 1, 3, 2], [2, 3, 7, 6], [6, 7, 5, 4], [4, 5, 1, 0], [2, 6, 4, 0], [7, 3, 1, 5]])
obj=bpy.data.objects.new('crease_edge_4_True',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
uv=mesh.uv_layers.new(name='UVMap')
coords=[[0.375, 0.0], [0.625, 0.0], [0.625, 0.25], [0.375, 0.25], [0.375, 0.25], [0.625, 0.25], [0.625, 0.5], [0.375, 0.5], [0.375, 0.5], [0.625, 0.5], [0.625, 0.75], [0.375, 0.75], [0.375, 0.75], [0.625, 0.75], [0.625, 1.0], [0.375, 1.0], [0.125, 0.5], [0.375, 0.5], [0.375, 0.75], [0.125, 0.75], [0.625, 0.5], [0.875, 0.5], [0.875, 0.75], [0.625, 0.75]]
for i,d in enumerate(uv.data):d.uv=coords[i]
attr=mesh.attributes.new(name='crease_edge',type='FLOAT',domain='EDGE')
for i,d in enumerate(attr.data):d.value=(i%3)*.5
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=4;mod.subdivision_type='SIMPLE'
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('crease_vert_1_False')
mesh.from_pydata([[-1.0, -1.0, -1.0], [-1.0, -1.0, 1.0], [-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, -1.0, -1.0], [1.0, -1.0, 1.0], [1.0, 1.0, -1.0], [1.0, 1.0, 1.0]],[[2, 0], [0, 1], [1, 3], [3, 2], [6, 2], [3, 7], [7, 6], [4, 6], [7, 5], [5, 4], [0, 4], [5, 1]],[[0, 1, 3, 2], [2, 3, 7, 6], [6, 7, 5, 4], [4, 5, 1, 0], [2, 6, 4, 0], [7, 3, 1, 5]])
obj=bpy.data.objects.new('crease_vert_1_False',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
uv=mesh.uv_layers.new(name='UVMap')
coords=[[0.375, 0.0], [0.625, 0.0], [0.625, 0.25], [0.375, 0.25], [0.375, 0.25], [0.625, 0.25], [0.625, 0.5], [0.375, 0.5], [0.375, 0.5], [0.625, 0.5], [0.625, 0.75], [0.375, 0.75], [0.375, 0.75], [0.625, 0.75], [0.625, 1.0], [0.375, 1.0], [0.125, 0.5], [0.375, 0.5], [0.375, 0.75], [0.125, 0.75], [0.625, 0.5], [0.875, 0.5], [0.875, 0.75], [0.625, 0.75]]
for i,d in enumerate(uv.data):d.uv=coords[i]
attr=mesh.attributes.new(name='crease_vert',type='FLOAT',domain='POINT')
for i,d in enumerate(attr.data):d.value=(i%3)*.5
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=1;mod.subdivision_type='CATMULL_CLARK'
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('crease_vert_1_True')
mesh.from_pydata([[-1.0, -1.0, -1.0], [-1.0, -1.0, 1.0], [-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, -1.0, -1.0], [1.0, -1.0, 1.0], [1.0, 1.0, -1.0], [1.0, 1.0, 1.0]],[[2, 0], [0, 1], [1, 3], [3, 2], [6, 2], [3, 7], [7, 6], [4, 6], [7, 5], [5, 4], [0, 4], [5, 1]],[[0, 1, 3, 2], [2, 3, 7, 6], [6, 7, 5, 4], [4, 5, 1, 0], [2, 6, 4, 0], [7, 3, 1, 5]])
obj=bpy.data.objects.new('crease_vert_1_True',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
uv=mesh.uv_layers.new(name='UVMap')
coords=[[0.375, 0.0], [0.625, 0.0], [0.625, 0.25], [0.375, 0.25], [0.375, 0.25], [0.625, 0.25], [0.625, 0.5], [0.375, 0.5], [0.375, 0.5], [0.625, 0.5], [0.625, 0.75], [0.375, 0.75], [0.375, 0.75], [0.625, 0.75], [0.625, 1.0], [0.375, 1.0], [0.125, 0.5], [0.375, 0.5], [0.375, 0.75], [0.125, 0.75], [0.625, 0.5], [0.875, 0.5], [0.875, 0.75], [0.625, 0.75]]
for i,d in enumerate(uv.data):d.uv=coords[i]
attr=mesh.attributes.new(name='crease_vert',type='FLOAT',domain='POINT')
for i,d in enumerate(attr.data):d.value=(i%3)*.5
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=1;mod.subdivision_type='SIMPLE'
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('crease_vert_2_False')
mesh.from_pydata([[-1.0, -1.0, -1.0], [-1.0, -1.0, 1.0], [-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, -1.0, -1.0], [1.0, -1.0, 1.0], [1.0, 1.0, -1.0], [1.0, 1.0, 1.0]],[[2, 0], [0, 1], [1, 3], [3, 2], [6, 2], [3, 7], [7, 6], [4, 6], [7, 5], [5, 4], [0, 4], [5, 1]],[[0, 1, 3, 2], [2, 3, 7, 6], [6, 7, 5, 4], [4, 5, 1, 0], [2, 6, 4, 0], [7, 3, 1, 5]])
obj=bpy.data.objects.new('crease_vert_2_False',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
uv=mesh.uv_layers.new(name='UVMap')
coords=[[0.375, 0.0], [0.625, 0.0], [0.625, 0.25], [0.375, 0.25], [0.375, 0.25], [0.625, 0.25], [0.625, 0.5], [0.375, 0.5], [0.375, 0.5], [0.625, 0.5], [0.625, 0.75], [0.375, 0.75], [0.375, 0.75], [0.625, 0.75], [0.625, 1.0], [0.375, 1.0], [0.125, 0.5], [0.375, 0.5], [0.375, 0.75], [0.125, 0.75], [0.625, 0.5], [0.875, 0.5], [0.875, 0.75], [0.625, 0.75]]
for i,d in enumerate(uv.data):d.uv=coords[i]
attr=mesh.attributes.new(name='crease_vert',type='FLOAT',domain='POINT')
for i,d in enumerate(attr.data):d.value=(i%3)*.5
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=2;mod.subdivision_type='CATMULL_CLARK'
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('crease_vert_2_True')
mesh.from_pydata([[-1.0, -1.0, -1.0], [-1.0, -1.0, 1.0], [-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, -1.0, -1.0], [1.0, -1.0, 1.0], [1.0, 1.0, -1.0], [1.0, 1.0, 1.0]],[[2, 0], [0, 1], [1, 3], [3, 2], [6, 2], [3, 7], [7, 6], [4, 6], [7, 5], [5, 4], [0, 4], [5, 1]],[[0, 1, 3, 2], [2, 3, 7, 6], [6, 7, 5, 4], [4, 5, 1, 0], [2, 6, 4, 0], [7, 3, 1, 5]])
obj=bpy.data.objects.new('crease_vert_2_True',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
uv=mesh.uv_layers.new(name='UVMap')
coords=[[0.375, 0.0], [0.625, 0.0], [0.625, 0.25], [0.375, 0.25], [0.375, 0.25], [0.625, 0.25], [0.625, 0.5], [0.375, 0.5], [0.375, 0.5], [0.625, 0.5], [0.625, 0.75], [0.375, 0.75], [0.375, 0.75], [0.625, 0.75], [0.625, 1.0], [0.375, 1.0], [0.125, 0.5], [0.375, 0.5], [0.375, 0.75], [0.125, 0.75], [0.625, 0.5], [0.875, 0.5], [0.875, 0.75], [0.625, 0.75]]
for i,d in enumerate(uv.data):d.uv=coords[i]
attr=mesh.attributes.new(name='crease_vert',type='FLOAT',domain='POINT')
for i,d in enumerate(attr.data):d.value=(i%3)*.5
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=2;mod.subdivision_type='SIMPLE'
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('crease_vert_4_False')
mesh.from_pydata([[-1.0, -1.0, -1.0], [-1.0, -1.0, 1.0], [-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, -1.0, -1.0], [1.0, -1.0, 1.0], [1.0, 1.0, -1.0], [1.0, 1.0, 1.0]],[[2, 0], [0, 1], [1, 3], [3, 2], [6, 2], [3, 7], [7, 6], [4, 6], [7, 5], [5, 4], [0, 4], [5, 1]],[[0, 1, 3, 2], [2, 3, 7, 6], [6, 7, 5, 4], [4, 5, 1, 0], [2, 6, 4, 0], [7, 3, 1, 5]])
obj=bpy.data.objects.new('crease_vert_4_False',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
uv=mesh.uv_layers.new(name='UVMap')
coords=[[0.375, 0.0], [0.625, 0.0], [0.625, 0.25], [0.375, 0.25], [0.375, 0.25], [0.625, 0.25], [0.625, 0.5], [0.375, 0.5], [0.375, 0.5], [0.625, 0.5], [0.625, 0.75], [0.375, 0.75], [0.375, 0.75], [0.625, 0.75], [0.625, 1.0], [0.375, 1.0], [0.125, 0.5], [0.375, 0.5], [0.375, 0.75], [0.125, 0.75], [0.625, 0.5], [0.875, 0.5], [0.875, 0.75], [0.625, 0.75]]
for i,d in enumerate(uv.data):d.uv=coords[i]
attr=mesh.attributes.new(name='crease_vert',type='FLOAT',domain='POINT')
for i,d in enumerate(attr.data):d.value=(i%3)*.5
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=4;mod.subdivision_type='CATMULL_CLARK'
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('crease_vert_4_True')
mesh.from_pydata([[-1.0, -1.0, -1.0], [-1.0, -1.0, 1.0], [-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, -1.0, -1.0], [1.0, -1.0, 1.0], [1.0, 1.0, -1.0], [1.0, 1.0, 1.0]],[[2, 0], [0, 1], [1, 3], [3, 2], [6, 2], [3, 7], [7, 6], [4, 6], [7, 5], [5, 4], [0, 4], [5, 1]],[[0, 1, 3, 2], [2, 3, 7, 6], [6, 7, 5, 4], [4, 5, 1, 0], [2, 6, 4, 0], [7, 3, 1, 5]])
obj=bpy.data.objects.new('crease_vert_4_True',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
uv=mesh.uv_layers.new(name='UVMap')
coords=[[0.375, 0.0], [0.625, 0.0], [0.625, 0.25], [0.375, 0.25], [0.375, 0.25], [0.625, 0.25], [0.625, 0.5], [0.375, 0.5], [0.375, 0.5], [0.625, 0.5], [0.625, 0.75], [0.375, 0.75], [0.375, 0.75], [0.625, 0.75], [0.625, 1.0], [0.375, 1.0], [0.125, 0.5], [0.375, 0.5], [0.375, 0.75], [0.125, 0.75], [0.625, 0.5], [0.875, 0.5], [0.875, 0.75], [0.625, 0.75]]
for i,d in enumerate(uv.data):d.uv=coords[i]
attr=mesh.attributes.new(name='crease_vert',type='FLOAT',domain='POINT')
for i,d in enumerate(attr.data):d.value=(i%3)*.5
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=4;mod.subdivision_type='SIMPLE'
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('custom_1_False')
mesh.from_pydata([[-1.0, -1.0, -1.0], [-1.0, -1.0, 1.0], [-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, -1.0, -1.0], [1.0, -1.0, 1.0], [1.0, 1.0, -1.0], [1.0, 1.0, 1.0]],[[2, 0], [0, 1], [1, 3], [3, 2], [6, 2], [3, 7], [7, 6], [4, 6], [7, 5], [5, 4], [0, 4], [5, 1]],[[0, 1, 3, 2], [2, 3, 7, 6], [6, 7, 5, 4], [4, 5, 1, 0], [2, 6, 4, 0], [7, 3, 1, 5]])
obj=bpy.data.objects.new('custom_1_False',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
uv=mesh.uv_layers.new(name='UVMap')
coords=[[0.375, 0.0], [0.625, 0.0], [0.625, 0.25], [0.375, 0.25], [0.375, 0.25], [0.625, 0.25], [0.625, 0.5], [0.375, 0.5], [0.375, 0.5], [0.625, 0.5], [0.625, 0.75], [0.375, 0.75], [0.375, 0.75], [0.625, 0.75], [0.625, 1.0], [0.375, 1.0], [0.125, 0.5], [0.375, 0.5], [0.375, 0.75], [0.125, 0.75], [0.625, 0.5], [0.875, 0.5], [0.875, 0.75], [0.625, 0.75]]
for i,d in enumerate(uv.data):d.uv=coords[i]
mesh.normals_split_custom_set([(0,.2,1)]*24)
color=mesh.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='CORNER')
for i,d in enumerate(color.data):d.color=(i/24,.2,.4,1)
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=1;mod.subdivision_type='CATMULL_CLARK'
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('custom_1_False_preserve')
mesh.from_pydata([[-1.0, -1.0, -1.0], [-1.0, -1.0, 1.0], [-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, -1.0, -1.0], [1.0, -1.0, 1.0], [1.0, 1.0, -1.0], [1.0, 1.0, 1.0]],[[2, 0], [0, 1], [1, 3], [3, 2], [6, 2], [3, 7], [7, 6], [4, 6], [7, 5], [5, 4], [0, 4], [5, 1]],[[0, 1, 3, 2], [2, 3, 7, 6], [6, 7, 5, 4], [4, 5, 1, 0], [2, 6, 4, 0], [7, 3, 1, 5]])
obj=bpy.data.objects.new('custom_1_False_preserve',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
uv=mesh.uv_layers.new(name='UVMap')
coords=[[0.375, 0.0], [0.625, 0.0], [0.625, 0.25], [0.375, 0.25], [0.375, 0.25], [0.625, 0.25], [0.625, 0.5], [0.375, 0.5], [0.375, 0.5], [0.625, 0.5], [0.625, 0.75], [0.375, 0.75], [0.375, 0.75], [0.625, 0.75], [0.625, 1.0], [0.375, 1.0], [0.125, 0.5], [0.375, 0.5], [0.375, 0.75], [0.125, 0.75], [0.625, 0.5], [0.875, 0.5], [0.875, 0.75], [0.625, 0.75]]
for i,d in enumerate(uv.data):d.uv=coords[i]
mesh.normals_split_custom_set([(0,.2,1)]*24)
color=mesh.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='CORNER')
for i,d in enumerate(color.data):d.color=(i/24,.2,.4,1)
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=1;mod.subdivision_type='CATMULL_CLARK';mod.use_custom_normals=True
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('custom_1_True')
mesh.from_pydata([[-1.0, -1.0, -1.0], [-1.0, -1.0, 1.0], [-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, -1.0, -1.0], [1.0, -1.0, 1.0], [1.0, 1.0, -1.0], [1.0, 1.0, 1.0]],[[2, 0], [0, 1], [1, 3], [3, 2], [6, 2], [3, 7], [7, 6], [4, 6], [7, 5], [5, 4], [0, 4], [5, 1]],[[0, 1, 3, 2], [2, 3, 7, 6], [6, 7, 5, 4], [4, 5, 1, 0], [2, 6, 4, 0], [7, 3, 1, 5]])
obj=bpy.data.objects.new('custom_1_True',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
uv=mesh.uv_layers.new(name='UVMap')
coords=[[0.375, 0.0], [0.625, 0.0], [0.625, 0.25], [0.375, 0.25], [0.375, 0.25], [0.625, 0.25], [0.625, 0.5], [0.375, 0.5], [0.375, 0.5], [0.625, 0.5], [0.625, 0.75], [0.375, 0.75], [0.375, 0.75], [0.625, 0.75], [0.625, 1.0], [0.375, 1.0], [0.125, 0.5], [0.375, 0.5], [0.375, 0.75], [0.125, 0.75], [0.625, 0.5], [0.875, 0.5], [0.875, 0.75], [0.625, 0.75]]
for i,d in enumerate(uv.data):d.uv=coords[i]
mesh.normals_split_custom_set([(0,.2,1)]*24)
color=mesh.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='CORNER')
for i,d in enumerate(color.data):d.color=(i/24,.2,.4,1)
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=1;mod.subdivision_type='SIMPLE'
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('custom_1_True_preserve')
mesh.from_pydata([[-1.0, -1.0, -1.0], [-1.0, -1.0, 1.0], [-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, -1.0, -1.0], [1.0, -1.0, 1.0], [1.0, 1.0, -1.0], [1.0, 1.0, 1.0]],[[2, 0], [0, 1], [1, 3], [3, 2], [6, 2], [3, 7], [7, 6], [4, 6], [7, 5], [5, 4], [0, 4], [5, 1]],[[0, 1, 3, 2], [2, 3, 7, 6], [6, 7, 5, 4], [4, 5, 1, 0], [2, 6, 4, 0], [7, 3, 1, 5]])
obj=bpy.data.objects.new('custom_1_True_preserve',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
uv=mesh.uv_layers.new(name='UVMap')
coords=[[0.375, 0.0], [0.625, 0.0], [0.625, 0.25], [0.375, 0.25], [0.375, 0.25], [0.625, 0.25], [0.625, 0.5], [0.375, 0.5], [0.375, 0.5], [0.625, 0.5], [0.625, 0.75], [0.375, 0.75], [0.375, 0.75], [0.625, 0.75], [0.625, 1.0], [0.375, 1.0], [0.125, 0.5], [0.375, 0.5], [0.375, 0.75], [0.125, 0.75], [0.625, 0.5], [0.875, 0.5], [0.875, 0.75], [0.625, 0.75]]
for i,d in enumerate(uv.data):d.uv=coords[i]
mesh.normals_split_custom_set([(0,.2,1)]*24)
color=mesh.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='CORNER')
for i,d in enumerate(color.data):d.color=(i/24,.2,.4,1)
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=1;mod.subdivision_type='SIMPLE';mod.use_custom_normals=True
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('custom_2_False')
mesh.from_pydata([[-1.0, -1.0, -1.0], [-1.0, -1.0, 1.0], [-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, -1.0, -1.0], [1.0, -1.0, 1.0], [1.0, 1.0, -1.0], [1.0, 1.0, 1.0]],[[2, 0], [0, 1], [1, 3], [3, 2], [6, 2], [3, 7], [7, 6], [4, 6], [7, 5], [5, 4], [0, 4], [5, 1]],[[0, 1, 3, 2], [2, 3, 7, 6], [6, 7, 5, 4], [4, 5, 1, 0], [2, 6, 4, 0], [7, 3, 1, 5]])
obj=bpy.data.objects.new('custom_2_False',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
uv=mesh.uv_layers.new(name='UVMap')
coords=[[0.375, 0.0], [0.625, 0.0], [0.625, 0.25], [0.375, 0.25], [0.375, 0.25], [0.625, 0.25], [0.625, 0.5], [0.375, 0.5], [0.375, 0.5], [0.625, 0.5], [0.625, 0.75], [0.375, 0.75], [0.375, 0.75], [0.625, 0.75], [0.625, 1.0], [0.375, 1.0], [0.125, 0.5], [0.375, 0.5], [0.375, 0.75], [0.125, 0.75], [0.625, 0.5], [0.875, 0.5], [0.875, 0.75], [0.625, 0.75]]
for i,d in enumerate(uv.data):d.uv=coords[i]
mesh.normals_split_custom_set([(0,.2,1)]*24)
color=mesh.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='CORNER')
for i,d in enumerate(color.data):d.color=(i/24,.2,.4,1)
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=2;mod.subdivision_type='CATMULL_CLARK'
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('custom_2_False_preserve')
mesh.from_pydata([[-1.0, -1.0, -1.0], [-1.0, -1.0, 1.0], [-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, -1.0, -1.0], [1.0, -1.0, 1.0], [1.0, 1.0, -1.0], [1.0, 1.0, 1.0]],[[2, 0], [0, 1], [1, 3], [3, 2], [6, 2], [3, 7], [7, 6], [4, 6], [7, 5], [5, 4], [0, 4], [5, 1]],[[0, 1, 3, 2], [2, 3, 7, 6], [6, 7, 5, 4], [4, 5, 1, 0], [2, 6, 4, 0], [7, 3, 1, 5]])
obj=bpy.data.objects.new('custom_2_False_preserve',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
uv=mesh.uv_layers.new(name='UVMap')
coords=[[0.375, 0.0], [0.625, 0.0], [0.625, 0.25], [0.375, 0.25], [0.375, 0.25], [0.625, 0.25], [0.625, 0.5], [0.375, 0.5], [0.375, 0.5], [0.625, 0.5], [0.625, 0.75], [0.375, 0.75], [0.375, 0.75], [0.625, 0.75], [0.625, 1.0], [0.375, 1.0], [0.125, 0.5], [0.375, 0.5], [0.375, 0.75], [0.125, 0.75], [0.625, 0.5], [0.875, 0.5], [0.875, 0.75], [0.625, 0.75]]
for i,d in enumerate(uv.data):d.uv=coords[i]
mesh.normals_split_custom_set([(0,.2,1)]*24)
color=mesh.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='CORNER')
for i,d in enumerate(color.data):d.color=(i/24,.2,.4,1)
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=2;mod.subdivision_type='CATMULL_CLARK';mod.use_custom_normals=True
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('custom_2_True')
mesh.from_pydata([[-1.0, -1.0, -1.0], [-1.0, -1.0, 1.0], [-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, -1.0, -1.0], [1.0, -1.0, 1.0], [1.0, 1.0, -1.0], [1.0, 1.0, 1.0]],[[2, 0], [0, 1], [1, 3], [3, 2], [6, 2], [3, 7], [7, 6], [4, 6], [7, 5], [5, 4], [0, 4], [5, 1]],[[0, 1, 3, 2], [2, 3, 7, 6], [6, 7, 5, 4], [4, 5, 1, 0], [2, 6, 4, 0], [7, 3, 1, 5]])
obj=bpy.data.objects.new('custom_2_True',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
uv=mesh.uv_layers.new(name='UVMap')
coords=[[0.375, 0.0], [0.625, 0.0], [0.625, 0.25], [0.375, 0.25], [0.375, 0.25], [0.625, 0.25], [0.625, 0.5], [0.375, 0.5], [0.375, 0.5], [0.625, 0.5], [0.625, 0.75], [0.375, 0.75], [0.375, 0.75], [0.625, 0.75], [0.625, 1.0], [0.375, 1.0], [0.125, 0.5], [0.375, 0.5], [0.375, 0.75], [0.125, 0.75], [0.625, 0.5], [0.875, 0.5], [0.875, 0.75], [0.625, 0.75]]
for i,d in enumerate(uv.data):d.uv=coords[i]
mesh.normals_split_custom_set([(0,.2,1)]*24)
color=mesh.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='CORNER')
for i,d in enumerate(color.data):d.color=(i/24,.2,.4,1)
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=2;mod.subdivision_type='SIMPLE'
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('custom_2_True_preserve')
mesh.from_pydata([[-1.0, -1.0, -1.0], [-1.0, -1.0, 1.0], [-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, -1.0, -1.0], [1.0, -1.0, 1.0], [1.0, 1.0, -1.0], [1.0, 1.0, 1.0]],[[2, 0], [0, 1], [1, 3], [3, 2], [6, 2], [3, 7], [7, 6], [4, 6], [7, 5], [5, 4], [0, 4], [5, 1]],[[0, 1, 3, 2], [2, 3, 7, 6], [6, 7, 5, 4], [4, 5, 1, 0], [2, 6, 4, 0], [7, 3, 1, 5]])
obj=bpy.data.objects.new('custom_2_True_preserve',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
uv=mesh.uv_layers.new(name='UVMap')
coords=[[0.375, 0.0], [0.625, 0.0], [0.625, 0.25], [0.375, 0.25], [0.375, 0.25], [0.625, 0.25], [0.625, 0.5], [0.375, 0.5], [0.375, 0.5], [0.625, 0.5], [0.625, 0.75], [0.375, 0.75], [0.375, 0.75], [0.625, 0.75], [0.625, 1.0], [0.375, 1.0], [0.125, 0.5], [0.375, 0.5], [0.375, 0.75], [0.125, 0.75], [0.625, 0.5], [0.875, 0.5], [0.875, 0.75], [0.625, 0.75]]
for i,d in enumerate(uv.data):d.uv=coords[i]
mesh.normals_split_custom_set([(0,.2,1)]*24)
color=mesh.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='CORNER')
for i,d in enumerate(color.data):d.color=(i/24,.2,.4,1)
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=2;mod.subdivision_type='SIMPLE';mod.use_custom_normals=True
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('custom_4_False')
mesh.from_pydata([[-1.0, -1.0, -1.0], [-1.0, -1.0, 1.0], [-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, -1.0, -1.0], [1.0, -1.0, 1.0], [1.0, 1.0, -1.0], [1.0, 1.0, 1.0]],[[2, 0], [0, 1], [1, 3], [3, 2], [6, 2], [3, 7], [7, 6], [4, 6], [7, 5], [5, 4], [0, 4], [5, 1]],[[0, 1, 3, 2], [2, 3, 7, 6], [6, 7, 5, 4], [4, 5, 1, 0], [2, 6, 4, 0], [7, 3, 1, 5]])
obj=bpy.data.objects.new('custom_4_False',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
uv=mesh.uv_layers.new(name='UVMap')
coords=[[0.375, 0.0], [0.625, 0.0], [0.625, 0.25], [0.375, 0.25], [0.375, 0.25], [0.625, 0.25], [0.625, 0.5], [0.375, 0.5], [0.375, 0.5], [0.625, 0.5], [0.625, 0.75], [0.375, 0.75], [0.375, 0.75], [0.625, 0.75], [0.625, 1.0], [0.375, 1.0], [0.125, 0.5], [0.375, 0.5], [0.375, 0.75], [0.125, 0.75], [0.625, 0.5], [0.875, 0.5], [0.875, 0.75], [0.625, 0.75]]
for i,d in enumerate(uv.data):d.uv=coords[i]
mesh.normals_split_custom_set([(0,.2,1)]*24)
color=mesh.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='CORNER')
for i,d in enumerate(color.data):d.color=(i/24,.2,.4,1)
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=4;mod.subdivision_type='CATMULL_CLARK'
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('custom_4_True')
mesh.from_pydata([[-1.0, -1.0, -1.0], [-1.0, -1.0, 1.0], [-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, -1.0, -1.0], [1.0, -1.0, 1.0], [1.0, 1.0, -1.0], [1.0, 1.0, 1.0]],[[2, 0], [0, 1], [1, 3], [3, 2], [6, 2], [3, 7], [7, 6], [4, 6], [7, 5], [5, 4], [0, 4], [5, 1]],[[0, 1, 3, 2], [2, 3, 7, 6], [6, 7, 5, 4], [4, 5, 1, 0], [2, 6, 4, 0], [7, 3, 1, 5]])
obj=bpy.data.objects.new('custom_4_True',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
uv=mesh.uv_layers.new(name='UVMap')
coords=[[0.375, 0.0], [0.625, 0.0], [0.625, 0.25], [0.375, 0.25], [0.375, 0.25], [0.625, 0.25], [0.625, 0.5], [0.375, 0.5], [0.375, 0.5], [0.625, 0.5], [0.625, 0.75], [0.375, 0.75], [0.375, 0.75], [0.625, 0.75], [0.625, 1.0], [0.375, 1.0], [0.125, 0.5], [0.375, 0.5], [0.375, 0.75], [0.125, 0.75], [0.625, 0.5], [0.875, 0.5], [0.875, 0.75], [0.625, 0.75]]
for i,d in enumerate(uv.data):d.uv=coords[i]
mesh.normals_split_custom_set([(0,.2,1)]*24)
color=mesh.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='CORNER')
for i,d in enumerate(color.data):d.color=(i/24,.2,.4,1)
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=4;mod.subdivision_type='SIMPLE'
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('wire_1_False')
mesh.from_pydata([[0.0, 0.0, 0.0], [1.0, 1.0, 0.0], [2.0, 0.0, 0.0], [3.0, 1.0, 0.0]],[[0, 1], [1, 2], [2, 3]],[])
obj=bpy.data.objects.new('wire_1_False',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=1;mod.subdivision_type='CATMULL_CLARK'
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('wire_1_True')
mesh.from_pydata([[0.0, 0.0, 0.0], [1.0, 1.0, 0.0], [2.0, 0.0, 0.0], [3.0, 1.0, 0.0]],[[0, 1], [1, 2], [2, 3]],[])
obj=bpy.data.objects.new('wire_1_True',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=1;mod.subdivision_type='SIMPLE'
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('wire_2_False')
mesh.from_pydata([[0.0, 0.0, 0.0], [1.0, 1.0, 0.0], [2.0, 0.0, 0.0], [3.0, 1.0, 0.0]],[[0, 1], [1, 2], [2, 3]],[])
obj=bpy.data.objects.new('wire_2_False',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=2;mod.subdivision_type='CATMULL_CLARK'
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('wire_2_True')
mesh.from_pydata([[0.0, 0.0, 0.0], [1.0, 1.0, 0.0], [2.0, 0.0, 0.0], [3.0, 1.0, 0.0]],[[0, 1], [1, 2], [2, 3]],[])
obj=bpy.data.objects.new('wire_2_True',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=2;mod.subdivision_type='SIMPLE'
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('wire_4_False')
mesh.from_pydata([[0.0, 0.0, 0.0], [1.0, 1.0, 0.0], [2.0, 0.0, 0.0], [3.0, 1.0, 0.0]],[[0, 1], [1, 2], [2, 3]],[])
obj=bpy.data.objects.new('wire_4_False',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=4;mod.subdivision_type='CATMULL_CLARK'
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('wire_4_True')
mesh.from_pydata([[0.0, 0.0, 0.0], [1.0, 1.0, 0.0], [2.0, 0.0, 0.0], [3.0, 1.0, 0.0]],[[0, 1], [1, 2], [2, 3]],[])
obj=bpy.data.objects.new('wire_4_True',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=4;mod.subdivision_type='SIMPLE'
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('loose_vertex_1_False')
mesh.from_pydata([[2.0, 3.0, 4.0]],[],[])
obj=bpy.data.objects.new('loose_vertex_1_False',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=1;mod.subdivision_type='CATMULL_CLARK'
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('loose_vertex_1_True')
mesh.from_pydata([[2.0, 3.0, 4.0]],[],[])
obj=bpy.data.objects.new('loose_vertex_1_True',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=1;mod.subdivision_type='SIMPLE'
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('loose_vertex_2_False')
mesh.from_pydata([[2.0, 3.0, 4.0]],[],[])
obj=bpy.data.objects.new('loose_vertex_2_False',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=2;mod.subdivision_type='CATMULL_CLARK'
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('loose_vertex_2_True')
mesh.from_pydata([[2.0, 3.0, 4.0]],[],[])
obj=bpy.data.objects.new('loose_vertex_2_True',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=2;mod.subdivision_type='SIMPLE'
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('loose_vertex_4_False')
mesh.from_pydata([[2.0, 3.0, 4.0]],[],[])
obj=bpy.data.objects.new('loose_vertex_4_False',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=4;mod.subdivision_type='CATMULL_CLARK'
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('loose_vertex_4_True')
mesh.from_pydata([[2.0, 3.0, 4.0]],[],[])
obj=bpy.data.objects.new('loose_vertex_4_True',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=4;mod.subdivision_type='SIMPLE'
bpy.ops.object.modifier_apply(modifier=mod.name)

import bpy
mesh=bpy.data.meshes.new('creased_off')
mesh.from_pydata([[-1.0, -1.0, -1.0], [-1.0, -1.0, 1.0], [-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, -1.0, -1.0], [1.0, -1.0, 1.0], [1.0, 1.0, -1.0], [1.0, 1.0, 1.0]],[[2, 0], [0, 1], [1, 3], [3, 2], [6, 2], [3, 7], [7, 6], [4, 6], [7, 5], [5, 4], [0, 4], [5, 1]],[[0, 1, 3, 2], [2, 3, 7, 6], [6, 7, 5, 4], [4, 5, 1, 0], [2, 6, 4, 0], [7, 3, 1, 5]])
obj=bpy.data.objects.new('creased_off',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
smooth=[False, False, False, False, False, False]
for i,face in enumerate(mesh.polygons):face.use_smooth=smooth[i]
uv=mesh.uv_layers.new(name='UVMap')
coords=[[0.375, 0.0], [0.625, 0.0], [0.625, 0.25], [0.375, 0.25], [0.375, 0.25], [0.625, 0.25], [0.625, 0.5], [0.375, 0.5], [0.375, 0.5], [0.625, 0.5], [0.625, 0.75], [0.375, 0.75], [0.375, 0.75], [0.625, 0.75], [0.625, 1.0], [0.375, 1.0], [0.125, 0.5], [0.375, 0.5], [0.375, 0.75], [0.125, 0.75], [0.625, 0.5], [0.875, 0.5], [0.875, 0.75], [0.625, 0.75]]
for i,uv_value in enumerate(uv.data):uv_value.uv=coords[i]
a=mesh.attributes.new(name='crease_edge',type='FLOAT',domain='EDGE')
weights=[0.0, 0.4000000059604645, 0.800000011920929, 0.0, 0.4000000059604645, 0.800000011920929, 0.0, 0.4000000059604645, 0.800000011920929, 0.0, 0.4000000059604645, 0.800000011920929]
for i,crease_value in enumerate(a.data):crease_value.value=weights[i]
a=mesh.attributes.new(name='crease_vert',type='FLOAT',domain='POINT')
weights=[0.0, 0.25, 0.5, 0.75, 0.0, 0.25, 0.5, 0.75]
for i,crease_value in enumerate(a.data):crease_value.value=weights[i]
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=2
mod.use_creases=False
mod.use_limit_surface=True
mod.use_custom_normals=False
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('finite')
mesh.from_pydata([[-1.0, -1.0, -1.0], [-1.0, -1.0, 1.0], [-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, -1.0, -1.0], [1.0, -1.0, 1.0], [1.0, 1.0, -1.0], [1.0, 1.0, 1.0]],[[2, 0], [0, 1], [1, 3], [3, 2], [6, 2], [3, 7], [7, 6], [4, 6], [7, 5], [5, 4], [0, 4], [5, 1]],[[0, 1, 3, 2], [2, 3, 7, 6], [6, 7, 5, 4], [4, 5, 1, 0], [2, 6, 4, 0], [7, 3, 1, 5]])
obj=bpy.data.objects.new('finite',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
smooth=[False, False, False, False, False, False]
for i,face in enumerate(mesh.polygons):face.use_smooth=smooth[i]
uv=mesh.uv_layers.new(name='UVMap')
coords=[[0.375, 0.0], [0.625, 0.0], [0.625, 0.25], [0.375, 0.25], [0.375, 0.25], [0.625, 0.25], [0.625, 0.5], [0.375, 0.5], [0.375, 0.5], [0.625, 0.5], [0.625, 0.75], [0.375, 0.75], [0.375, 0.75], [0.625, 0.75], [0.625, 1.0], [0.375, 1.0], [0.125, 0.5], [0.375, 0.5], [0.375, 0.75], [0.125, 0.75], [0.625, 0.5], [0.875, 0.5], [0.875, 0.75], [0.625, 0.75]]
for i,uv_value in enumerate(uv.data):uv_value.uv=coords[i]
a=mesh.attributes.new(name='crease_edge',type='FLOAT',domain='EDGE')
weights=[0.0, 0.4000000059604645, 0.800000011920929, 0.0, 0.4000000059604645, 0.800000011920929, 0.0, 0.4000000059604645, 0.800000011920929, 0.0, 0.4000000059604645, 0.800000011920929]
for i,crease_value in enumerate(a.data):crease_value.value=weights[i]
a=mesh.attributes.new(name='crease_vert',type='FLOAT',domain='POINT')
weights=[0.0, 0.25, 0.5, 0.75, 0.0, 0.25, 0.5, 0.75]
for i,crease_value in enumerate(a.data):crease_value.value=weights[i]
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=2
mod.use_creases=True
mod.use_limit_surface=False
mod.use_custom_normals=False
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('level6')
mesh.from_pydata([[-1.0, -1.0, -1.0], [-1.0, -1.0, 1.0], [-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, -1.0, -1.0], [1.0, -1.0, 1.0], [1.0, 1.0, -1.0], [1.0, 1.0, 1.0]],[[2, 0], [0, 1], [1, 3], [3, 2], [6, 2], [3, 7], [7, 6], [4, 6], [7, 5], [5, 4], [0, 4], [5, 1]],[[0, 1, 3, 2], [2, 3, 7, 6], [6, 7, 5, 4], [4, 5, 1, 0], [2, 6, 4, 0], [7, 3, 1, 5]])
obj=bpy.data.objects.new('level6',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
smooth=[False, False, False, False, False, False]
for i,face in enumerate(mesh.polygons):face.use_smooth=smooth[i]
uv=mesh.uv_layers.new(name='UVMap')
coords=[[0.375, 0.0], [0.625, 0.0], [0.625, 0.25], [0.375, 0.25], [0.375, 0.25], [0.625, 0.25], [0.625, 0.5], [0.375, 0.5], [0.375, 0.5], [0.625, 0.5], [0.625, 0.75], [0.375, 0.75], [0.375, 0.75], [0.625, 0.75], [0.625, 1.0], [0.375, 1.0], [0.125, 0.5], [0.375, 0.5], [0.375, 0.75], [0.125, 0.75], [0.625, 0.5], [0.875, 0.5], [0.875, 0.75], [0.625, 0.75]]
for i,uv_value in enumerate(uv.data):uv_value.uv=coords[i]
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=6
mod.use_creases=True
mod.use_limit_surface=True
mod.use_custom_normals=False
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('smooth_normals')
mesh.from_pydata([[-1.0, -1.0, -1.0], [-1.0, -1.0, 1.0], [-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, -1.0, -1.0], [1.0, -1.0, 1.0], [1.0, 1.0, -1.0], [1.0, 1.0, 1.0]],[[2, 0], [0, 1], [1, 3], [3, 2], [6, 2], [3, 7], [7, 6], [4, 6], [7, 5], [5, 4], [0, 4], [5, 1]],[[0, 1, 3, 2], [2, 3, 7, 6], [6, 7, 5, 4], [4, 5, 1, 0], [2, 6, 4, 0], [7, 3, 1, 5]])
obj=bpy.data.objects.new('smooth_normals',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
smooth=[True, True, True, True, True, True]
for i,face in enumerate(mesh.polygons):face.use_smooth=smooth[i]
uv=mesh.uv_layers.new(name='UVMap')
coords=[[0.375, 0.0], [0.625, 0.0], [0.625, 0.25], [0.375, 0.25], [0.375, 0.25], [0.625, 0.25], [0.625, 0.5], [0.375, 0.5], [0.375, 0.5], [0.625, 0.5], [0.625, 0.75], [0.375, 0.75], [0.375, 0.75], [0.625, 0.75], [0.625, 1.0], [0.375, 1.0], [0.125, 0.5], [0.375, 0.5], [0.375, 0.75], [0.125, 0.75], [0.625, 0.5], [0.875, 0.5], [0.875, 0.75], [0.625, 0.75]]
for i,uv_value in enumerate(uv.data):uv_value.uv=coords[i]
mesh.normals_split_custom_set([(0,.2,1)]*24)
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=2
mod.use_creases=True
mod.use_limit_surface=True
mod.use_custom_normals=False
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('ngon_colors')
mesh.from_pydata([[1.0, 0.0, 0.0], [0.30901700258255005, 0.9510565400123596, 0.0], [-0.80901700258255, 0.5877852439880371, 0.0], [-0.80901700258255, -0.5877852439880371, 0.0], [0.30901700258255005, -0.9510565400123596, 0.0]],[[0, 4], [0, 1], [1, 2], [2, 3], [3, 4]],[[0, 1, 2, 3, 4]])
obj=bpy.data.objects.new('ngon_colors',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
smooth=[False]
for i,face in enumerate(mesh.polygons):face.use_smooth=smooth[i]
color=mesh.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='CORNER')
rgba=[[0.0, 0.4000000059604645, 0.10000000149011612, 1.0], [0.20000000298023224, 0.4000000059604645, 0.10000000149011612, 1.0], [0.4000000059604645, 0.4000000059604645, 0.10000000149011612, 1.0], [0.6000000238418579, 0.4000000059604645, 0.10000000149011612, 1.0], [0.800000011920929, 0.4000000059604645, 0.10000000149011612, 1.0]]
for i,color_value in enumerate(color.data):color_value.color=rgba[i]
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=2
mod.use_creases=True
mod.use_limit_surface=True
mod.use_custom_normals=False
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('branched_wire')
mesh.from_pydata([[0.0, 0.0, 0.0], [1.0, 1.0, 0.0], [2.0, 0.0, 0.0], [1.0, 2.0, 0.0]],[[0, 1], [1, 2], [1, 3]],[])
obj=bpy.data.objects.new('branched_wire',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
smooth=[]
for i,face in enumerate(mesh.polygons):face.use_smooth=smooth[i]
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=2
mod.use_creases=True
mod.use_limit_surface=True
mod.use_custom_normals=False
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('wire_creases')
mesh.from_pydata([[0.0, 0.0, 0.0], [1.0, 1.0, 0.0], [2.0, 0.0, 0.0], [1.0, 2.0, 0.0]],[[0, 1], [1, 2], [1, 3]],[])
obj=bpy.data.objects.new('wire_creases',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
smooth=[]
for i,face in enumerate(mesh.polygons):face.use_smooth=smooth[i]
a=mesh.attributes.new(name='crease_edge',type='FLOAT',domain='EDGE')
weights=[0.0, 0.4000000059604645, 0.800000011920929]
for i,crease_value in enumerate(a.data):crease_value.value=weights[i]
a=mesh.attributes.new(name='crease_vert',type='FLOAT',domain='POINT')
weights=[0.0, 0.25, 0.5, 0.75]
for i,crease_value in enumerate(a.data):crease_value.value=weights[i]
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=2
mod.use_creases=True
mod.use_limit_surface=True
mod.use_custom_normals=False
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=bpy.data.meshes.new('surface_and_wire')
mesh.from_pydata([[0.0, 0.0, 0.0], [1.0, 1.0, 0.0], [2.0, 0.0, 0.0], [1.0, 2.0, 0.0], [4.0, 0.0, 0.0], [5.0, 0.0, 0.0], [5.0, 1.0, 0.0], [4.0, 1.0, 0.0]],[[0, 1], [1, 2], [1, 3], [4, 7], [4, 5], [5, 6], [6, 7]],[[4, 5, 6, 7]])
obj=bpy.data.objects.new('surface_and_wire',mesh)
bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
smooth=[False]
for i,face in enumerate(mesh.polygons):face.use_smooth=smooth[i]
mod=obj.modifiers.new('Subdivision','SUBSURF')
mod.levels=2
mod.use_creases=True
mod.use_limit_surface=True
mod.use_custom_normals=False
bpy.ops.object.modifier_apply(modifier=mod.name)
