import bpy
name = _cfg['name']
assert bpy.data.objects.get(name) is None, 'Recipe name already exists; edit it or choose a new name'
bpy.ops.mesh.primitive_cube_add(size=1, location=_cfg['location'])
obj = bpy.context.object
obj.name = name
obj.scale = _cfg['dimensions']
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
mat = bpy.data.materials.new(name + ' Surface')
mat.diffuse_color = (*_cfg['color'], 1)
mat.metallic = _cfg['metallic']
mat.roughness = _cfg['roughness']
obj.data.materials.append(mat)
if _cfg['bevel'] > 0:
    bevel = obj.modifiers.new('Edge highlights', 'BEVEL')
    bevel.width = _cfg['bevel']
    bevel.segments = _cfg['segments']
    bevel.limit_method = 'ANGLE'
    for face in obj.data.polygons:
        face.use_smooth = True
    normals = obj.modifiers.new('Broad face normals', 'WEIGHTED_NORMAL')
    normals.keep_sharp = True
