import bpy
context = bpy.context

# name of collection
name = "Foo"

scene = context.scene

coll = bpy.data.collections.get(name)
# if it doesn't exist create it
if coll is None:
    coll = bpy.data.collections.new(name)
# if it is not linked to scene colleciton treelink it
if not scene.user_of_id(coll):
    context.collection.children.link(coll)
