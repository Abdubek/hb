import bpy

class subcustomPropertiesGroup(bpy.types.PropertyGroup):
    customString : bpy.props.StringProperty()

bpy.utils.register_class(subcustomPropertiesGroup)

class customPropertiesGroup(bpy.types.PropertyGroup):
    subLists : bpy.props.CollectionProperty(type=subcustomPropertiesGroup)    

bpy.utils.register_class(customPropertiesGroup)

bpy.types.Scene.customLists = bpy.props.CollectionProperty(type=customPropertiesGroup)

newcustomList = bpy.context.scene.customLists.add()
newcustomList.name= "List 1"
newSubList = bpy.context.scene.customLists["List 1"].subLists.add()
newSubList.name = "Sub List 1"
newSubList.customString = "String 1"
