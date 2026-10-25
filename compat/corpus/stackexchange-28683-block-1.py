import bpy
import random

class ModalTimerOperator(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "wm.modal_timer_operator"
    bl_label = "Modal Timer Operator"

    limits : bpy.props.IntProperty(default=0) #not 'limits ='
    _timer = None

    def modal(self, context, event):
        if event.type in {'RIGHTMOUSE', 'ESC'} or self.limits > 30:
            self.limits = 0
            self.cancel(context)
            return {'FINISHED'}

        if event.type == 'TIMER':
            XYZcoord = (random.random()*100, random.random()*100, random.random()*100)
            bpy.ops.mesh.primitive_uv_sphere_add(location=XYZcoord)
            self.limits += 1

        return {'PASS_THROUGH'}

    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(time_step=0.1, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)


def register():
    bpy.utils.register_class(ModalTimerOperator)


def unregister():
    bpy.utils.unregister_class(ModalTimerOperator)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.wm.modal_timer_operator()
