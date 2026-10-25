import bpy

# Call the obj import operator and pass the absolute file path
bpy.ops.import_scene.obj(filepath="/user-home/Desktop/foo.obj")

# Get the context object, print the name and its reference
obj = bpy.context.object
print(obj.name, ":", obj)

# Get all imported objects and print their names
objs = bpy.context.selected_objects
print(", ".join(o.name for o in objs))
