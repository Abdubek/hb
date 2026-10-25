import bpy

class subcustomPropertiesGroup(bpy.types.PropertyGroup):
    customString = bpy.props.StringProperty()
bpy.utils.register_class(subcustomPropertiesGroup)

class customPropertiesGroup(bpy.types.PropertyGroup):
    subLists = bpy.props.CollectionProperty(type=subcustomPropertiesGroup)    
bpy.utils.register_class(customPropertiesGroup)

bpy.types.Scene.customLists = bpy.props.CollectionProperty(type=customPropertiesGroup)
bpy.types.Scene.subLists = bpy.props.CollectionProperty(type=subcustomPropertiesGroup)

bpy.context.scene.customLists.clear()
bpy.context.scene.subLists.clear()

bpy.context.scene.customLists.add().name = 'list1'
bpy.context.scene.customLists.add().name = 'list2'

newCustomItem = bpy.context.scene.customLists['list1'].subLists.add()
newCustomItem.customString = "test1"
newCustomItem = bpy.context.scene.customLists['list1'].subLists.add()
newCustomItem.customString = "test2"
newCustomItem = bpy.context.scene.customLists['list2'].subLists.add()
newCustomItem.customString = "test3"
newCustomItem = bpy.context.scene.customLists['list2'].subLists.add()
newCustomItem.customString = "test4"

print('_______________')
for customList in bpy.context.scene.customLists:

    print("List: "+customList.name)

    for subList in customList.subLists:

        print("Property: "+subList.customString)
