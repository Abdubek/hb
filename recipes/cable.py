import bpy
name = _cfg['name']
assert bpy.data.objects.get(name) is None, 'Recipe name already exists; edit it or choose a new name'
curve = bpy.data.curves.new(name, 'CURVE')
curve.dimensions = '3D'
curve.bevel_depth = _cfg['radius']
curve.bevel_resolution = _cfg['profile_resolution']
curve.resolution_u = _cfg['resolution']
curve.use_fill_caps = True
spline = curve.splines.new('BEZIER')
spline.bezier_points.add(len(_cfg['points']) - 1)
for point, co in zip(spline.bezier_points, _cfg['points']):
    point.co = co
    point.handle_left_type = 'AUTO'
    point.handle_right_type = 'AUTO'
mat = bpy.data.materials.new(name + ' Rubber')
mat.diffuse_color = (*_cfg['color'], 1)
mat.roughness = .55
curve.materials.append(mat)
obj = bpy.data.objects.new(name, curve)
bpy.context.collection.objects.link(obj)
