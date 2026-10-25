import bpy

def set_active_panel_category(category, area_type):
    if bpy.app.version >= (4, 2, 0):
        areas = (area for win in bpy.context.window_manager.windows for area in win.screen.areas if area.type == area_type)
        for a in areas:
            for r in a.regions:
                if r.type == 'UI':
                    if r.width == 1:
                        with bpy.context.temp_override(area=a):
                            bpy.ops.wm.context_toggle(data_path='space_data.show_region_ui')
                    try:
                        if r.active_panel_category != category:
                            r.active_panel_category = category
                            r.tag_redraw()
                    except (NameError, AttributeError) as e:
                        raise e
                    
area_type = 'VIEW_3D'
category = 'View'

set_active_panel_category(category, area_type)
```
