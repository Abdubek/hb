import bpy
orders=('XYZ','XZY','YXZ','YZX','ZXY','ZYX')
for index,order in enumerate(orders):
 bpy.ops.mesh.primitive_cube_add(size=1,location=(index*3,0,0))
 obj=bpy.context.object;obj.name='Euler_'+order
 obj.rotation_mode=order;obj.rotation_euler=(.3,.7,-1.1);obj.scale=(-.5,1.2,2)
 assert obj.rotation_euler.order==order
 bpy.ops.mesh.primitive_cube_add(size=.6,location=(index*3,3,0))
 obj=bpy.context.object;obj.name='FromQuaternion_'+order
 obj.rotation_mode='QUATERNION';obj.rotation_quaternion=(.7,.2,-.4,.5);obj.rotation_mode=order
 bpy.ops.mesh.primitive_cube_add(size=.6,location=(index*3,6,0))
 obj=bpy.context.object;obj.name='ToQuaternion_'+order
 obj.rotation_mode=order;obj.rotation_euler=(.3,.7,-1.1);obj.rotation_mode='QUATERNION'
 assert obj.rotation_euler.order=='XYZ'
