import bpy
from mathutils import Matrix,Euler
for i,mode in enumerate(('XYZ','XZY','YXZ','YZX','ZXY','ZYX','QUATERNION')):
 bpy.ops.object.empty_add(location=(i*4,0,1));parent=bpy.context.object;parent.name='Parent_'+mode;parent.rotation_euler=(.2,-.4,.7);parent.scale=(1.2,.7,2)
 bpy.ops.mesh.primitive_cube_add(size=.5);obj=bpy.context.object;obj.name='World_'+mode;obj.rotation_mode=mode;obj.parent=parent
 target=Matrix.Translation((i*4,2,3)) @ Euler((.4,-.6,.9),'YZX').to_matrix().to_4x4() @ Matrix.Diagonal((-.6 if i%2 else .6,1.4,2,1))
 if i==2:target[0][1]+=.3
 obj.matrix_world=target
 bpy.context.view_layer.update()
 assert len(obj.matrix_world)==4
