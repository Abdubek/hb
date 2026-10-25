import bpy

scn = bpy.data.scenes['Scene']
ob = bpy.data.objects['Cube']

testgroup = bpy.data.groups.new('testgroup')
testgroup.objects.link(ob)
testgroup.objects.unlink(ob)

scn.objects.unlink(ob)

ob.user_clear()    #manually clears all users, frees the object to be removed

bpy.data.objects.remove(ob)
