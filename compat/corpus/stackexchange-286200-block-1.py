import bpy

# strokes = bpy.data.grease_pencils["Annotations"].layers['RulerData3D'].frames[0].strokes

def is_measure_tool_active():
    try:
        if 'builtin.measure' in bpy.context.workspace.tools: return True
        return False
    except: return False

def set_active_tool(tool_name):
    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
            override = bpy.context.copy()
            override["space_data"] = area.spaces[0]
            override["area"] = area
            bpy.ops.wm.tool_set_by_id(override, name=tool_name)
            break

def refresh():
    if is_measure_tool_active():
        set_active_tool("builtin.select_box")
        set_active_tool("builtin.measure")

def get_layers():
    try: return bpy.data.grease_pencils["Annotations"].layers
    except: return None

layers = get_layers()

if layers is not None and 'RulerData3D' in layers:
    layers.remove(layers['RulerData3D'])

    refresh()
