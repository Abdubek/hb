import bpy
from bpy.types import Menu, Operator, ShaderNodeMath
from bpy.props import EnumProperty
 
class AddMathNode(Operator):
    ''' Add Math Node '''
    bl_idname = "node.add_math"
    bl_label = "Add Math Node"
    items = [
        (p.identifier, p.name, p.description) 
        for p in ShaderNodeMath.bl_rna.properties["operation"].enum_items
            ]
    #print(items)
    operation : EnumProperty(
        items=items,
        name="Operation",
        default='ADD',
        )
            
    def execute(self, context):
        # the material in the node editor
        mat = context.material  
        # add a new math node to its nodes         
        n = mat.node_tree.nodes.new("ShaderNodeMath")
        # set some properties
        n.operation = self.operation
        n.name = self.operation.lower().title()
        # make active
        mat.node_tree.nodes.active = n
        return {'FINISHED'}
        #return bpy.ops.transform.translate('INVOKE_DEFAULT') # use translate   
      
classes = (AddMathNode,)
def draw_menu(self, context):
    layout = self.layout
    layout.operator_menu_enum("node.add_math", "operation")
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.NODE_MT_add.append(draw_menu)
 
def unregister():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.NODE_MT_add.remove(draw_menu)

 
if __name__ == "__main__":
    register()
