"""Mesh joining contract, authored and run in Blender before implementation."""
import bpy
red=bpy.data.materials.new('Red');blue=bpy.data.materials.new('Blue')
parts=[]
for name,loc,rot,scale in [('Zulu',(4,0,0),(.1,.2,.3),(2,.7,1)),('Active',(1,2,3),(.2,.3,.4),(.8,1.3,2)),('Alpha',(0,3,0),(.3,.1,.2),(1,2,.8))]:
    bpy.ops.mesh.primitive_cube_add(location=loc,rotation=rot,calc_uvs=name!='Alpha')
    o=bpy.context.object;o.name=name;o.data.name=name+'Data';o.scale=scale
    o.data.materials.append(red if name!='Alpha' else blue)
    if name=='Active':o.data.materials.append(blue);o.data.polygons[1].material_index=1
    if name=='Alpha':o.data.uv_layers.new(name='Second');o.data.polygons[0].use_smooth=True
    parts.append(o)
bpy.ops.object.select_all(action='SELECT');a=parts[1];bpy.context.view_layer.objects.active=a
assert bpy.ops.object.join()=={'FINISHED'}
assert len(bpy.context.scene.objects)==1 and bpy.context.object==a
assert len(a.data.vertices)==24 and len(a.data.polygons)==18
assert len(a.data.uv_layers)==2 and len(a.data.materials)==2
assert len(bpy.data.meshes)==3
assert bpy.ops.object.join()=={'CANCELLED'}
# Empty source, loose edge, no source materials/UVs, and unselected object.
bpy.ops.mesh.primitive_cube_add(location=(-8,0,0));untouched=bpy.context.object
bpy.ops.object.select_all(action='DESELECT')
for name,verts,edges,faces in [('Loose',[(0,0,0),(1,0,0)],[(0,1)],[]),('Empty',[],[],[]),('Face',[(0,0,0),(1,0,0),(0,1,0)],[],[(0,1,2)])]:
    m=bpy.data.meshes.new(name);m.from_pydata(verts,edges,faces)
    o=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(o);o.select_set(True)
a.select_set(True);bpy.context.view_layer.objects.active=a
assert bpy.ops.object.join()=={'FINISHED'}
assert len(a.data.vertices)==29 and len(a.data.polygons)==19
assert len(a.data.edges)==40
assert untouched.name in bpy.context.scene.objects
# Join into an empty active mesh; source material order is stable and unused data remains.
bpy.ops.object.select_all(action='DESELECT')
m=bpy.data.meshes.new('Target');t=bpy.data.objects.new('Target',m);bpy.context.collection.objects.link(t);t.select_set(True)
bpy.ops.mesh.primitive_cube_add(calc_uvs=False);s=bpy.context.object;s.data.materials.append(blue)
t.select_set(True);bpy.context.view_layer.objects.active=t
assert bpy.ops.object.join()=={'FINISHED'}
assert len(t.data.vertices)==8 and len(t.data.materials)==1
# Two meshes without materials, and an active material duplicated in its slot list.
bpy.ops.mesh.primitive_cube_add(calc_uvs=False,location=(10,0,0));x=bpy.context.object
bpy.ops.mesh.primitive_cube_add(calc_uvs=False,location=(12,0,0));y=bpy.context.object
x.select_set(True);bpy.context.view_layer.objects.active=x
assert bpy.ops.object.join()=={'FINISHED'}
bpy.ops.mesh.primitive_cube_add(location=(14,0,0));d=bpy.context.object
d.data.materials.append(red);d.data.materials.append(red);d.data.polygons[0].material_index=1
bpy.ops.mesh.primitive_cube_add(location=(16,0,0));e=bpy.context.object;e.data.materials.append(red)
d.select_set(True);bpy.context.view_layer.objects.active=d
assert bpy.ops.object.join()=={'FINISHED'}
assert d.data.polygons[0].material_index==0

# First source supplies active UV when the target has no UV layers.
bpy.ops.object.select_all(action='DESELECT')
m=bpy.data.meshes.new('UVTarget');t=bpy.data.objects.new('UVTarget',m);bpy.context.collection.objects.link(t)
bpy.ops.mesh.primitive_cube_add();s=bpy.context.object
l=s.data.uv_layers.new(name='Detail',do_init=False);s.data.uv_layers.active=l
t.select_set(True);bpy.context.view_layer.objects.active=t
assert bpy.ops.object.join()=={'FINISHED'}
assert t.data.uv_layers.active.name=='Detail'
# Empty selected meshes cancel without removing either object.
bpy.ops.object.select_all(action='DESELECT')
empty_objects=[]
for i in range(2):
    mesh=bpy.data.meshes.new('EmptyOnly');obj=bpy.data.objects.new('EmptyOnly',mesh)
    bpy.context.collection.objects.link(obj);obj.select_set(True);empty_objects.append(obj)
bpy.context.view_layer.objects.active=empty_objects[0]
assert bpy.ops.object.join()=={'CANCELLED'}
assert len(bpy.context.selected_objects)==2

bpy.ops.mesh.primitive_cube_add()
for obj in empty_objects:obj.select_set(True)
assert bpy.ops.object.join()=={'CANCELLED'}
assert len(bpy.context.selected_objects)==3
