import bpy

obj=bpy.data.objects['Cube']
modifier=obj.modifiers['Dynamic Paint']
canvas_surface=modifier.canvas_settings.canvas_surfaces['Surface']
point_cache=canvas_surface.point_cache

context={}
context['blend_data']=bpy.data
context['scene']=bpy.data.scenes['Scene']
context['active_object']=obj
context['point_cache']=point_cache

bpy.ops.ptcache.bake(context,bake=True)
