import bpy

#default getter
def get_my_prop(self):
    return self['my_prop']

#omit the setter with a given getter to make it read-only
bpy.types.Object.my_prop = bpy.props.StringProperty(get=get_my_prop)

for obj in bpy.context.selected_objects:
    #assign the value directly
    obj['my_prop'] = "My Value"
