import bpy
# import bgl
# import blf
import gpu
from gpu_extras.batch import batch_for_shader
from blf import color as blf_color
from blf import size as blf_size
from blf import draw as blf_draw
from blf import position as blf_position
from bgl import glEnable, GL_BLEND

shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
shader_bind = shader.bind
uniform_float = shader.uniform_float
Box_indices = ((0, 1, 2), (0, 2, 3))

class Box:
    __slots__ = 'L', 'R', 'B', 'T', 'batch', 'color'
    def __init__(self, L, R, B, T, color):
        self.L = L
        self.R = R
        self.B = B
        self.T = T
        self.color = color
    def update(self):
        self.batch = batch_for_shader(shader, 'TRIS', {"pos": (
            (self.L, self.B), (self.L, self.T),
            (self.R, self.T), (self.R, self.B))}, indices=Box_indices
        )
    def draw(self):
        shader_bind()
        uniform_float("color", self.color)
        self.batch.draw(shader)

    def inbox(self, event):
        x = event.mouse_region_x
        y = event.mouse_region_y
        return self.L <= x <= self.R and self.B <= y <= self.T

    def get_height(self):
        return self.T - self.B
    def get_width(self):
        return self.R - self.L

    def move(self, dx, dy):
        self.L += dx
        self.R += dx
        self.B += dy
        self.T += dy
        self.update()

class Blf:
    __slots__ = 'x', 'y', 'size', 'color', 'text'
    def __init__(self, x, y, size, color, text):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.text = text
    def draw(self):
        blf_color(0, *self.color)
        blf_size(0, self.size, 72)
        blf_position(0, self.x, self.y, 0)
        blf_draw(0, self.text)
    def move(self, dx, dy):
        self.x += dx
        self.y += dy

class ModalDrawOperator(bpy.types.Operator):
    bl_idname = "view3d.modal_operator"
    bl_label = "Test Operator"

    instance = None
    handle = None
    AREA = None

    @classmethod
    def DRAW(cls):
        if cls.instance is None:
            # open new file without close the operator
            print("you need debug here, tips: bpy.app.handlers")
            return

        if bpy.context.area != cls.AREA: return # draw in one viewport only

        ins = cls.instance
        boxes = ins.boxes
        glEnable(GL_BLEND)

        boxes["rim"].draw()
        boxes["main"].draw()
        boxes["title"].draw()
        boxes["close_button"].draw()
        for b in ins.blfs.values():
            b.draw()

    def fin(self):
        print("  fin")
        cls = self.__class__
        cls.AREA.spaces[0].__class__.draw_handler_remove(cls.handle, 'WINDOW')
        self.RETURN = {'CANCELLED'}
        cls = self.__class__
        cls.handle = None
        cls.instance = None
        cls.AREA = None
        try:
            bpy.context.area.tag_redraw()
        except:
            pass

    def modal(self, context, event):
        self.sub_modal(event)
        return self.RETURN

    def modal_inside(self, event):
        boxes = self.boxes
        if boxes["main"].inbox(event) is False:
            self.RETURN = {'PASS_THROUGH'}
            self.sub_modal = self.modal_outside
            return

        if event.type == 'ESC' and event.value == 'PRESS':
            self.fin()
            return

        if boxes["title"].inbox(event):
            if boxes["close_button"].inbox(event):
                if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
                    self.fin()
                return

            if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
                self.sub_modal = self.modal_move
                self.mou_x = event.mouse_region_x
                self.mou_y = event.mouse_region_y
            return

    def modal_outside(self, event):
        if self.boxes["main"].inbox(event):
            self.RETURN = {'RUNNING_MODAL'}
            self.sub_modal = self.modal_inside
            self.modal_inside(event)
            return
    def modal_move(self, event):
        bpy.context.area.tag_redraw()
        if event.value == 'RELEASE':
            self.sub_modal = self.modal_inside
            b = self.boxes["main"]
            dx = 0
            dy = 0
            if b.L < 0: dx = - b.L
            elif b.R > bpy.context.region.width: dx = bpy.context.region.width - b.R
            if b.T > bpy.context.region.height: dy = bpy.context.region.height - b.T
            elif b.B < 0: dy = - b.B

            for b in self.boxes.values():
                b.move(dx, dy)
            for b in self.blfs.values():
                b.move(dx, dy)
            return

        dx = event.mouse_region_x - self.mou_x
        dy = event.mouse_region_y - self.mou_y
        for b in self.boxes.values():
            b.move(dx, dy)
        for b in self.blfs.values():
            b.move(dx, dy)

        self.mou_x = event.mouse_region_x
        self.mou_y = event.mouse_region_y

    def invoke(self, context, event):
        # if context.area.type != 'VIEW_3D':  return {'CANCELLED'}

        cls = self.__class__
        if cls.handle is not None:  return {'CANCELLED'}

        cls.AREA = bpy.context.area
        cls.handle = cls.AREA.spaces[0].__class__.draw_handler_add(cls.DRAW, (), 'WINDOW', 'POST_PIXEL')
        cls.instance = self
        self.sub_modal = self.modal_inside
        self.RETURN = {'RUNNING_MODAL'}

        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()

        boxes = {}
        blfs = {}
        self.boxes = boxes
        self.blfs = blfs
        x = event.mouse_region_x
        y = event.mouse_region_y

        left = x - 200
        right = x + 200
        bottom = y - 100
        top = y + 100
        color = (0.3, 0.3, 0.3, 1.0)
        boxes["main"] = Box(left, right, bottom, top, color)
        boxes["rim"] = Box(left - 1, right + 1, bottom - 1, top + 1, (0.4, 0.4, 0.4, 1.0))
        boxes["title"] = Box(left, right, top - 35, top, (0.2, 0.2, 0.2, 1.0))
        R = right - 2
        T = top - 2
        B = boxes["title"].B + 2
        L = R - boxes["title"].get_height() + 4
        boxes["close_button"] = Box(L, R, B, T, (0.65, 0.2, 0.2, 1.0))
        blfs["title"] = Blf(left + 10, top - 26, 22, (0.8, 0.8, 0.8, 1.0), "Dialog")
        blfs["body"] = Blf(left + 20, top - 80, 40, (0.5, 0.8, 0.8, 1.0), "Hello")
        blfs["close_button"] = Blf(L + 6, B + 3, 33, (0.8, 0.8, 0.8, 1.0), "✕")

        for b in boxes.values():
            b.update()
        return {'RUNNING_MODAL'}

def register():
    bpy.utils.register_class(ModalDrawOperator)

def unregister():
    bpy.utils.unregister_class(ModalDrawOperator)

if __name__ == "__main__":
    register()
