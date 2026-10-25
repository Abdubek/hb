HB_EQUIVALENT_MESH_PREFIXES=('EditSpheres','Icosphere')
import bpy
bpy.context.scene.cursor.location=(2,-3,1);bpy.context.scene.cursor.rotation_euler=(.2,.3,.4)
bpy.ops.mesh.primitive_cube_add(size=.6,align='CURSOR',enter_editmode=True)
obj=bpy.context.object;obj.name='EditCubes'
assert obj.mode=='EDIT' and bpy.context.mode=='EDIT_MESH'
bpy.ops.mesh.primitive_plane_add(size=1,location=(3,-2,2))
bpy.ops.mesh.primitive_cube_add(size=.4,location=(1,-2,2),scale=(.7,1.3,2))
bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.mesh.primitive_cube_add(size=.4,location=(-3,1,1),rotation=(.2,.3,-.4));obj=bpy.context.object;obj.name='EditSpheres';obj.data.name='EditSpheres';obj.scale=(.7,1.2,1.5)
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=4,radius=.6,location=(-2,1,2),scale=(.5,1.3,2))
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.7,location=(-4,1,2))
bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=.7,depth=1.2,scale=(.5,1.3,2),location=(0,3,1));bpy.context.object.name='ScaledCylinder'
bpy.ops.mesh.primitive_cone_add(vertices=8,radius1=.7,radius2=.2,depth=1.2,scale=(.5,1.3,2),location=(2,3,1));bpy.context.object.name='ScaledCone'
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.7,scale=(-.5,1.3,2),location=(4,3,1));bpy.context.object.name='ReflectedIco'
assert bpy.context.mode=='OBJECT'
