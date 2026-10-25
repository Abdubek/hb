import bpy

#Bones and its parents
def BoneAndParents( bone ):
    yield bone
    while bone.parent:
        bone = bone.parent
        yield bone

arm = bpy.data.objects['Armature']

bpy.ops.object.mode_set(mode='OBJECT')

#Add a temporary empty
bpy.ops.object.add()
empty = bpy.context.scene.objects.active

bpy.context.scene.objects.active = arm

bpy.ops.object.mode_set(mode='POSE')

bone = arm.pose.bones['Bone.003']

#Add IK constraint and update
constraint = bone.constraints.new( 'IK' )
constraint.target = empty
bone.constraints.update()
bpy.context.scene.update() #Important: update the scene

#Get the bones and transformation due to the constraint
bones = [b for b in BoneAndParents( bone )]
transformations = [b.matrix.copy() for b in bones]

#Get rid of the temporary constraint and update
bone.constraints.remove( constraint )
bone.constraints.update()

#Assign transformation
for b, t in zip( bones, transformations ):
    b.matrix = t

#Remove temporary empty
bpy.ops.object.mode_set(mode='OBJECT')
bpy.context.scene.objects.active = empty
bpy.ops.object.delete()

#Back to pose
bpy.context.scene.objects.active = arm
bpy.ops.object.mode_set(mode='POSE')
