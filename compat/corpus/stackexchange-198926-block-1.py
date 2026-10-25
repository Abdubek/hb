import bpy
from pathlib import Path
from bpy_extras.io_utils import ImportHelper 
from bpy.types import Operator, OperatorFileListElement
from bpy.props import CollectionProperty, StringProperty

class OT_TestOpenFilebrowser(Operator, ImportHelper): 
    bl_idname = "test.open_filebrowser" 
    bl_label = "Open the file browser" 
    directory : StringProperty(subtype='DIR_PATH')
    files : CollectionProperty(type=OperatorFileListElement)
    
    def execute(self, context): 
        
        """Do something with the selected file(s)."""
        base = Path(self.directory)                
        for f in self.files:
            print(base / f.name)

        return {'FINISHED'}
    
def register(): 
    bpy.utils.register_class(OT_TestOpenFilebrowser) 

def unregister(): 
    bpy.utils.unregister_class(OT_TestOpenFilebrowser) 
    
if __name__ == "__main__": 
    register()

    # test call 
    bpy.ops.test.open_filebrowser('INVOKE_DEFAULT')
