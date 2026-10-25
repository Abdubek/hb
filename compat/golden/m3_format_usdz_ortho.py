import bpy
bpy.ops.object.camera_add(location=(1,2,3));camera=bpy.context.object;camera.data.type='ORTHO';camera.data.ortho_scale=6;camera.data.shift_x=.1;camera.data.shift_y=-.2
camera.data.clip_start=.2;camera.data.clip_end=300;bpy.context.scene.camera=camera
