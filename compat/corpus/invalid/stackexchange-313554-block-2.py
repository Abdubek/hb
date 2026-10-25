font_size = 28
txtForTest = "GJKLPgjklp!?"


import bpy, blf, gpu, gpu_extras.batch
from mathutils import Vector as Vec
from bpy import context as C, data as D


def DrawRect(pos1, pos2, col):
    gpu.state.blend_set('ALPHA')
    gpuShader.bind()
    gpuShader.uniform_float('color', col)
    vpos = (pos1[0],pos1[1]), (pos2[0],pos1[1]), (pos2[0],pos2[1]), (pos1[0],pos2[1])
    gpu_extras.batch.batch_for_shader(gpuShader, type='TRI_FAN', content={'pos':vpos}).draw(gpuShader)


def CallbackDraw():
    #Frame for centered text:
    pos1 = Vec((200,200))
    pos2 = Vec((430,260))
    DrawRect(pos1, pos2, (.75,.75,1,.15))
    col = (1,1,1,.5)
    DrawRect(pos1, (pos2.x, pos1.y+1), col)
    DrawRect(pos1, (pos1.x+1, pos2.y), col)
    DrawRect((pos2.x-1, pos1.y), pos2, col)
    DrawRect((pos1.x, pos2.y-1), pos2, col)
    #Visualisation:
    blf.size(fontId, font_size)
    dim = Vec(blf.dimensions(fontId, txtForTest))
    cen = (pos1+pos2)/2
    bou1 = cen-dim/2
    bou2 = cen+dim/2
    col = (1,1,1,.5)
    DrawRect((0, bou2.y), (1000, bou2.y+1), col)
    DrawRect((0, bou1.y), (1000, bou1.y+1), col)
    DrawRect((cen.x+dim.x/2, 0), (cen.x+dim.x/2+1, 1000), col)
    DrawRect((cen.x-dim.x/2, 0), (cen.x-dim.x/2+1, 1000), col)
    
    DrawRect((0, cen.y-.5), (1000, cen.y+.5), col)

    #Text:
    blf.position(fontId, cen.x-dim.x/2, cen.y-centering_offset, 0)
    blf.enable(fontId, blf.SHADOW)
    blf.shadow_offset(fontId, 1, -1)
    blf.shadow(fontId, 5, .1, .1, .1, 1)
    blf.color(fontId, .9, .9, 1, 1)
    blf.draw(fontId, txtForTest)


def get_text_centering_offset(txt, font_path, blf_height):
    temp_name = "Temporary datablock - delete it"
    
    font = D.fonts.load(filepath=font_path, check_existing=True)
    txt_curve = D.curves.new(name=temp_name, type='FONT')
    txt_curve.font = font
    txt_curve.body = txt
    
    ob = D.objects.new(name=temp_name, object_data=txt_curve)
#    C.collection.objects.link(ob)
    
    # left/right, front/rear, top/bottom
    # ^    ^      ^     ^     ^   ^
    # see numpad orthographic views for reference
    lfb, lft, lrt, lrb, rfb, rft, rrt, rrb = ob.bound_box

    top_in_2D = lrb[1]
    bottom_in_2D = lfb[1]
    
    D.objects.remove(ob)
    D.curves.remove(txt_curve)
    
    height = top_in_2D - bottom_in_2D
    ratio = blf_height / height
    
    return (top_in_2D + bottom_in_2D)/2 * ratio
    

# using main() helps to avoid bugs related to namespace pollution
def main():
    global fontId, gpuShader, centering_offset
    txt_for_measurement = txtForTest
    #txt_for_measurement = "Sp"  # recommended

    font_path = r"C:\Windows\Fonts\consola.TTF"
    fontId = blf.load(font_path)
    blf.size(fontId, 1000)  # big size for accuracy; don't go too crazy, e.g. 100k doesn't work
    blf_height = blf.dimensions(fontId, txtForTest)[1]
    blf_height /= 1000  # cancel out the temporary magnification

    centering_offset = get_text_centering_offset(
        txt=txtForTest,
        font_path=font_path,
        blf_height=blf_height
    )
    print(centering_offset)
    centering_offset *= font_size  # because 1000 was a constant value, not a multiplier
    
    gpuShader = gpu.shader.from_builtin('UNIFORM_COLOR')
    
    # for easy script changes:
    s3D = bpy.types.SpaceView3D
    try:
        s3D.draw_handler_remove(s3D.my_handler, 'WINDOW')
    except (AttributeError, ValueError):
        pass
    s3D.my_handler = s3D.draw_handler_add(CallbackDraw, (), 'WINDOW', 'POST_PIXEL')
    
    
main()
