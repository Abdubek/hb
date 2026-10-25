"""Object creation operators, measured against Blender before API exposure."""
def _object_add(name,data,location,rotation):
    obj=bpy.data.objects.new(name,data)
    bpy.context.collection.objects.link(obj)
    obj.location=location;obj.rotation_euler=rotation
    select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
    return obj

def camera_add(*,enter_editmode=False,align='WORLD',location=(0.,0.,0.),rotation=(0.,0.,0.),scale=(0.,0.,0.)):
    _primitive_options('bpy.ops.object.camera_add',enter_editmode,align,location,rotation,scale)
    _object_add('Camera',bpy.data.cameras.new('Camera'),location,rotation)
    return {'FINISHED'}

def light_add(*,type='POINT',radius=1.,align='WORLD',location=(0.,0.,0.),rotation=(0.,0.,0.),scale=(0.,0.,0.)):
    _primitive_options('bpy.ops.object.light_add',False,align,location,rotation,scale)
    radius=_construction_float(radius)
    if type not in ('POINT','SUN','SPOT','AREA'):raise UnsupportedError('bpy.ops.object.light_add(type='+repr(type)+')')
    data=bpy.data.lights.new(type.title(),type=type)
    if type=='SUN':data.energy=1.
    if type=='AREA':data.size=data.size_y=max(0.,min(1e12,radius))
    _object_add(type.title(),data,location,rotation)
    return {'FINISHED'}

def empty_add(*,type='PLAIN_AXES',radius=1.,align='WORLD',location=(0.,0.,0.),rotation=(0.,0.,0.),scale=(0.,0.,0.)):
    _primitive_options('bpy.ops.object.empty_add',False,align,location,rotation,scale)
    radius=_construction_float(radius)
    if type not in ('PLAIN_AXES','ARROWS','SINGLE_ARROW','CIRCLE','CUBE','SPHERE','CONE'):raise UnsupportedError('bpy.ops.object.empty_add(type='+repr(type)+')','Image empties are not supported.')
    obj=_object_add('Empty',None,location,rotation)
    obj.empty_display_type=type;obj.empty_display_size=max(0.,min(1e12,radius))
    return {'FINISHED'}

bpy.ops.object._values.update(camera_add=camera_add,light_add=light_add,empty_add=empty_add)

def duplicate(*,linked=False,mode='TRANSLATION'):
    if mode!='TRANSLATION':raise UnsupportedError('bpy.ops.object.duplicate(mode='+repr(mode)+')','Use the default duplication mode; apply transforms through object properties.')
    originals=list(bpy.context.selected_objects);active=bpy.context.object
    if not originals:return {'CANCELLED'}
    copies={};data_copies={}
    select_all(action='DESELECT')
    for original in originals:
        copy=original.copy();copies[original._id]=copy
        data=original.data
        if data is not None and not linked:
            key=(data._kind,data._id)
            if key not in data_copies:data_copies[key]=wrap(data._kind,request('copy',kind=data._kind,id=data._id))
            copy.data=data_copies[key]
        for collection in original.users_collection:collection.objects.link(copy)
        copy.select_set(True)
    for original in originals:
        copy=copies[original._id];parent=original.parent
        if parent is not None and parent._id in copies:copy.parent=copies[parent._id]
        stack=copy._get().get('modifiers',[]);changed=False
        for modifier in stack:
            fields=('object',) if modifier['type']=='BOOLEAN' else ('offset_object','start_cap','end_cap') if modifier['type']=='ARRAY' else ('mirror_object',) if modifier['type']=='MIRROR' else ()
            for field in fields:
                if modifier.get(field) in copies:modifier[field]=copies[modifier[field]]._id;changed=True
        if changed:request('modifier_stack',id=copy._id,value=stack)
    if active is not None and active._id in copies:bpy.context.view_layer.objects.active=copies[active._id]
    return {'FINISHED'}

bpy.ops.object._values['duplicate']=duplicate

def _set_object_basis(obj,matrix):
    scale=Vector(Vector([matrix[i][j] for i in range(3)]).length for j in range(3))
    if matrix.to_3x3().determinant()<0:scale=-scale
    obj.location=matrix.translation
    if obj.rotation_mode=='QUATERNION':obj.rotation_quaternion=matrix.to_quaternion()
    else:obj.rotation_euler=matrix.to_quaternion().to_euler(obj.rotation_mode)
    obj.scale=scale

def parent_set(*,type='OBJECT',xmirror=False,keep_transform=False):
    if type!='OBJECT' or xmirror:raise UnsupportedError('bpy.ops.object.parent_set','Object parenting is supported; bone, vertex and mirrored rig parenting are outside this contract.')
    parent=bpy.context.object
    if parent is None:raise RuntimeError('bpy.ops.object.parent_set requires an active object')
    children=[o for o in bpy.context.selected_objects if o!=parent]
    for child in children:
        cursor=parent
        while cursor is not None:
            if cursor==child:raise RuntimeError('Cyclic parent relation')
            cursor=cursor.parent
    try:inverse=Matrix(request('world',id=parent._id)).inverted()
    except ValueError:raise UnsupportedError('bpy.ops.object.parent_set','The active parent must have a nonsingular world transform.')
    preserved={o._id:Matrix(request('world',id=o._id)) for o in children} if keep_transform else {}
    for child in children:
        if keep_transform:_set_object_basis(child,preserved[child._id])
        child.parent=parent
        child._set('matrix_parent_inverse',[inverse[i][j] for j in range(4) for i in range(4)])
    return {'FINISHED'}

bpy.ops.object._values['parent_set']=parent_set

def origin_set(*,type='ORIGIN_GEOMETRY',center='MEDIAN'):
    if type not in ('ORIGIN_GEOMETRY','GEOMETRY_ORIGIN') or center not in ('MEDIAN','BOUNDS'):
        raise UnsupportedError('bpy.ops.object.origin_set','Mesh geometry/origin relocation supports ORIGIN_GEOMETRY or GEOMETRY_ORIGIN with MEDIAN or BOUNDS centers.')
    objects=[obj for obj in bpy.context.selected_objects if obj.type=='MESH']
    centers={};shifted=set()
    if type=='ORIGIN_GEOMETRY':
        for obj in objects:
            if obj.children:
                try:Matrix(request('world',id=obj._id)).inverted()
                except ValueError:raise UnsupportedError('bpy.ops.object.origin_set','Parent compensation requires a nonsingular object transform.')
    for obj in objects:
        mesh=obj.data
        if mesh._id not in centers:
            vertices=mesh._get()['vertices']
            if not vertices:centers[mesh._id]=Vector((0,0,0))
            elif center=='MEDIAN':centers[mesh._id]=Vector(sum(v[i] for v in vertices)/len(vertices) for i in range(3))
            else:centers[mesh._id]=Vector((min(v[i] for v in vertices)+max(v[i] for v in vertices))*.5 for i in range(3))
    for obj in objects:
        mesh=obj.data;offset=centers[mesh._id]
        if mesh._id not in shifted:
            mesh._set('vertices',[[f32(v[i]-offset[i]) for i in range(3)] for v in mesh._get()['vertices']]);shifted.add(mesh._id)
        if type=='ORIGIN_GEOMETRY':
            children=[(child,Matrix(request('world',id=child._id))) for child in obj.children]
            rotation=obj.rotation_quaternion if obj.rotation_mode=='QUATERNION' else obj.rotation_euler
            delta=rotation.to_matrix() @ Vector(offset[i]*obj.scale[i] for i in range(3))
            obj.location=obj.location+delta
            if children:
                try:inverse=Matrix(request('world',id=obj._id)).inverted()
                except ValueError:raise UnsupportedError('bpy.ops.object.origin_set','Parent compensation requires a nonsingular object transform.')
                for child,world in children:
                    _set_object_basis(child,world)
                    child._set('matrix_parent_inverse',[inverse[i][j] for j in range(4) for i in range(4)])
    return {'FINISHED'}

bpy.ops.object._values['origin_set']=origin_set


def _object_quaternion_euler(quaternion,order):
    # Object RNA uses the raw, already decomposed quaternion matrix here.
    m=quaternion.to_matrix()._rows;i,j,k,parity=_ORDERS[order];cy=math.hypot(m[i][i],m[j][i])
    if cy>1e-6:angles=[math.atan2(m[k][j],m[k][k]),math.atan2(-m[k][i],cy),math.atan2(m[j][i],m[i][i])]
    else:angles=[math.atan2(-m[j][k],m[j][j]),math.atan2(-m[k][i],cy),0.]
    if parity:angles=[-v for v in angles]
    def wrap(v):return (v+math.pi)%(2*math.pi)-math.pi
    other=[wrap(angles[0]+math.pi),wrap(math.pi-angles[1]),wrap(angles[2]+math.pi)]
    if sum(map(abs,other))<sum(map(abs,angles)):angles=other
    values=[0.,0.,0.]
    for axis,value in zip((i,j,k),angles):values[axis]=value
    return Euler(values,order)

def _set_matrix_world(obj,value):
    matrix=Matrix(value)
    if len(matrix)!=4 or any(len(row)!=4 for row in matrix):raise ValueError('Object.matrix_world requires a 4x4 matrix')
    if not all(math.isfinite(x) and abs(x)<=1e6 for row in matrix for x in row):raise ValueError('Object.matrix_world entries must be finite and within 1e6')
    if tuple(matrix[3])!=(0.,0.,0.,1.):raise UnsupportedError('bpy.types.Object.matrix_world','Only affine matrices are supported')
    parent=obj.parent
    if parent is not None:
        inverse=obj._get().get('matrix_parent_inverse')
        parent_matrix=parent.matrix_world
        if inverse is not None:parent_matrix=parent_matrix @ Matrix([[inverse[j*4+i] for j in range(4)] for i in range(4)])
        try:matrix=parent_matrix.inverted() @ matrix
        except ValueError:raise UnsupportedError('bpy.types.Object.matrix_world','The effective parent transform must be nonsingular')
    location,quaternion,scale=matrix.decompose()
    field='rotation_quaternion' if obj.rotation_mode=='QUATERNION' else 'rotation_euler'
    rotation=quaternion if field=='rotation_quaternion' else _object_quaternion_euler(quaternion,obj.rotation_mode)
    request('object_basis',id=obj._id,location=list(location),scale=list(scale),rotation_field=field,rotation=list(rotation))

Object.matrix_world=property(lambda obj:Matrix(request('world',id=obj._id)),_set_matrix_world)
