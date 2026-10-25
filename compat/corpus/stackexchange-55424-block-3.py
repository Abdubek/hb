import bpy
from bpy.props import StringProperty, CollectionProperty

class MyCollectionProperty(bpy.types.PropertyGroup):
    name = StringProperty(default="")


bpy.utils.register_class(MyCollectionProperty)
bpy.types.Scene.my_collection_prop = CollectionProperty(
        type=MyCollectionProperty)

scene = bpy.data.scenes[0]
for attr in dir(scene):
    prop = getattr(scene, attr, None)
    if isinstance(prop, bpy.types.bpy_prop_collection):
        if bpy.types.Scene.bl_rna.properties[attr].fixed_type == MyCollectionProperty.bl_rna:
            print(prop, "found")
