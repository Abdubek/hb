import bpy
name = _cfg['name']
assert bpy.data.objects.get(name) is None, 'Recipe name already exists; edit it or choose a new name'
curve = bpy.data.curves.new(name, 'FONT')
curve.font = bpy.data.fonts.load(_cfg['font'])
curve.body = _cfg['text']
curve.size = _cfg['size']
curve.extrude = _cfg['extrude']
curve.align_x = 'CENTER'
mat = bpy.data.materials.new(name + ' Surface')
mat.diffuse_color = (*_cfg['color'], 1)
mat.roughness = .35
curve.materials.append(mat)
obj = bpy.data.objects.new(name, curve)
bpy.context.collection.objects.link(obj)
obj.location = _cfg['location']
obj.rotation_euler = _cfg['rotation']
