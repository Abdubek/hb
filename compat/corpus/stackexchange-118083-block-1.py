import bpy
from bpy.props import FloatProperty
from mathutils import Vector, Matrix, Quaternion, Euler
from math import degrees, radians

class HelloWorldPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Hello World Panel"
    bl_idname = "OBJECT_PT_hello"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout

        obj = context.object

        row = layout.row()
        row.label(text="Active object is: " + obj.name)
        row = layout.row()
        row.prop(obj, "name")

        row = layout.row()
        row.prop(obj, "rotate")

def get_rotation(self):
    return self.rotation_euler.to_matrix().to_euler('ZYX').z

def set_rotation(self, value):
    rot = self.rotation_euler.to_matrix().to_euler('ZYX')
    rot.z = value
    self.rotation_euler = rot.to_matrix().to_euler(self.rotation_mode)

def register():
    bpy.types.Object.rotate = FloatProperty(name="Rotation",
            description="Rotate object.",
            get=get_rotation,
            set=set_rotation,
            unit='ROTATION')

    bpy.utils.register_class(HelloWorldPanel)


def unregister():
    del bpy.types.Object.rotate
    bpy.utils.unregister_class(HelloWorldPanel)


if __name__ == "__main__":
    register()
