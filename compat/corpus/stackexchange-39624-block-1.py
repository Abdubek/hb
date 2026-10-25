import bpy

def callback(scene, prop):
    print("Property '%s' of %s updated to value %s" % (prop, scene.name, getattr(scene, prop)))

def create_update_func(prop):
    def update(self, context):
        callback(self, prop)
    return update

bpy.types.Scene.prop_a = bpy.props.BoolProperty(update=create_update_func("prop_a"))
bpy.types.Scene.prop_b = bpy.props.BoolProperty(update=create_update_func("prop_b"))
bpy.types.Scene.prop_c = bpy.props.BoolProperty(update=create_update_func("prop_c"))
