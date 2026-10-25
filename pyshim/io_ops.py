"""File operators use the native asset pipeline within the current transaction."""
def import_scene_gltf(*,filepath,merge_vertices=False):
    if merge_vertices:raise UnsupportedError('bpy.ops.import_scene.gltf(merge_vertices=True)','Import preserves the file vertex indexing; use merge_vertices=False.')
    _operation_warnings.extend(request('import_gltf',path=str(filepath)))
    return {'FINISHED'}

bpy.ops._values['import_scene']=Namespace('bpy.ops.import_scene',gltf=import_scene_gltf)

def export_scene_gltf(*,filepath,export_format='GLB',use_selection=False,export_apply=False,export_cameras=False,export_lights=False):
    if export_format not in ('GLB','GLTF_SEPARATE'):raise UnsupportedError('bpy.ops.export_scene.gltf(export_format='+repr(export_format)+')','Use GLB or GLTF_SEPARATE.')
    _operation_warnings.extend(request('export_gltf',path=str(filepath),format=export_format,selection=bool(use_selection),apply=bool(export_apply),cameras=bool(export_cameras),lights=bool(export_lights)))
    return {'FINISHED'}

bpy.ops._values['export_scene']=Namespace('bpy.ops.export_scene',gltf=export_scene_gltf)

def _axis_import_matrix(forward,up):
    def axis(name):
        if name not in ('X','Y','Z','-X','-Y','-Z'):raise ValueError('Expected a signed X/Y/Z axis')
        return Vector([( -1 if name.startswith('-') else 1) if c==name[-1] else 0 for c in 'XYZ'])
    f,u=axis(forward),axis(up)
    if f.dot(u):raise ValueError('Forward and up axes must differ')
    return Matrix((f.cross(u),f,u)).to_4x4()

def import_scene_obj(*,filepath,axis_forward='-Z',axis_up='Y'):
    matrix=_axis_import_matrix(axis_forward,axis_up)
    _operation_warnings.extend(request('import_obj',path=str(filepath),matrix=[matrix[i][j] for j in range(4) for i in range(4)]))
    return {'FINISHED'}

bpy.ops.import_scene._values['obj']=import_scene_obj

def export_scene_obj(*,filepath,use_selection=False,use_mesh_modifiers=True,use_normals=True,use_uvs=True,use_materials=True,use_triangles=False,axis_forward='-Z',axis_up='Y',global_scale=1.):
    scale=float(global_scale)
    if not math.isfinite(scale) or scale<=0:raise ValueError('global_scale must be finite and positive')
    matrix=_axis_import_matrix(axis_forward,axis_up).inverted()
    for i in range(3):
        for j in range(3):matrix[i][j]*=scale
    _operation_warnings.extend(request('export_obj',path=str(filepath),selection=bool(use_selection),apply=bool(use_mesh_modifiers),normals=bool(use_normals),uvs=bool(use_uvs),materials=bool(use_materials),triangles=bool(use_triangles),matrix=[matrix[i][j] for j in range(4) for i in range(4)]))
    return {'FINISHED'}

bpy.ops.export_scene._values['obj']=export_scene_obj

def render_render(*,animation=False,write_still=False,use_viewport=False,layer='',scene=''):
    if animation or use_viewport or layer or scene:raise UnsupportedError('bpy.ops.render.render','Render the current scene camera with animation=False and use_viewport=False; named scene/layer overrides are unavailable.')
    _operation_warnings.extend(request('render_operator',write_still=bool(write_still)))
    return {'FINISHED'}

bpy.ops._values['render']=Namespace('bpy.ops.render',render=render_render)
