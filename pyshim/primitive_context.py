"""Headless construction cursor and single-object primitive edit context."""
_EDIT_OBJECT=None

class ConstructionCursor(Strict):
    _path='bpy.types.View3DCursor'
    def __init__(self):self._location=[0.,0.,0.];self._rotation=[0.,0.,0.]
    def _write(self,field,values):
        values=[f32(v) for v in values]
        if len(values)!=3 or not all(math.isfinite(v) for v in values):raise ValueError('Cursor requires three finite components')
        setattr(self,field,values)
    location=property(lambda self:VectorView(lambda:self._location,lambda v:self._write('_location',v),self._path+'.location'),lambda self,v:self._write('_location',v))
    rotation_euler=property(lambda self:EulerView(lambda:self._rotation,lambda v:self._write('_rotation',v),self._path+'.rotation_euler',lambda:'XYZ'),lambda self,v:self._write('_rotation',v))

_CONSTRUCTION_CURSOR=ConstructionCursor()
SceneContext.cursor=property(lambda self:_CONSTRUCTION_CURSOR)
def _edit_object():
    if _EDIT_OBJECT is None:return None
    try:
        obj=wrap('objects',_EDIT_OBJECT)
        return obj if obj._get()['linked'] else None
    except Exception:return None
Object.mode=property(lambda obj:'EDIT' if _edit_object()==obj else 'OBJECT')
bpy.context._values['mode']=Dynamic(lambda:'EDIT_MESH' if _edit_object() is not None else 'OBJECT')

def mode_set(*,mode='OBJECT',toggle=False):
    global _EDIT_OBJECT
    if toggle or mode not in ('OBJECT','EDIT'):raise UnsupportedError('bpy.ops.object.mode_set','Use OBJECT or EDIT without toggle')
    if mode=='OBJECT':_EDIT_OBJECT=None;return {'FINISHED'}
    obj=bpy.context.object
    if obj is None or obj.type!='MESH':raise RuntimeError('Edit mode requires an active mesh')
    if any(other!=obj for other in bpy.context.selected_objects):raise UnsupportedError('bpy.ops.object.mode_set','Only one selected mesh can enter edit mode')
    _EDIT_OBJECT=obj._id;return {'FINISHED'}
bpy.ops.object._values['mode_set']=mode_set

def editmode_toggle():
    return mode_set(mode='OBJECT' if _edit_object() is not None else 'EDIT')
bpy.ops.object._values['editmode_toggle']=editmode_toggle

def _append_primitive(target,source):
    old=target.data._get();new=source.data._get()
    offset=len(old['vertices']);old_loops=sum(map(len,old['faces']));new_loops=sum(map(len,new['faces']))
    if offset+len(new['vertices'])>100000 or len(old['faces'])+len(new['faces'])>100000:raise UnsupportedError('Primitive edit mode','Combined construction is limited to 100,000 vertices/faces')
    matrix=target.matrix_world.inverted() @ source.matrix_world
    old['vertices'] += [list(matrix @ Vector(p)) for p in new['vertices']]
    old['edges'] += [[v+offset for v in edge] for edge in new['edges']]
    old['faces'] += [[v+offset for v in face] for face in new['faces']]
    old['smooth'] += new['smooth'];old['material_indices'] += [0]*len(new['faces'])
    incoming=new['uv_layers'][new['active_uv']]['data'] if new['uv_layers'] else None
    if not old['uv_layers'] and incoming is not None:old['uv_layers']=[dict(name='UVMap',data=[[0.,0.]]*old_loops)];old['active_uv']=0
    for index,layer in enumerate(old['uv_layers']):layer['data'] += incoming if incoming is not None and index==old['active_uv'] else [[0.,0.]]*new_loops
    request('bmesh_publish',id=target.data._id,mesh=old)

def _construction_wrapper(kind,original):
    def operator(*args,**options):
        global _EDIT_OBJECT
        align=options.get('align','WORLD')
        if align not in ('WORLD','CURSOR'):raise UnsupportedError('bpy.ops.mesh.primitive_'+kind+'_add','Use WORLD or CURSOR alignment; viewport alignment is outside the headless contract')
        enter=bool(options.pop('enter_editmode',False)) if kind!='torus' else False
        options['align']='WORLD'
        if 'location' not in options:options['location']=tuple(_CONSTRUCTION_CURSOR.location)
        if 'rotation' not in options:options['rotation']=tuple(_CONSTRUCTION_CURSOR.rotation_euler) if align=='CURSOR' else (0.,0.,0.)
        target=_edit_object()
        if target is not None:
            mesh=target.data._get()
            if mesh['loop_normals'] or mesh['colors'] or any(mesh.get(k) is not None for k in ('shape_keys','crease_edge','crease_vert','face_strength','deform_weights')):raise UnsupportedError('Primitive edit mode','Edit construction supports ordinary mesh geometry, materials and UV layers')
            try:target.matrix_world.inverted()
            except ValueError:raise UnsupportedError('Primitive edit mode','The edit object transform must be nonsingular')
        construction_scale=None
        if kind not in ('cube','plane','circle','torus') and 'scale' in options:
            construction_scale=[f32(v) for v in options.pop('scale')]
            if len(construction_scale)!=3 or not all(math.isfinite(v) for v in construction_scale):raise ValueError('Scale requires three finite components')
            if kind in ('cone','cylinder') and options.get('calc_uvs',True) and any(v<0 for v in construction_scale):raise UnsupportedError('Primitive construction UVs','Reflected cone/cylinder UV construction is outside the verified subset; use calc_uvs=False')
        if kind=='circle' and max(0.,float(options.get('radius',1.)))==0 and options.get('calc_uvs',True):raise UnsupportedError('Circle radius','Zero-radius Blender UVs are non-finite; use calc_uvs=False')
        if kind=='cube' and max(0.,float(options.get('size',2.)))==0:options['size']=1.
        result=original(*args,**options)
        source=bpy.context.object
        if construction_scale is not None:
            mesh=source.data;record=mesh._get()
            mesh._set('vertices',[[f32(p[i]*construction_scale[i]) for i in range(3)] for p in record['vertices']])
            if kind in ('cone','cylinder') and construction_scale==[0.,0.,0.] and record['uv_layers']:
                uv=record['uv_layers'][0]['data'];start=0
                for face in record['faces']:
                    if len(face)!=4:
                        for corner in range(start,start+len(face)):uv[corner]=[.75,.25] if options.get('end_fill_type','NGON')!='NOTHING' else [.5,.5]
                    start+=len(face)
                mesh._set('uv_layers',record['uv_layers'])
        if target is not None:
            mesh=source.data
            try:_append_primitive(target,source)
            finally:
                bpy.data.objects.remove(source,do_unlink=True);bpy.data.meshes.remove(mesh)
                target.select_set(True);bpy.context.view_layer.objects.active=target
        elif enter:
            _EDIT_OBJECT=source._id
        return result
    return operator

for _primitive_kind in ('cube','plane','circle','cylinder','cone','uv_sphere','ico_sphere','torus'):
    _primitive_name='primitive_'+_primitive_kind+'_add'
    bpy.ops.mesh._values[_primitive_name]=_construction_wrapper(_primitive_kind,bpy.ops.mesh._values[_primitive_name])

def _object_mode_operation(name,operation):
    def call(*args,**kwargs):
        if _edit_object() is not None:raise UnsupportedError('bpy.ops.object.'+name,'Return to OBJECT mode before using object operations')
        return operation(*args,**kwargs)
    return call
for _name,_operation in list(bpy.ops.object._values.items()):
    if _name not in ('mode_set','editmode_toggle'):bpy.ops.object._values[_name]=_object_mode_operation(_name,_operation)
