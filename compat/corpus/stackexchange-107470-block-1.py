import bpy

context = bpy.context
for area in bpy.context.screen.areas:
   if area.type == 'IMAGE_EDITOR':
       override = bpy.context.copy()
       override['space_data'] = area.spaces.active
       override['region'] = area.regions[-1]
       override['area'] = area
       bpy.ops.screen.screen_full_area(override, use_hide_panels=True)

       print(context.area, override['area'])
       print(context.screen, override['screen'])
       print(context.window, override['window'])
       override['screen'] = context.screen
       override["area"] = context.area
       bpy.ops.image.view_all(override, fit_view=True)
       break
