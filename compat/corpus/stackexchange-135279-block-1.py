import bpy

class ObjectCopy(bpy.types.PropertyGroup):
    object: bpy.props.PointerProperty(type=bpy.types.Object)    

    def copy(self):
        self.object = self.id_data.copy()
        self.name = self.object.name
        return self.object

    def add(self, ob):
        self.object = ob
        self.name = ob.name
        return self.object

def register():
    bpy.utils.register_class(ObjectCopy)
    bpy.types.Object.copies = bpy.props.CollectionProperty(type=ObjectCopy)

def unregister():
    bpy.utils.unregister_class(ObjectCopy)
    del(bpy.types.Object.copies)
    
if __name__ == "__main__":
    register()
