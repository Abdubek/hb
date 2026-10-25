"""MIRROR affine planes, bisection, UV offsets and vertex-group seams."""
import bpy

def make(name,vertices,faces):
    data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces)
    obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);return obj

def apply_first(obj):
    bpy.context.view_layer.objects.active=obj;obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier=obj.modifiers[0].name)

for flip in (False,True):
    obj=make('Bisect'+str(flip),[(-2,-1,0),(2,-1,0),(2,1,0),(-2,1,0)],[(0,1,2,3)])
    modifier=obj.modifiers.new('Mirror','MIRROR');modifier.use_bisect_axis[0]=True;modifier.use_bisect_flip_axis[0]=flip
    apply_first(obj);assert len(obj.data.vertices)==6 and len(obj.data.polygons)==2

obj=make('ObjectPlane',[(0,0,0),(1,0,0),(1,1,0),(0,1,0)],[(0,1,2,3)]);obj.location=(2,3,0);obj.scale=(2,1,1)
control=bpy.data.objects.new('MirrorPlane',None);bpy.context.collection.objects.link(control);control.location=(3,2,0);control.rotation_euler=(0,0,.4);control.scale=(.5,3,1)
modifier=obj.modifiers.new('Mirror','MIRROR');modifier.mirror_object=control;modifier.use_mirror_merge=False
assert modifier.mirror_object==control
apply_first(obj)

bpy.ops.mesh.primitive_plane_add(size=2,location=(1,0,0));obj=bpy.context.object;obj.name='MirrorUV'
modifier=obj.modifiers.new('Mirror','MIRROR');modifier.use_mirror_merge=False;modifier.use_mirror_u=True;modifier.use_mirror_v=True
modifier.offset_u=.2;modifier.offset_v=-.3;modifier.mirror_offset_u=.1;modifier.mirror_offset_v=.25
apply_first(obj);assert len(obj.data.uv_layers.active.data)==8

obj=make('MirrorGroups',[(0,0,0),(1,0,0),(1,1,0),(0,1,0)],[(0,1,2,3)])
left=obj.vertex_groups.new(name='Arm.L');right=obj.vertex_groups.new(name='Arm.R');center=obj.vertex_groups.new(name='Center')
left.add([0,1],.8,'REPLACE');right.add([0,3],.2,'REPLACE');center.add([0,1,2,3],.5,'REPLACE')
modifier=obj.modifiers.new('Mirror','MIRROR');assert modifier.use_mirror_vertex_groups
apply_first(obj);left=obj.vertex_groups['Arm.L'];right=obj.vertex_groups['Arm.R']
assert abs(left.weight(0)-.5)<1e-6 and abs(right.weight(0)-.5)<1e-6
assert [group.name for group in obj.vertex_groups]==['Arm.L','Arm.R','Center']

obj=make('NearBisect',[(-.0005,-1,0),(1,-1,0),(1,1,0),(-.0005,1,0)],[(0,1,2,3)])
modifier=obj.modifiers.new('Mirror','MIRROR');modifier.use_bisect_axis[0]=True;modifier.use_mirror_merge=False
apply_first(obj);assert obj.data.vertices[0].co.x==0

obj=make('ArrayWeights',[(0,0,0),(1,0,0),(1,1,0),(0,1,0)],[(0,1,2,3)])
group=obj.vertex_groups.new(name='Group');group.add([0,3],.2,'REPLACE');group.add([1,2],.8,'REPLACE')
modifier=obj.modifiers.new('Array','ARRAY');modifier.count=2;modifier.use_merge_vertices=True
apply_first(obj);group=obj.vertex_groups['Group']
assert len(obj.data.vertices)==6 and abs(group.weight(1)-.8)<1e-6
