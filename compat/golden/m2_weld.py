"""Distance-weld seam contracts, authored against Blender before implementation."""
HB_SYMBOLS={
'bpy.types.WeldModifier.name':'Modifier name', 'bpy.types.WeldModifier.type':'WELD',
'bpy.types.WeldModifier.show_viewport':'Viewport query and glTF export evaluation flag',
'bpy.types.WeldModifier.show_render':'CPU preview evaluation flag',
}
import bpy

def seam(name,gap):
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata([(0,0,0),(1,0,0),(1,1,0),(0,1,0),(1+gap,0,0),(2,0,0),(2,1,0),(1+gap,1,0)],[],[(0,1,2,3),(4,5,6,7)])
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active=obj;obj.select_set(True)
    for i in range(2):
        mat=bpy.data.materials.new(name+str(i));mat.diffuse_color=(.2+.4*i,.3,.5,1);mesh.materials.append(mat)
    for i,p in enumerate(mesh.polygons):p.material_index=i;p.use_smooth=bool(i)
    for layer_name in ('UV','Detail'):
        layer=mesh.uv_layers.new(name=layer_name)
        for i,loop in enumerate(layer.data):loop.uv=(i*.125,(i%3)*.25)
    return obj

for gap,threshold,expected in ((0,0,8),(0,.001,6),(.0005,.001,6),(.001,.001,8),(.0015,.001,8),(.125,.125,8),(.125,.126,6)):
    obj=seam('Weld',gap);mod=obj.modifiers.new('Weld','WELD')
    assert mod.type=='WELD' and mod.mode=='ALL'
    assert abs(mod.merge_threshold-.001)<1e-8
    assert not mod.loose_edges and mod.vertex_group=='' and not mod.invert_vertex_group
    mod.mode='ALL';mod.loose_edges=False;mod.vertex_group='';mod.invert_vertex_group=False
    mod.merge_threshold=threshold;mod.name='Seam repair'
    mod.show_viewport=False;mod.show_viewport=True;mod.show_render=False;mod.show_render=True
    bpy.ops.object.modifier_apply(modifier=mod.name)
    assert len(obj.data.vertices)==expected and len(obj.data.polygons)==2
    assert [p.material_index for p in obj.data.polygons]==[0,1]
    assert [p.use_smooth for p in obj.data.polygons]==[False,True]

# A strip's repeated face borders are welded before shell evaluation.
obj=seam('Stack',.0005)
array=obj.modifiers.new('Repeat','ARRAY');array.count=3
array.relative_offset_displace=(1,0,0)
mod=obj.modifiers.new('Weld','WELD');mod.merge_threshold=.001
shell=obj.modifiers.new('Shell','SOLIDIFY');shell.thickness=.15
assert len(obj.data.vertices)==8

# Three-way coincident seam clusters: six separately authored cube faces.
points=((-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1))
faces=((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7))
mesh=bpy.data.meshes.new('Cube seams')
mesh.from_pydata([points[j] for f in faces for j in f],[],[tuple(range(i*4,i*4+4)) for i in range(6)])
obj=bpy.data.objects.new('Cube seams',mesh);bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj;obj.select_set(True)
mod=obj.modifiers.new('Weld','WELD');bpy.ops.object.modifier_apply(modifier=mod.name)
assert len(mesh.vertices)==8 and len(mesh.polygons)==6

# Dense but unambiguous clusters average positions; no face collapses occur.
mesh=bpy.data.meshes.new('Cluster')
mesh.from_pydata([(0,0,0),(.1,0,0),(.15,0,0),(4,0,0),(4,2,0),(0,2,0)],[],[(0,3,4,5)])
obj=bpy.data.objects.new('Cluster',mesh);bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj;obj.select_set(True)
mod=obj.modifiers.new('Weld','WELD');mod.merge_threshold=.2;bpy.ops.object.modifier_apply(modifier=mod.name)
assert len(mesh.vertices)==4 and abs(mesh.vertices[0].co.x-1/12)<1e-5

# Non-destructive flags, object-local threshold, empty input and clamping.
obj=seam('Hidden viewport',.0005);obj.scale=(2,3,4)
mod=obj.modifiers.new('Weld','WELD');mod.show_viewport=False
obj=seam('Hidden render',.0005);mod=obj.modifiers.new('Weld','WELD');mod.show_render=False
mesh=bpy.data.meshes.new('Empty');obj=bpy.data.objects.new('Empty',mesh);bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
mod=obj.modifiers.new('Weld','WELD');mod.merge_threshold=-1;assert mod.merge_threshold==0
bpy.ops.object.modifier_apply(modifier=mod.name)

# Complete clusters up to the documented bound, also far from the origin.
for count in (2,3,4,8,16,64):
    for offset in (0,10000):
        mesh=bpy.data.meshes.new('Dense cluster')
        points=[(offset+.0001*i/(count-1),0,0) for i in range(count)]+[(offset+4,0,0),(offset+4,2,0),(offset,2,0)]
        mesh.from_pydata(points,[],[(0,count,count+1,count+2)])
        obj=bpy.data.objects.new('Dense cluster',mesh);bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
        mod=obj.modifiers.new('Weld','WELD');mod.merge_threshold=.01
        bpy.ops.object.modifier_apply(modifier=mod.name);assert len(mesh.vertices)==4

mesh=bpy.data.meshes.new('Weld wires');mesh.from_pydata([(0,0,0),(.1,0,0),(1,0,0),(1.1,0,0)],[(0,1),(0,2),(1,3),(2,3)],[])
obj=bpy.data.objects.new('Weld wires',mesh);bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
mod=obj.modifiers.new('Weld','WELD');mod.merge_threshold=.15;bpy.ops.object.modifier_apply(modifier=mod.name)
assert len(mesh.vertices)==2 and len(mesh.edges)==1
