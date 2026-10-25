import bpy
context = bpy.context
obj = context.object

namelist = [("Bone", "Head")]

for name, newname in namelist:
    # get the pose bone with name
    pb = obj.pose.bones.get(name)
    # continue if no bone of that name
    if pb is None:
        continue
    # rename
    pb.name = newname
