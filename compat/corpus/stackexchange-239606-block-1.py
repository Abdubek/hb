import bpy
        
def msgbus_callback(*arg):
    # in console will be print selected_objects 
    print(bpy.context.selected_objects)
    # you can do something
        
def subscribe_to_obj(): 
             
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.LayerObjects, 'active'),
        owner=bpy,
        args=('something, if you need',),
        notify=msgbus_callback
        )
        
if __name__ == "__main__":
    subscribe_to_obj() 
