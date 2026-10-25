import bpy
from bpy.types import Menu
 
class Submenu(Menu):
    bl_label = 'Some Submenu'    
    def draw(self, context):
        layout = self.layout
        layout.label(text="Some Submenu")
        layout.separator()
        layout.operator("mesh.primitive_cube_add", text = "Some Submenu Operator", icon = "BLENDER")
        layout.operator("mesh.primitive_cube_add", text = "Some Submenu Operator", icon = "BLENDER")
        layout.operator("mesh.primitive_cube_add", text = "Some Submenu Operator", icon = "BLENDER")
        layout.operator("mesh.primitive_cube_add", text = "Some Submenu Operator", icon = "BLENDER")
 
class Pie_menu(Menu):
    bl_label = "Some Pie Menu"
    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator("wm.call_menu_pie", text = "Some Other Pie", icon = "RIGHTARROW_THIN").name="Pie_menu"
        pie.operator("mesh.primitive_cube_add", text = "Some Operator", icon = "BLENDER")
        pie.operator("mesh.primitive_cube_add", text = "Some Operator", icon = "BLENDER")
        pie.operator("mesh.primitive_cube_add", text = "Some Operator", icon = "BLENDER")
        pie.operator("mesh.primitive_cube_add", text = "Some Operator", icon = "BLENDER")
        pie.operator("mesh.primitive_cube_add", text = "Some Operator", icon = "BLENDER")
        pie.operator("mesh.primitive_cube_add", text = "Some Operator", icon = "BLENDER")
        pie.operator("mesh.primitive_cube_add", text = "Some Operator", icon = "BLENDER")
        pie.separator()
        pie.separator()
        other = pie.column()
        gap = other.column()
        gap.separator()
        gap.scale_y = 7
        other_menu = other.box().column()
        other_menu.scale_y=1.3
        other_menu.operator("mesh.primitive_cube_add", text = "Some Menu Operator",icon = "BLENDER")
        other_menu.operator("mesh.primitive_cube_add", text = "Some Menu Operator",icon = "BLENDER") 
        other_menu.menu('Submenu', icon='RIGHTARROW_THIN',  text='Some Submenu...')

 
def register():
    bpy.utils.register_class(Submenu)
    bpy.utils.register_class(Pie_menu)
 
def unregister():
    bpy.utils.unregister_class(Submenu)
    bpy.utils.unregister_class(Pie_menu)
 
if __name__ == "__main__":
    register()
 
    bpy.ops.wm.call_menu_pie(name="Pie_menu")
