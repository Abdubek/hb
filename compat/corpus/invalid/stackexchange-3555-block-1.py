import bpy

frameStart = 1
frameEnd = 155
frameStep = 50
viewer_area = None
viewer_space = None

for area_search in bpy.context.screen.areas:
    if viewer_area == None and area_search.type == 'IMAGE_EDITOR':
        viewer_area = area_search
        break

if viewer_area == None:
    viewer_area = bpy.context.screen.areas[0]
    viewer_area.type = "IMAGE_EDITOR"

for space in viewer_area.spaces:
    if space.type == "IMAGE_EDITOR":
        viewer_space = space

path = 'H:\\Data\\_blender\\Fluid\\Video_Edit.mov'
img = bpy.data.images.load(path)
w = img.size[0]
h = img.size[1]
viewer_space.image = img

frame = 1
for frame in range(frameStart, frameEnd, frameStep):
    viewer_space.image_user.frame_offset = frame
    #switch back and forth to force refresh
    viewer_space.draw_channels = 'COLOR_ALPHA'
    viewer_space.draw_channels = 'COLOR'
    pixels = list(viewer_space.image.pixels)
    tmp = bpy.data.images.new(name="sample"+str(frame), width=w, height=h, alpha=False, float_buffer=False)
    tmp.pixels = pixels

img.user_clear()
bpy.data.images.remove(img)
