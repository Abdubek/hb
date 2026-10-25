"""Persistent modifier descriptors. Evaluation is owned by the Rust core."""
class Modifier(Strict):
    _path='bpy.types.Modifier'
    def __init__(self,owner,key):self._owner,self._key=owner,key
    def _index(self,stack):
        for i,m in enumerate(stack):
            if m['_key']==self._key:return i
        raise ReferenceError('Modifier has been removed')
    def _read(self,name):
        stack=self._owner._get().get('modifiers',[]);return stack[self._index(stack)][name]
    def _set(self,name,value):
        stack=self._owner._get().get('modifiers',[]);i=self._index(stack)
        if name=='name':value=_modifier_name(str(value),[m['name'] for j,m in enumerate(stack) if j!=i])
        stack[i][name]=value;request('modifier_stack',id=self._owner._id,value=stack)
    name=prop('name',str)
    show_viewport=prop('show_viewport',bool);show_render=prop('show_render',bool)
    @property
    def type(self):return self._read('type')

def fixed_prop(name,value):
    def set(self,new):
        if new!=value:raise UnsupportedError(self._path+'.'+name+'='+repr(new),'The supported value is '+repr(value))
        self._set(name,value)
    return property(lambda self:self._read(name),set)

def modifier_object_prop(name,mesh_only=False):
    def get(self):return wrap('objects',self._read(name))
    def set(self,value):
        if value is not None:
            if not isinstance(value,Object) or (mesh_only and value.type!='MESH'):raise TypeError('Expected a mesh object or None' if mesh_only else 'Expected an object or None')
            value._get()
        self._set(name,None if value is None else value._id)
    return property(get,set)

class ArrayModifier(Modifier):
    _path='bpy.types.ArrayModifier'
    count=prop('count',int,1,10000);fit_type=fixed_prop('fit_type','FIXED_COUNT')
    use_relative_offset=prop('use_relative_offset',bool);use_constant_offset=prop('use_constant_offset',bool)
    relative_offset_displace=vector_prop('relative_offset_displace',3);constant_offset_displace=vector_prop('constant_offset_displace',3)
    def _read(self,name):
        defaults={'offset_object':None,'start_cap':None,'end_cap':None,'merge_threshold':f32(.01),'use_merge_vertices_cap':False}
        if name in defaults:
            stack=self._owner._get().get('modifiers',[]);return stack[self._index(stack)].get(name,defaults[name])
        return super()._read(name)
    use_merge_vertices=prop('use_merge_vertices',bool);use_object_offset=prop('use_object_offset',bool)
    use_merge_vertices_cap=prop('use_merge_vertices_cap',bool);merge_threshold=prop('merge_threshold',float,0.,1.)
    offset_object=modifier_object_prop('offset_object')
    start_cap=modifier_object_prop('start_cap',True);end_cap=modifier_object_prop('end_cap',True)
class MirrorModifier(Modifier):
    _path='bpy.types.MirrorModifier'
    def _read(self,name):
        defaults={'mirror_object':None,'use_bisect_axis':[False]*3,'use_bisect_flip_axis':[False]*3,'bisect_threshold':f32(.001),'use_mirror_vertex_groups':True,'use_mirror_u':False,'use_mirror_v':False,'offset_u':0.,'offset_v':0.,'mirror_offset_u':0.,'mirror_offset_v':0.}
        if name in defaults:
            stack=self._owner._get().get('modifiers',[]);return stack[self._index(stack)].get(name,defaults[name])
        return super()._read(name)
    mirror_object=modifier_object_prop('mirror_object')
    use_mirror_vertex_groups=prop('use_mirror_vertex_groups',bool)
    use_mirror_u=prop('use_mirror_u',bool);use_mirror_v=prop('use_mirror_v',bool)
    offset_u=prop('offset_u',float,-1.,1.);offset_v=prop('offset_v',float,-1.,1.)
    mirror_offset_u=prop('mirror_offset_u',float,-1.,1.);mirror_offset_v=prop('mirror_offset_v',float,-1.,1.)
    bisect_threshold=prop('bisect_threshold',float,0.,1.)
    def _set_bisect(self,name,value):
        value=list(value)
        if len(value)!=3:raise ValueError('Expected three axis flags')
        self._set(name,[bool(v) for v in value])
    use_bisect_axis=property(lambda self:NumericView(lambda:self._read('use_bisect_axis'),lambda v:self._set_bisect('use_bisect_axis',v),self._path+'.use_bisect_axis'),lambda self,v:self._set_bisect('use_bisect_axis',v))
    use_bisect_flip_axis=property(lambda self:NumericView(lambda:self._read('use_bisect_flip_axis'),lambda v:self._set_bisect('use_bisect_flip_axis',v),self._path+'.use_bisect_flip_axis'),lambda self,v:self._set_bisect('use_bisect_flip_axis',v))
    use_mirror_merge=prop('use_mirror_merge',bool);use_clip=prop('use_clip',bool)
    merge_threshold=prop('merge_threshold',float,0.,1.)
    @property
    def use_axis(self):return NumericView(lambda:self._read('use_axis'),lambda v:self._set_axis(v),self._path+'.use_axis')
    @use_axis.setter
    def use_axis(self,value):self._set_axis(value)
    def _set_axis(self,value):
        value=list(value)
        if len(value)!=3:raise ValueError('Expected three axis flags')
        self._set('use_axis',[bool(v) for v in value])
class TriangulateModifier(Modifier):
    _path='bpy.types.TriangulateModifier'
    quad_method=prop('quad_method',str,choices=('BEAUTY','FIXED','FIXED_ALTERNATE','SHORTEST_DIAGONAL','LONGEST_DIAGONAL'))
    ngon_method=prop('ngon_method',str,choices=('BEAUTY','CLIP'))
    min_vertices=prop('min_vertices',int,4,2147483647)
    keep_custom_normals=prop('keep_custom_normals',bool)
class SolidifyModifier(Modifier):
    _path='bpy.types.SolidifyModifier'
    def _read(self,name):
        defaults={'vertex_group':'','shell_vertex_group':'','rim_vertex_group':'','invert_vertex_group':False,'thickness_vertex_group':0.}
        if name in defaults:
            stack=self._owner._get().get('modifiers',[]);return stack[self._index(stack)].get(name,defaults[name])
        return super()._read(name)
    solidify_mode=prop('solidify_mode',str,choices=('EXTRUDE','NON_MANIFOLD'))
    vertex_group=prop('vertex_group',str);shell_vertex_group=prop('shell_vertex_group',str);rim_vertex_group=prop('rim_vertex_group',str)
    invert_vertex_group=prop('invert_vertex_group',bool);thickness_vertex_group=prop('thickness_vertex_group',float,0.,1.)
    thickness=prop('thickness',float,-10000,10000);offset=prop('offset',float,-1,1)
    use_rim=prop('use_rim',bool);use_rim_only=prop('use_rim_only',bool)
    use_even_offset=prop('use_even_offset',bool);use_quality_normals=prop('use_quality_normals',bool)
    thickness_clamp=prop('thickness_clamp',float,0.,100.)
    material_offset=prop('material_offset',int,-32768,32767);material_offset_rim=prop('material_offset_rim',int,-32768,32767)

class BevelModifier(Modifier):
    _path='bpy.types.BevelModifier'
    width=prop('width',float,0.,1e6)
    @property
    def segments(self):return self._read('segments')
    @segments.setter
    def segments(self,value):
        value=max(1,int(value))
        if value>8:raise UnsupportedError(self._path+'.segments','Bevel supports 1..8 segments.')
        self._set('segments',value)
    affect=prop('affect',str,choices=('EDGES','VERTICES'));offset_type=fixed_prop('offset_type','OFFSET')
    limit_method=prop('limit_method',str,choices=('NONE','ANGLE'))
    angle_limit=prop('angle_limit',float,0.,math.pi)
    profile=fixed_prop('profile',.5);use_clamp_overlap=prop('use_clamp_overlap',bool)
    loop_slide=fixed_prop('loop_slide',True);harden_normals=fixed_prop('harden_normals',False)
    material=fixed_prop('material',-1)

class WeightedNormalModifier(Modifier):
    _path='bpy.types.WeightedNormalModifier'
    mode=prop('mode',str,choices=('FACE_AREA','CORNER_ANGLE','FACE_AREA_WITH_ANGLE'))
    weight=prop('weight',int,1,100)
    thresh=prop('thresh',float,0.,10.)
    keep_sharp=prop('keep_sharp',bool)
    use_face_influence=prop('use_face_influence',bool)
    vertex_group=prop('vertex_group',str);invert_vertex_group=prop('invert_vertex_group',bool)

class WeldModifier(Modifier):
    _path='bpy.types.WeldModifier'
    mode=prop('mode',str,choices=('ALL','CONNECTED'))
    merge_threshold=prop('merge_threshold',float,0.,3.4028234663852886e38)
    loose_edges=prop('loose_edges',bool)
    vertex_group=prop('vertex_group',str);invert_vertex_group=prop('invert_vertex_group',bool)

class DisplaceModifier(Modifier):
    _path='bpy.types.DisplaceModifier'
    strength=prop('strength',float,-3.4028234663852886e38,3.4028234663852886e38)
    mid_level=prop('mid_level',float,0.,1.)
    direction=prop('direction',str,choices=('NORMAL','X','Y','Z'))
    space=fixed_prop('space','LOCAL');texture_coords=fixed_prop('texture_coords','LOCAL')
    vertex_group=prop('vertex_group',str);invert_vertex_group=prop('invert_vertex_group',bool)
    @property
    def texture(self):return wrap('textures',self._read('texture'))
    @texture.setter
    def texture(self,value):
        if value is not None:
            if not isinstance(value,CloudsTexture):raise TypeError('Expected a CLOUDS texture or None')
            value._get()
        self._set('texture',None if value is None else value._id)

class SubsurfModifier(Modifier):
    _path='bpy.types.SubsurfModifier'
    def _read(self,name):
        if name=='use_custom_normals':
            stack=self._owner._get().get('modifiers',[]);return stack[self._index(stack)].get(name,False)
        return super()._read(name)
    use_custom_normals=prop('use_custom_normals',bool)
    subdivision_type=prop('subdivision_type',str,choices=('CATMULL_CLARK','SIMPLE'))
    def _set_level(self,name,value):
        value=max(0,int(value))
        if value>6:raise UnsupportedError(self._path+'.'+name,'Subdivision supports levels 0..6.')
        self._set(name,value)
    levels=property(lambda self:self._read('levels'),lambda self,v:self._set_level('levels',v))
    render_levels=property(lambda self:self._read('render_levels'),lambda self,v:self._set_level('render_levels',v))
    quality=fixed_prop('quality',3);uv_smooth=fixed_prop('uv_smooth','PRESERVE_BOUNDARIES')
    boundary_smooth=prop('boundary_smooth',str,choices=('ALL','PRESERVE_CORNERS'))
    use_limit_surface=prop('use_limit_surface',bool);use_creases=prop('use_creases',bool)
    show_only_control_edges=prop('show_only_control_edges',bool)

class BooleanModifier(Modifier):
    _path='bpy.types.BooleanModifier'
    def _read(self,name):
        if name=='collection':
            stack=self._owner._get().get('modifiers',[]);return stack[self._index(stack)].get(name)
        return Modifier._read(self,name)
    @property
    def collection(self):return wrap('collections',self._read('collection'))
    @collection.setter
    def collection(self,value):
        if value is not None:
            if not isinstance(value,Collection):raise TypeError('Expected a collection or None')
            value._get()
        self._set('collection',None if value is None else value._id)
    operation=prop('operation',str,choices=('DIFFERENCE','UNION','INTERSECT'))
    solver=prop('solver',str,choices=('EXACT','FAST','MANIFOLD'))
    operand_type=prop('operand_type',str,choices=('OBJECT','COLLECTION'));material_mode=fixed_prop('material_mode','INDEX')
    use_self=fixed_prop('use_self',False);use_hole_tolerant=fixed_prop('use_hole_tolerant',False)
    @property
    def double_threshold(self):return self._read('double_threshold')
    @double_threshold.setter
    def double_threshold(self,value):
        if f32(float(value))!=f32(1e-6):raise UnsupportedError(self._path+'.double_threshold','MANIFOLD uses the default value 1e-6.')
        self._set('double_threshold',f32(1e-6))
    @property
    def object(self):return wrap('objects',self._read('object'))
    @object.setter
    def object(self,value):
        if value is not None:
            if not isinstance(value,Object) or value.type!='MESH':raise TypeError('BOOLEAN operand must be a mesh object or None')
            value._get()
        self._set('object',value._id if value is not None else None)

MODIFIERS={'WEIGHTED_NORMAL':WeightedNormalModifier,'DISPLACE':DisplaceModifier,'SUBSURF':SubsurfModifier,'BOOLEAN':BooleanModifier,'WELD':WeldModifier,'BEVEL':BevelModifier,'ARRAY':ArrayModifier,'MIRROR':MirrorModifier,'TRIANGULATE':TriangulateModifier,'SOLIDIFY':SolidifyModifier}
DEFAULT_MODIFIERS={
'WEIGHTED_NORMAL':dict(mode='FACE_AREA',weight=50,thresh=f32(.01),keep_sharp=False,use_face_influence=False,vertex_group='',invert_vertex_group=False),
'DISPLACE':dict(texture=None,strength=1.,mid_level=.5,direction='NORMAL',space='LOCAL',texture_coords='LOCAL',vertex_group='',invert_vertex_group=False),
'SUBSURF':dict(subdivision_type='CATMULL_CLARK',levels=1,render_levels=2,quality=3,uv_smooth='PRESERVE_BOUNDARIES',boundary_smooth='ALL',use_limit_surface=True,use_creases=True,show_only_control_edges=True),
'BOOLEAN':dict(operation='DIFFERENCE',solver='EXACT',operand_type='OBJECT',material_mode='INDEX',use_self=False,use_hole_tolerant=False,double_threshold=f32(1e-6),object=None),
'WELD':dict(mode='ALL',merge_threshold=f32(.001),loose_edges=False,vertex_group='',invert_vertex_group=False),
'BEVEL':dict(width=f32(.1),segments=1,affect='EDGES',offset_type='OFFSET',limit_method='ANGLE',angle_limit=f32(math.pi/6),profile=.5,use_clamp_overlap=True,loop_slide=True,harden_normals=False,material=-1),
'ARRAY':dict(count=2,fit_type='FIXED_COUNT',use_relative_offset=True,relative_offset_displace=[1.,0.,0.],use_constant_offset=False,constant_offset_displace=[1.,0.,0.],use_merge_vertices=False,use_object_offset=False),
'MIRROR':dict(use_axis=[True,False,False],use_mirror_merge=True,merge_threshold=f32(.001),use_clip=False),
'TRIANGULATE':dict(quad_method='SHORTEST_DIAGONAL',ngon_method='BEAUTY',min_vertices=4,keep_custom_normals=False),
'SOLIDIFY':dict(solidify_mode='EXTRUDE',thickness=f32(.01),offset=-1.,use_rim=True,use_rim_only=False,use_even_offset=False,use_quality_normals=False,thickness_clamp=0.,material_offset=0,material_offset_rim=0),
}

def _modifier_name(name,names):
    name=(name or 'Array').split('\0')[0]
    while len(name.encode('utf-8'))>63:name=name[:-1]
    if name not in names:return name
    base=name.rsplit('.',1)[0] if name.rsplit('.',1)[-1].isdigit() else name
    i=1
    while f'{base}.{i:03}' in names:i+=1
    return f'{base}.{i:03}'
class Modifiers(Sequence):
    def __init__(self,owner):
        self._owner=owner
        super().__init__('bpy.types.Object.modifiers',lambda:[MODIFIERS[m['type']](owner,m['_key']) for m in owner._get().get('modifiers',[])])
    def new(self,name,type):
        if type not in MODIFIERS:raise UnsupportedError(self._path+'.new(type='+repr(type)+')','Supported modifiers: '+', '.join(MODIFIERS))
        if self._owner.type!='MESH':raise UnsupportedError(self._path+'.new','Modifiers require a mesh object.')
        stack=self._owner._get().get('modifiers',[])
        key=self._owner._get().get('modifier_next_id',0)
        value=dict(_key=key,name=_modifier_name(str(name),[m['name'] for m in stack]),type=type,show_viewport=True,show_render=True,**DEFAULT_MODIFIERS[type])
        request('modifier_stack',id=self._owner._id,value=stack+[value],next_id=key+1)
        return MODIFIERS[type](self._owner,key)
    def remove(self,modifier):
        if not isinstance(modifier,Modifier) or modifier._owner is not self._owner:raise TypeError('Expected a modifier from this object')
        stack=self._owner._get().get('modifiers',[]);stack.pop(modifier._index(stack));request('modifier_stack',id=self._owner._id,value=stack)
    def clear(self):request('modifier_stack',id=self._owner._id,value=[])
Object.modifiers=property(lambda self:Modifiers(self))

def modifier_apply(*,modifier):
    owner=bpy.context.object
    if owner is None or owner.type!='MESH':raise RuntimeError('modifier_apply requires an active mesh object')
    stack=owner._get().get('modifiers',[])
    if not stack or stack[0]['name']!=modifier:raise UnsupportedError('bpy.ops.object.modifier_apply','Apply the first modifier in stack order.')
    if owner.data.users!=1:raise UnsupportedError('bpy.ops.object.modifier_apply','Copy the mesh data before applying a modifier to a shared mesh.')
    request('modifier_apply',id=owner._id);return {'FINISHED'}
bpy.ops.object._values['modifier_apply']=modifier_apply


def _assembly_basis_parts(obj,parts,flags=(True,True,True)):
    location,quaternion,scale=parts
    field='rotation_quaternion' if obj.rotation_mode=='QUATERNION' else 'rotation_euler'
    rotation=quaternion if field=='rotation_quaternion' else _object_quaternion_euler(quaternion,obj.rotation_mode)
    if not flags[0]:location=obj.location
    if not flags[1]:rotation=obj.rotation_quaternion if field=='rotation_quaternion' else obj.rotation_euler
    if not flags[2]:scale=obj.scale
    request('object_basis',id=obj._id,location=list(location),scale=list(scale),rotation_field=field,rotation=list(rotation))

def transform_apply(*,location=True,rotation=True,scale=True,properties=True,isolate_users=False):
    if not (location or rotation or scale):return {'FINISHED'}
    objects=list(bpy.context.selected_objects);active=bpy.context.object;groups={};children={};flags=(bool(location),bool(rotation),bool(scale))
    for obj in objects:
        if obj.type!='MESH' or any(v==0 for v in obj.scale):raise UnsupportedError('bpy.ops.object.transform_apply','Select meshes with nonzero scale components')
        mesh=obj.data._get()
        if mesh.get('shape_keys') or obj._get().get('matrix') is not None:raise UnsupportedError('bpy.ops.object.transform_apply','Apply to TRS mesh objects before creating shape keys')
        if mesh['loop_normals'] and any(v<0 for v in obj.scale):raise UnsupportedError('bpy.ops.object.transform_apply','Reflected packed-normal transformation is outside the verified subset')
        groups.setdefault(obj.data._id,[]).append(obj)
        children[obj._id]=[(child,child.matrix_world.decompose()) for child in obj.children]
        if obj.children:
            try:obj.matrix_world.inverted()
            except ValueError:raise UnsupportedError('bpy.ops.object.transform_apply','Child compensation requires nonsingular world transforms')
    plans=[]
    for members in groups.values():
        first=active if active in members else members[0];mesh=first.data
        if mesh.users>len(members) and not isolate_users:raise UnsupportedError('bpy.ops.object.transform_apply','Select every mesh user or set isolate_users=True')
        if len(members)>1 and any(obj.parent is not None or obj.children for obj in members):raise UnsupportedError('bpy.ops.object.transform_apply','Shared selected users must be unparented and have no children')
        inverse=first.matrix_world.inverted() if len(members)>1 else None
        others=[(obj,(obj.matrix_world @ inverse).decompose()) for obj in members if obj!=first]
        plans.append((first,members,mesh.users>len(members),others))
    for first,members,copy_data,others in plans:
        if copy_data:
            mesh=first.data.copy()
            for obj in members:obj.data=mesh
        request('transform_apply',id=first._id,location=flags[0],rotation=flags[1],scale=flags[2])
        for obj,parts in others:_assembly_basis_parts(obj,parts,flags)
        for obj in members:
            if children[obj._id]:
                inverse=obj.matrix_world.inverted()
                for child,parts in children[obj._id]:
                    _assembly_basis_parts(child,parts)
                    child._set('matrix_parent_inverse',[inverse[i][j] for j in range(4) for i in range(4)])
    return {'FINISHED'}
bpy.ops.object._values['transform_apply']=transform_apply


def join():
    active=bpy.context.object
    if active is None or active.type!='MESH' or not active.select_get():
        raise RuntimeError('bpy.ops.object.join requires a selected active mesh object')
    objects=list(bpy.context.selected_objects)
    for obj in objects:
        if obj.type!='MESH' or len(obj.modifiers):raise UnsupportedError('bpy.ops.object.join','Select meshes and apply modifiers before joining')
        mesh=obj.data._get()
        if mesh['loop_normals'] or mesh['colors'] or any(mesh.get(k) is not None for k in ('deform_weights','crease_edge','crease_vert','face_strength','shape_keys')):
            raise UnsupportedError('bpy.ops.object.join','Join supports ordinary mesh geometry and UV layers')
        if mesh['materials'] and any(i>=len(mesh['materials']) for i in mesh['material_indices']):raise UnsupportedError('bpy.ops.object.join','Assign valid material slot indices before joining')
    try:active.matrix_world.inverted()
    except ValueError:raise UnsupportedError('bpy.ops.object.join','The active world transform must be nonsingular')
    parent=active.parent;parts=active.matrix_world.decompose() if parent in objects else None
    if parent not in objects and parent is not None:
        cursor=parent.parent
        while cursor is not None:
            if cursor in objects:raise UnsupportedError('bpy.ops.object.join','Joining an indirect active ancestor is outside the verified hierarchy subset')
            cursor=cursor.parent
    result=request('join',id=active._id)
    if result and parts is not None:_assembly_basis_parts(active,parts)
    return {'FINISHED'} if result else {'CANCELLED'}
bpy.ops.object._values['join']=join
