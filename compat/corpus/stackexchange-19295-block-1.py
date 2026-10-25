import bpy


class HelloWorldPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Hello World Panel"
    bl_idname = "OBJECT_PT_hello"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        sce = context.scene

        col = layout.column()
        col.prop(sce, "arma")
        col.prop(sce, "bone")

        col.prop_search(sce, "arma_name", bpy.data, "armatures")
        arma = bpy.data.armatures.get(sce.arma_name)
        if arma is not None:
            col.prop_search(sce, "bone_name", arma, "bones")

        col.prop_search(sce, "arma_name", sce, "arma_coll", icon='OBJECT_DATA')

def arma_items(self, context):
    obs = []
    for ob in context.scene.objects:
        if ob.type == 'ARMATURE':
            obs.append((ob.name, ob.name, ""))
    return obs

def arma_upd(self, context):
    self.arma_coll.clear()
    for ob in context.scene.objects:
        if ob.type == 'ARMATURE':
            item = self.arma_coll.add()
            item.name = ob.name

def bone_items(self, context):
    arma = context.scene.objects.get(self.arma)
    if arma is None:
        return
    return [(bone.name, bone.name, "") for bone in arma.data.bones]

def register():
    bpy.utils.register_class(HelloWorldPanel)
    bpy.types.Scene.arma = bpy.props.EnumProperty(items=arma_items, update=arma_upd)
    bpy.types.Scene.bone = bpy.props.EnumProperty(items=bone_items)
    bpy.types.Scene.arma_coll = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    bpy.types.Scene.arma_name = bpy.props.StringProperty()
    bpy.types.Scene.bone_name = bpy.props.StringProperty()


def unregister():
    bpy.utils.unregister_class(HelloWorldPanel)
    del bpy.types.Scene.arma
    del bpy.types.Scene.bone
    del bpy.types.Scene.arma_name
    del bpy.types.Scene.bone_name
    del bpy.types.Scene.arma_coll


if __name__ == "__main__":
    register()
