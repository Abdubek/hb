"""ARRAY offset, seam, cyclic seam, cap and attribute references."""
import bpy,math

def make(name,vertices,faces):
    data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces)
    obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);return obj

def apply_array(obj):
    bpy.context.view_layer.objects.active=obj;obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier=obj.modifiers[0].name)

vertices=[(0,0,0),(1,0,0),(1,1,0),(0,1,0)];faces=[(0,1,2,3)]
obj=make('AffineArray',vertices,faces);obj.location=(2,3,4)
control=bpy.data.objects.new('AffineControl',None);bpy.context.collection.objects.link(control);control.location=(3,3,4);control.rotation_euler=(0,0,.5);control.scale=(.8,1.2,1)
mod=obj.modifiers.new('Array','ARRAY');mod.count=3;mod.use_object_offset=True;mod.offset_object=control;mod.relative_offset_displace=(.5,.25,0)
assert mod.offset_object==control
apply_array(obj);assert len(obj.data.vertices)==12 and len(obj.data.polygons)==3

obj=make('MergedArray',vertices,faces);mod=obj.modifiers.new('Array','ARRAY');mod.count=3;mod.use_merge_vertices=True;mod.merge_threshold=.001
apply_array(obj);assert len(obj.data.vertices)==8 and len(obj.data.polygons)==3

obj=make('CappedArray',vertices,faces)
start=make('StartCap',[(0,0,0),(1,0,0),(1,1,0)],[(0,1,2)])
end=make('EndCap',[(0,0,0),(1,0,0),(0,1,0)],[(0,1,2)])
start.location=(100,100,100);end.scale=(2,3,4)
material=bpy.data.materials.new('ArrayMaterial');cap_material=bpy.data.materials.new('CapMaterial');obj.data.materials.append(material);start.data.materials.append(cap_material)
mod=obj.modifiers.new('Array','ARRAY');mod.count=3;mod.start_cap=start;mod.end_cap=end;mod.use_merge_vertices=True;mod.merge_threshold=.001
assert mod.start_cap==start and mod.end_cap==end
apply_array(obj);assert len(obj.data.vertices)==10 and len(obj.data.polygons)==5
assert len(obj.data.materials)==1 and all(p.material_index==0 for p in obj.data.polygons)

obj=make('ReflectedArray',vertices,faces);control=bpy.data.objects.new('ReflectControl',None);bpy.context.collection.objects.link(control);control.scale=(-1,1,1)
mod=obj.modifiers.new('Array','ARRAY');mod.count=2;mod.use_relative_offset=False;mod.use_object_offset=True;mod.offset_object=control
apply_array(obj);assert len(obj.data.vertices)==8

obj=make('CoincidentArray',vertices,faces);mod=obj.modifiers.new('Array','ARRAY');mod.count=3;mod.use_relative_offset=False;mod.use_merge_vertices=True
apply_array(obj);assert len(obj.data.vertices)==4 and len(obj.data.polygons)==1

obj=make('ClosedArray',vertices,faces);control=bpy.data.objects.new('LoopControl',None);bpy.context.collection.objects.link(control);control.rotation_euler=(0,0,2*math.pi/3)
mod=obj.modifiers.new('Array','ARRAY');mod.count=4;mod.use_relative_offset=False;mod.use_object_offset=True;mod.offset_object=control;mod.use_merge_vertices=True;mod.use_merge_vertices_cap=True
apply_array(obj);assert len(obj.data.vertices)==10 and len(obj.data.polygons)==3

bpy.ops.mesh.primitive_plane_add(size=2);obj=bpy.context.object;obj.name='UVArray'
mod=obj.modifiers.new('Array','ARRAY');mod.count=3;mod.use_merge_vertices=True
apply_array(obj);assert len(obj.data.vertices)==8 and len(obj.data.uv_layers.active.data)==12
