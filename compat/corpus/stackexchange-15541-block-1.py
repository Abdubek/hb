import bpy

class FooOp(bpy.types.Operator):
    bl_idname = "development.fooop"
    bl_label = "Foo"

    @classmethod
    def poll(cls,context):
        return True

    def execute(self, context):
        return self.invoke(context, None)

    def invoke(self,context,event):
        self.report({'INFO'},"running FooOp!")
        return {'FINISHED'}

def make_foo(scene):
    bpy.ops.development.fooOp('EXEC_DEFAULT')


bpy.app.handlers.render_complete.append(make_foo)
bpy.utils.register_class(FooOp)
