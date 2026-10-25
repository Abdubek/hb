import bpy,json

out={}
cases=[
 ('chain',[(0,0,0),(.09,0,0),(.18,0,0),(.27,0,0)],[(0,1),(1,2),(2,3)],[],.1),
 ('chain_no_edges',[(0,0,0),(.09,0,0),(.18,0,0),(.27,0,0)],[],[],.1),
 ('collapse_quad',[(0,0,0),(.05,0,0),(1,1,0),(0,1,0)],[],[(0,1,2,3)],.1),
 ('collapse_triangle',[(0,0,0),(.05,0,0),(1,1,0)],[],[(0,1,2)],.1),
 ('nonadjacent',[(0,0,0),(1,0,0),(.05,.01,0),(0,1,0)],[],[(0,1,2,3)],.1),
 ('duplicates',[(0,0,0),(1,0,0),(0,1,0),(.01,0,0),(1.01,0,0),(.01,1,0)],[],[(0,1,2),(3,4,5)],.1),
 ('exact',[(0,0,0),(0,0,0),(1,0,0)],[(0,1),(1,2)],[],0),
]
for base,vertices,edges,faces,distance in cases:
 for mode in ('ALL','CONNECTED'):
  for loose in (False,True):
   for grouped in (False,True):
    name=f'{base}_{mode}_{loose}_{grouped}'
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,edges,faces)
    layer=mesh.uv_layers.new(name='UVMap')
    for i,entry in enumerate(layer.data):entry.uv=(i*.13,i*.07)
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
    if grouped:
     group=obj.vertex_groups.new(name='Mask')
     for i in range(len(vertices)):group.add([i],[0,.2,1][i%3],'REPLACE')
    mod=obj.modifiers.new('Weld','WELD');mod.mode=mode;mod.merge_threshold=distance;mod.loose_edges=loose
    if grouped:mod.vertex_group='Mask'
    bpy.ops.object.modifier_apply(modifier=mod.name)
    mesh=obj.data
    obj.name=name
