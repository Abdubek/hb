"""Evaluated USDZ mesh/material/camera/light reference scene."""
import bpy
HB_EQUIVALENT_MESH_PREFIXES=('Sphere',)
bpy.ops.mesh.primitive_cube_add(location=(1,2,3));cube=bpy.context.object;cube.name='USD_cube';cube.scale=(-2,1,1);cube.rotation_euler=(.2,.4,.6)
modifier=cube.modifiers.new('Copies','ARRAY');modifier.count=2
material=bpy.data.materials.new('USD_paint');material.use_nodes=True
shader=material.node_tree.nodes['Principled BSDF'];shader.inputs['Base Color'].default_value=(.2,.4,.6,1);shader.inputs['Metallic'].default_value=.3;shader.inputs['Roughness'].default_value=.25
cube.data.materials.append(material)
bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=4,radius=.3,location=(0,0,2));child=bpy.context.object;child.name='USD_child';child.parent=cube;child.data.materials.append(material)
bpy.ops.object.camera_add(location=(4,-6,5));camera=bpy.context.object;camera.name='USD_camera';bpy.context.scene.camera=camera
for kind in ('POINT','SPOT','SUN','AREA'):
    bpy.ops.object.light_add(type=kind,location=(2,-3,4));light=bpy.context.object;light.name='USD_'+kind;light.data.energy=100;light.data.color=(1,.5,.2)
    if kind=='AREA':light.data.shape='RECTANGLE';light.data.size=2;light.data.size_y=3
