import ast
import json
import struct
import sys
import types
import _hb

class UnsupportedError(Exception):
    def __init__(self,path,reason='This path is outside the tested hb modeling subset.'):
        self.path,self.reason=path,reason
        self.suggestion='Inspect hb api '+path.split('(')[0].split('=')[0]+' for tested paths and parameter limits; use hb capabilities for supported alternatives.'
        if 'World' in path or 'worlds' in path:
            self.suggestion='Use World.color or one Background with color/strength and an equirectangular Environment Texture. Other World nodes are outside the manifest.'
        elif 'matrix_world' in path:
            self.suggestion='Assign a finite affine 4x4 matrix with a nonsingular effective parent transform; use hb api bpy.types.Object.matrix_world for the bounded contract.'
        elif path.startswith(('bpy.ops.import_', 'bpy.ops.export_', 'bpy.ops.render')):
            self.suggestion='Inspect hb api for the supported bpy operator parameters, or use hb import, hb export and hb render for the documented asset/preview subset.'
        elif 'Bevel' in path or 'BEVEL' in path:
            self.suggestion='BEVEL supports canonical cuboids, EDGES/VERTICES, OFFSET, profile 0.5 and 1..8 segments; inspect width/clamping and textured-segment limits in hb api bpy.types.BevelModifier.'
        elif 'bmesh' in path:
            self.suggestion='Inspect hb api bmesh.ops and bmesh.types.BMesh for the supported operators and bounded UV/color/shape layers. Unlisted topology interpolation and edit lifecycle are unavailable.'
        self.doc='docs/compatibility.md#unsupported'
        super().__init__(path+': '+reason)

def request(op,**kwargs):
    if op in ('export_gltf','export_obj','render_operator','dimensions','set_dimensions','snapshot','copy') and _CURVE_DIRTY:_evaluate_curves()
    response=json.loads(_hb.request(json.dumps(dict(op=op,**kwargs),allow_nan=False)))
    if 'error' in response:raise RuntimeError(response['error'])
    return response['result']

def f32(v):return struct.unpack('f',struct.pack('f',float(v)))[0]
class Strict:
    def __getattr__(self,name):raise UnsupportedError(self._path+'.'+name)
    def __setattr__(self,name,value):
        if name.startswith('_'):object.__setattr__(self,name,value)
        elif isinstance(getattr(type(self),name,None),property) and getattr(type(self),name).fset:object.__setattr__(self,name,value)
        else:raise UnsupportedError(self._path+'.'+name)
class Namespace(Strict):
    def __init__(self,path,**values):self._path,self._values=path,values
    def __getattr__(self,name):
        if name in self._values:
            v=self._values[name]
            return v() if isinstance(v,Dynamic) else v
        return super().__getattr__(name)
class Dynamic:
    def __init__(self,fn):self.fn=fn
    def __call__(self):return self.fn()
class NumericView(Strict):
    def __init__(self,get,set,path):self._get,self._set,self._path=get,set,path
    def __len__(self):return len(self._get())
    def __iter__(self):return iter(self._get())
    def __getitem__(self,key):return tuple(self._get())[key]
    def __setitem__(self,key,value):
        v=self._get();v[key]=value
        self._set(v)
    def __repr__(self):return repr(tuple(self))
    def __add__(self,other):raise UnsupportedError(self._path+'.arithmetic','This numeric RNA view is not a Vector; use component assignment. Use an explicit mathutils.Color, Euler or Vector for standalone arithmetic.')
    __sub__=__mul__=__truediv__=__matmul__=__add__
    x=property(lambda s:s[0],lambda s,v:s.__setitem__(0,v))
    y=property(lambda s:s[1],lambda s,v:s.__setitem__(1,v))
    z=property(lambda s:s[2],lambda s,v:s.__setitem__(2,v))

VectorView=NumericView

def prop(name,cast=None,minimum=None,maximum=None,choices=None):
    def get(self):
        v=self._read(name)
        return f32(v) if cast is float else v
    def set(self,value):
        if choices and value not in choices:raise UnsupportedError(self._path+'.'+name+'='+repr(value),'Supported values: '+', '.join(choices))
        if cast is not None:value=cast(value)
        if minimum is not None:value=max(minimum,value)
        if maximum is not None:value=min(maximum,value)
        if cast is float:value=f32(value)
        self._set(name,value)
    return property(get,set)
def vector_prop(name,n,clamp=False):
    def set(self,value):
        v=list(value)
        if len(v)!=n:raise ValueError('Expected a sequence of length '+str(n))
        v=[f32(max(0,min(1,x)) if clamp else x) for x in v]
        self._set(name,v)
    return property(lambda self:(VectorView if name in ('location','scale') else NumericView)(lambda:self._read(name),lambda v:set(self,v),self._path+'.'+name),set)
_cache={}
def wrap(kind,key):
    if key is None:return None
    k=(kind,key)
    if k not in _cache:
        cls=Curve if kind=='meshes' and request('get',kind=kind,id=key).get('curve') is not None else CLASSES[kind]
        if cls is Curve and request('read',kind=kind,id=key,path=['curve','type'])=='FONT':cls=TextCurve
        _cache[k]=cls(key)
    return _cache[k]
def ref(obj):return None if obj is None else dict(kind=obj._kind,id=obj._id)
class DataBlock(Strict):
    def __init__(self,key):self._id=key
    def _get(self):return request('get',kind=self._kind,id=self._id)
    def _read(self,field):return request('read',kind=self._kind,id=self._id,path=[field])
    def _set(self,field,value):request('set',kind=self._kind,id=self._id,field=field,value=value)
    name=prop('name',str)
    @property
    def users(self):return self._get()['users']
    def copy(self):
        if self._kind not in ('meshes','objects','worlds'):raise UnsupportedError(self._path+'.copy')
        return wrap(self._kind,request('copy',kind=self._kind,id=self._id))
class Object(DataBlock):
    _kind='objects';_path='bpy.types.Object'
    location=vector_prop('location',3);rotation_euler=vector_prop('rotation_euler',3);scale=vector_prop('scale',3)
    hide_render=prop('hide_render',bool)
    empty_display_size=prop('empty_display_size',float,.0001,1000.)
    empty_display_type=prop('empty_display_type',str,choices=('PLAIN_AXES','ARROWS','SINGLE_ARROW','CIRCLE','CUBE','SPHERE','CONE'))
    def _set_dimensions(self,value):
        value=[f32(v) for v in value]
        if len(value)!=3:raise ValueError('Expected three dimensions')
        request('set_dimensions',id=self._id,value=value)
    dimensions=property(lambda self:VectorView(lambda:request('dimensions',id=self._id),self._set_dimensions,self._path+'.dimensions'),_set_dimensions)
    @property
    def rotation_mode(self):return self._get().get('rotation_mode','XYZ')
    @rotation_mode.setter
    def rotation_mode(self,v):
        if v not in (*_ORDERS,'QUATERNION'):raise UnsupportedError(self._path+'.rotation_mode='+repr(v),'Use one of six Euler orders or QUATERNION rotation.')
        if v==self.rotation_mode:return
        if v=='QUATERNION':self.rotation_quaternion=self.rotation_euler.to_quaternion()
        elif self.rotation_mode=='QUATERNION':
            self.rotation_quaternion.normalize();self.rotation_euler=self.rotation_quaternion.to_euler(v)
        self._set('rotation_mode',v)
    @property
    def rotation_quaternion(self):return QuaternionView(lambda:self._get().get('rotation_quaternion',[1,0,0,0]),lambda value:self._set('rotation_quaternion',value))
    @rotation_quaternion.setter
    def rotation_quaternion(self,value):
        value=list(value)
        if len(value)!=4:raise ValueError('Expected four quaternion components')
        self._set('rotation_quaternion',[f32(x) for x in value])
    @property
    def type(self):return self._get()['type']
    @property
    def data(self):
        d=self._read('data');return wrap(d['kind'],d['id']) if d else None
    @data.setter
    def data(self,value):
        if value is not None and not isinstance(value,(Mesh,Curve,Camera,Light)):raise TypeError('Expected mesh, camera, light or None')
        self._set('data',ref(value))
    @property
    def parent(self):return wrap('objects',self._read('parent'))
    @parent.setter
    def parent(self,value):
        if value is not None and not isinstance(value,Object):raise TypeError('Expected Object or None')
        self._set('parent',None if value is None else value._id)
    @property
    def children(self):return tuple(wrap('objects',k) for k in self._get()['children'])
    @property
    def users_collection(self):return tuple(wrap('collections',k) for k in self._get()['users_collection'])
    def select_get(self,*,view_layer=None):
        if view_layer is not None:raise UnsupportedError(self._path+'.select_get(view_layer=...)')
        return self._read('selected') if self._get()['linked'] else False
    def select_set(self,state,*,view_layer=None):
        if view_layer is not None:raise UnsupportedError(self._path+'.select_set(view_layer=...)')
        self._set('selected',bool(state))
class Sequence(Strict):
    def __init__(self,path,values):self._path,self._values=path,values
    def __iter__(self):return iter(self._values())
    def __len__(self):return len(self._values())
    def __getitem__(self,key):
        values=self._values()
        if isinstance(key,(int,slice)):return values[key]
        if not isinstance(key,str):raise TypeError('Expected integer or string key')
        for v in values:
            if v.name==key:return v
        raise KeyError(key)
    def __contains__(self,key):
        if not isinstance(key,str):raise TypeError('Expected a string key')
        return any(v.name==key for v in self)
    def get(self,key,default=None):
        if not isinstance(key,str):raise TypeError('get() expects a string key')
        try:return self[key]
        except KeyError:return default
class Database(Sequence):
    def __init__(self,kind):
        self._kind=kind
        super().__init__('bpy.data.'+kind,lambda:[wrap(kind,k) for k in request('list',kind=kind)])
    def new(self,name,*args,**kwargs):
        if not isinstance(name,str):raise TypeError('name must be a string')
        extra={}
        if self._kind=='objects':
            if len(args)==1 and not kwargs:data=args[0]
            elif not args and set(kwargs)=={'object_data'}:data=kwargs['object_data']
            else:raise TypeError('new(name, object_data) requires a data block or None')
            if data is not None and not isinstance(data,(Mesh,Curve,Camera,Light)):raise TypeError('Expected a mesh, camera, light or None')
            extra['data']=ref(data)
        elif self._kind=='textures':
            if len(args)==1 and not kwargs:t=args[0]
            elif not args and set(kwargs)=={'type'}:t=kwargs['type']
            else:raise TypeError('new(name, type) requires a texture type')
            if t!='CLOUDS':raise UnsupportedError(self._path+'.new(type='+repr(t)+')','Procedural CLOUDS textures are supported.')
            extra['type']=t
        elif self._kind=='lights':
            if len(args)==1 and not kwargs:t=args[0]
            elif not args and set(kwargs)=={'type'}:t=kwargs['type']
            else:raise TypeError('new(name, type) requires a light type')
            if t not in ('POINT','SUN','SPOT','AREA'):raise UnsupportedError(self._path+'.new(type='+repr(t)+')')
            extra['type']=t
        elif args or kwargs:raise TypeError('new(name) takes one argument')
        return wrap(self._kind,request('new',kind=self._kind,name=name,extra=extra))
    def remove(self,datablock,*,do_unlink=True,do_id_user=True,do_ui_user=True):
        if not do_id_user or not do_ui_user:raise UnsupportedError(self._path+'.remove(do_id_user=False/do_ui_user=False)')
        if not isinstance(datablock,DataBlock) or datablock._kind!=self._kind:raise TypeError('Wrong data block type')
        request('remove',kind=self._kind,id=datablock._id,do_unlink=bool(do_unlink))
class Membership(Sequence):
    def __init__(self,owner,children=False):
        self._owner,self._children=owner,children
        kind='collections' if children else 'objects';field='children' if children else 'objects'
        super().__init__('bpy.types.Collection.'+field,lambda:[wrap(kind,k) for k in owner._read(field)])
    def link(self,object):
        if not isinstance(object,Collection if self._children else Object):raise TypeError('Wrong collection member type')
        request('link',id=self._owner._id,target=object._id,children=self._children,unlink=False)
    def unlink(self,object):request('link',id=self._owner._id,target=object._id,children=self._children,unlink=True)
class Collection(DataBlock):
    _kind='collections';_path='bpy.types.Collection'
    @property
    def objects(self):return Membership(self)
    @property
    def children(self):return Membership(self,True)
class ViewObjects(Sequence):
    def __init__(self):super().__init__('bpy.context.view_layer.objects',lambda:[wrap('objects',k) for k in request('linked')])
    @property
    def active(self):return wrap('objects',request('active'))
    @active.setter
    def active(self,value):
        if value is not None and not isinstance(value,Object):raise TypeError('Expected Object or None')
        request('set_active',value=None if value is None else value._id)
class MeshElement(Strict):
    def __init__(self,mesh,index,field):self._mesh,self._index,self._field=mesh,index,field;self._path='bpy.types.'+{'vertices':'MeshVertex','edges':'MeshEdge','faces':'MeshPolygon'}[field]
    def _read(self,field=None):return request('read',kind='meshes',id=self._mesh._id,path=[field or self._field,self._index])
    def _write(self,field,value):request('write',kind='meshes',id=self._mesh._id,path=[field,self._index],value=value)
    @property
    def index(self):return self._index
    @property
    def co(self):
        if self._field!='vertices':raise UnsupportedError(self._path+'.co')
        return VectorView(self._read,lambda v:self._set_co(v),self._path+'.co')
    @co.setter
    def co(self,value):self._set_co(value)
    def _set_co(self,v):
        if self._field!='vertices':raise UnsupportedError(self._path+'.co')
        v=list(v)
        if len(v)!=3:raise ValueError('Expected three coordinates')
        self._write('vertices',[f32(x) for x in v])
    @property
    def vertices(self):
        if self._field=='vertices':raise UnsupportedError(self._path+'.vertices')
        return tuple(self._read())
    @property
    def loop_indices(self):
        if self._field!='faces':raise UnsupportedError(self._path+'.loop_indices')
        faces=self._mesh._get()['faces']
        start=sum(len(face) for face in faces[:self._index])
        return range(start,start+len(faces[self._index]))
    @property
    def material_index(self):
        if self._field!='faces':raise UnsupportedError(self._path+'.material_index')
        return self._read('material_indices')
    @material_index.setter
    def material_index(self,v):
        if self._field!='faces':raise UnsupportedError(self._path+'.material_index')
        self._write('material_indices',max(0,min(32767,int(v))))
    @property
    def use_smooth(self):
        if self._field!='faces':raise UnsupportedError(self._path+'.use_smooth')
        return self._read('smooth')
    @use_smooth.setter
    def use_smooth(self,v):
        if self._field!='faces':raise UnsupportedError(self._path+'.use_smooth')
        self._write('smooth',bool(v))
class MeshElements(Strict):
    def __init__(self,mesh,field):self._mesh,self._field=mesh,field;self._path='bpy.types.Mesh.'+field
    def __len__(self):return request('length',kind='meshes',id=self._mesh._id,path=[self._field])
    def __iter__(self):return (self[i] for i in range(len(self)))
    def __getitem__(self,i):
        if isinstance(i,slice):return [self[j] for j in range(*i.indices(len(self)))]
        if i<0:i+=len(self)
        if not 0<=i<len(self):raise IndexError(i)
        return MeshElement(self._mesh,i,self._field)
class Materials(Strict):
    _path='bpy.types.Mesh.materials'
    def __init__(self,mesh):self._mesh=mesh
    def _ids(self):return self._mesh._read('materials')
    def __len__(self):return len(self._ids())
    def __iter__(self):return (wrap('materials',k) for k in self._ids())
    def __getitem__(self,i):return wrap('materials',self._ids()[i])
    def __setitem__(self,i,v):
        if v is not None and not isinstance(v,Material):raise TypeError('Expected material or None')
        ids=self._ids();ids[i]=None if v is None else v._id;self._mesh._set('materials',ids)
    def append(self,material):
        if not isinstance(material,Material):raise TypeError('Expected material')
        self._mesh._set('materials',self._ids()+[material._id])
    def clear(self):
        self._mesh._set('materials',[])
        self._mesh._set('material_indices',[0]*len(self._mesh.polygons))
    def pop(self,*,index=-1):
        ids=self._ids();i=index if index>=0 else len(ids)+index;k=ids.pop(index);self._mesh._set('materials',ids)
        indices=self._mesh._read('material_indices');self._mesh._set('material_indices',[max(0,n-1) if n>=i else n for n in indices])
        return wrap('materials',k)
class UVLoop(Strict):
    _path='bpy.types.MeshUVLoop'
    def __init__(self,layer,index):self._layer,self._index=layer,index
    def _get(self):return request('read',kind='meshes',id=self._layer._mesh._id,path=['uv_layers',self._layer._index,'data',self._index])
    def _set(self,value):
        if len(value)!=2:raise ValueError('UV needs two values')
        request('write',kind='meshes',id=self._layer._mesh._id,path=['uv_layers',self._layer._index,'data',self._index],value=[f32(x) for x in value])
    uv=property(lambda self:VectorView(self._get,self._set,self._path+'.uv'),_set)
class UVData(Strict):
    _path='bpy.types.MeshUVLoopLayer.data'
    def __init__(self,layer):self._layer=layer
    def __len__(self):return request('length',kind='meshes',id=self._layer._mesh._id,path=['uv_layers',self._layer._index,'data'])
    def __iter__(self):return (self[i] for i in range(len(self)))
    def __getitem__(self,i):
        if i<0:i+=len(self)
        if not 0<=i<len(self):raise IndexError(i)
        return UVLoop(self._layer,i)
class UVLayer(Strict):
    _path='bpy.types.MeshUVLoopLayer'
    def __init__(self,mesh,index):self._mesh,self._index=mesh,index
    @property
    def name(self):return request('read',kind='meshes',id=self._mesh._id,path=['uv_layers',self._index,'name'])
    @property
    def data(self):return UVData(self)
    @property
    def active_render(self):return self._mesh._get().get('render_uv',0)==self._index
    @active_render.setter
    def active_render(self,value):
        if value:
            if self._index>7:raise UnsupportedError(self._path+'.active_render','Use render UV channels 0..7.')
            self._mesh._set('render_uv',self._index)
class UVLayers(Sequence):
    def __init__(self,mesh):
        self._mesh=mesh
        super().__init__('bpy.types.Mesh.uv_layers',lambda:[UVLayer(mesh,i) for i in range(request('length',kind='meshes',id=mesh._id,path=['uv_layers']))])
    def new(self,*,name='UVMap',do_init=True):
        layers=self._mesh._read('uv_layers');used={x['name'] for x in layers};base=name;n=1
        while name in used:name=base+'.'+str(n).zfill(3);n+=1
        if layers and do_init:data=layers[self._mesh._read('active_uv')]['data']
        else:
            data=[]
            for face in self._mesh.polygons:
                count=len(face.vertices)
                if not do_init:data.extend([[0.,0.] for _ in range(count)])
                elif count<=4:data.extend([[0.,0.],[1.,0.],[1.,1.],[0.,1.]][:count])
                else:
                    step=f32(2*math.pi/count)
                    for i in range(count):
                        angle=f32(step*i)
                        data.append([f32(.5+f32(.5*f32(math.sin(angle)))),f32(.5+f32(.5*f32(math.cos(angle))))])
        layers.append(dict(name=name,data=data));self._mesh._set('uv_layers',layers)
        return UVLayer(self._mesh,len(layers)-1)
    @property
    def active(self):return self[self._mesh._read('active_uv')] if len(self) else None
    @active.setter
    def active(self,v):self._mesh._set('active_uv',v._index)
class CornerColor(Strict):
    _path='bpy.types.FloatColorAttributeValue'
    def __init__(self,mesh,index):self._mesh,self._index=mesh,index
    def _get(self):return request('read',kind='meshes',id=self._mesh._id,path=['colors',self._index])
    def _set(self,value):
        value=[f32(x) for x in value]
        if len(value)!=4 or any(not -float('inf')<x<float('inf') for x in value):raise ValueError('Expected four finite color components')
        request('write',kind='meshes',id=self._mesh._id,path=['colors',self._index],value=value)
    color=property(lambda self:NumericView(self._get,self._set,self._path+'.color'),_set)
class CornerColorData(Strict):
    _path='bpy.types.FloatColorAttribute.data'
    def __init__(self,mesh):self._mesh=mesh
    def __len__(self):return len(self._mesh._read('colors'))
    def __iter__(self):return (self[i] for i in range(len(self)))
    def __getitem__(self,i):
        if i<0:i+=len(self)
        if not 0<=i<len(self):raise IndexError(i)
        return CornerColor(self._mesh,i)
class CornerColorAttribute(Strict):
    _path='bpy.types.FloatColorAttribute'
    def __init__(self,mesh):self._mesh=mesh
    @property
    def name(self):return self._mesh._get().get('color_attribute_name','Color')
    @property
    def domain(self):return 'CORNER'
    @property
    def data_type(self):return 'FLOAT_COLOR'
    @property
    def data(self):return CornerColorData(self._mesh)
class CornerColorAttributes(Sequence):
    def __init__(self,mesh):
        self._mesh=mesh
        super().__init__('bpy.types.Mesh.color_attributes',lambda:[CornerColorAttribute(mesh)] if mesh._read('colors') or mesh._get().get('color_attribute_name') else [])
    def new(self,name,type,domain):
        if type!='FLOAT_COLOR' or domain!='CORNER':raise UnsupportedError(self._path+'.new','This subset supports one FLOAT_COLOR CORNER attribute')
        if len(self):raise UnsupportedError(self._path+'.new','This subset supports one corner color attribute')
        if not str(name) or len(str(name).encode())>63:raise ValueError('Color attribute name requires 1..63 UTF-8 bytes')
        self._mesh._set('colors',[[0.,0.,0.,1.] for _ in range(sum(len(f) for f in self._mesh._read('faces')))])
        self._mesh._set('color_attribute_name',str(name))
        return CornerColorAttribute(self._mesh)
class CreaseValue(Strict):
    _path='bpy.types.FloatAttributeValue'
    def __init__(self,mesh,name,index):self._mesh,self._name,self._index=mesh,name,index
    def _get(self):return request('read',kind='meshes',id=self._mesh._id,path=[self._name,self._index])
    def _set(self,value):
        value=f32(value)
        if not 0<=value<=1:raise ValueError('Crease values must be finite in 0..1')
        request('write',kind='meshes',id=self._mesh._id,path=[self._name,self._index],value=value)
    value=property(_get,_set)
class CreaseAttribute(Strict):
    _path='bpy.types.FloatAttribute'
    def __init__(self,mesh,name):self._mesh,self._name=mesh,name
    @property
    def name(self):return self._name
    @property
    def domain(self):return 'EDGE' if self._name=='crease_edge' else 'POINT'
    @property
    def data_type(self):return 'FLOAT'
    @property
    def data(self):return Sequence(self._path+'.data',lambda:[CreaseValue(self._mesh,self._name,i) for i in range(len(self._mesh._read(self._name)))])
class FaceStrengthValue(Strict):
    _path='bpy.types.IntAttributeValue'
    def __init__(self,mesh,index):self._mesh,self._index=mesh,index
    def _get(self):return request('read',kind='meshes',id=self._mesh._id,path=['face_strength',self._index])
    def _set(self,value):
        value=int(value)
        if not 0<=value<=2:raise ValueError('Face strength requires 0 (weak), 1 (medium) or 2 (strong)')
        request('write',kind='meshes',id=self._mesh._id,path=['face_strength',self._index],value=value)
    value=property(_get,_set)
class FaceStrengthAttribute(Strict):
    _path='bpy.types.IntAttribute'
    def __init__(self,mesh):self._mesh=mesh
    @property
    def name(self):return '__mod_weightednormals_faceweight'
    @property
    def domain(self):return 'FACE'
    @property
    def data_type(self):return 'INT'
    @property
    def data(self):return Sequence(self._path+'.data',lambda:[FaceStrengthValue(self._mesh,i) for i in range(len(self._mesh._read('faces')))])
class MeshAttributes(Sequence):
    def __init__(self,mesh):
        self._mesh=mesh
        super().__init__('bpy.types.Mesh.attributes',lambda:[CreaseAttribute(mesh,n) for n in ('crease_edge','crease_vert') if n in mesh._get()]+([FaceStrengthAttribute(mesh)] if 'face_strength' in mesh._get() else []))
    def new(self,name,type,domain):
        if (name,type,domain)==('__mod_weightednormals_faceweight','INT','FACE'):
            if self.get(name) is not None:raise ValueError('Face strength attribute already exists')
            self._mesh._set('face_strength',[0]*len(self._mesh._read('faces')))
            return FaceStrengthAttribute(self._mesh)
        if type!='FLOAT' or (name,domain) not in (('crease_edge','EDGE'),('crease_vert','POINT')):raise UnsupportedError(self._path+'.new','Only crease_edge FLOAT EDGE, crease_vert FLOAT POINT and __mod_weightednormals_faceweight INT FACE are supported')
        if self.get(name) is not None:raise ValueError('Crease attribute already exists')
        self._mesh._set(name,[0.] * len(self._mesh._read('edges' if domain=='EDGE' else 'vertices')))
        return CreaseAttribute(self._mesh,name)
class Mesh(DataBlock):
    _kind='meshes';_path='bpy.types.Mesh'
    @property
    def color_attributes(self):return CornerColorAttributes(self)
    @property
    def attributes(self):return MeshAttributes(self)
    def normals_split_custom_set(self,normals):
        values=[list(n) for n in normals]
        if len(values)!=sum(len(f) for f in self._read('faces')):raise ValueError('Expected one normal per mesh corner')
        result=[]
        for normal in values:
            if len(normal)!=3:raise ValueError('Expected three normal components')
            normal=[f32(x) for x in normal]
            length=sum(x*x for x in normal)**.5
            if not 0<length<float('inf'):raise ValueError('Custom normals must be finite and nonzero')
            result.append([f32(x/length) for x in normal])
        self._set('loop_normals',result)
    @property
    def has_custom_normals(self):return bool(self._read('loop_normals'))
    def from_pydata(self,vertices,edges,faces,shade_flat=True):request('mesh_from',id=self._id,vertices=[list(v) for v in vertices],edges=[list(e) for e in edges],faces=[list(f) for f in faces],smooth=not shade_flat)
    def update(self,*,calc_edges=False,calc_edges_loose=False):request('mesh_update',id=self._id,calc_edges=bool(calc_edges),calc_edges_loose=bool(calc_edges_loose))
    @property
    def vertices(self):return MeshElements(self,'vertices')
    @property
    def edges(self):return MeshElements(self,'edges')
    @property
    def polygons(self):return MeshElements(self,'faces')
    @property
    def materials(self):return Materials(self)
    @property
    def uv_layers(self):return UVLayers(self)
class Camera(DataBlock):
    _kind='cameras';_path='bpy.types.Camera'
    type=prop('type',choices=('PERSP','ORTHO'));lens=prop('lens',float,1);sensor_width=prop('sensor_width',float,.001);sensor_height=prop('sensor_height',float,.001);sensor_fit=prop('sensor_fit',choices=('AUTO','HORIZONTAL','VERTICAL'))
    clip_start=prop('clip_start',float,.000001);clip_end=prop('clip_end',float,.000001);ortho_scale=prop('ortho_scale',float,.000001);shift_x=prop('shift_x',float);shift_y=prop('shift_y',float)
class Light(DataBlock):
    shape=prop('shape',str,choices=('SQUARE','RECTANGLE','DISK','ELLIPSE'))
    size_y=prop('size_y',float,0.,3.4028234663852886e38)
    use_shadow=prop('use_shadow',bool)
    _kind='lights';_path='bpy.types.Light'
    def _guard(self,name):
        allowed={'shadow_soft_size':('POINT','SPOT'),'size':('AREA',),'size_y':('AREA',),'shape':('AREA',),'spot_size':('SPOT',),'spot_blend':('SPOT',)}
        if name in allowed and DataBlock._read(self,'type') not in allowed[name]:raise UnsupportedError(self._path+'.'+name,'This property is unavailable for this light type.')
    def _read(self,name):self._guard(name);return DataBlock._read(self,name)
    def _set(self,name,value):self._guard(name);return DataBlock._set(self,name,value)
    type=prop('type',choices=('POINT','SUN','SPOT','AREA'));energy=prop('energy',float,0);color=vector_prop('color',3,True);shadow_soft_size=prop('shadow_soft_size',float,0);size=prop('size',float,0);spot_size=prop('spot_size',float,.0174533,3.1415927);spot_blend=prop('spot_blend',float,0,1)
NODE_TYPES={'ShaderNodeBsdfPrincipled':('Principled BSDF',{'Base Color':[.8,.8,.8,1.],'Metallic':0.,'Roughness':.5,'Alpha':1.,'Emission Color':[1.,1.,1.,1.],'Emission Strength':0.,'Normal':[0.,0.,0.]},['BSDF']), 'ShaderNodeOutputMaterial':('Material Output',{'Surface':None},[]),'ShaderNodeTexImage':('Image Texture',{'Vector':[0.,0.,0.]},['Color','Alpha']),'ShaderNodeNormalMap':('Normal Map',{'Strength':1.,'Color':[.5,.5,1.,1.]},['Normal'])}
PRINCIPLED_INPUTS={'Base Color': [0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0], 'Metallic': 0.0, 'Roughness': 0.5, 'IOR': 1.5, 'Alpha': 1.0, 'Normal': [0.0, 0.0, 0.0], 'Diffuse Roughness': 0.0, 'Subsurface Weight': 0.0, 'Subsurface Radius': [1.0, 0.20000000298023224, 0.10000000149011612], 'Subsurface Scale': 0.05000000074505806, 'Subsurface Anisotropy': 0.0, 'Specular IOR Level': 0.5, 'Specular Tint': [1.0, 1.0, 1.0, 1.0], 'Anisotropic': 0.0, 'Anisotropic Rotation': 0.0, 'Tangent': [0.0, 0.0, 0.0], 'Transmission Weight': 0.0, 'Coat Weight': 0.0, 'Coat Roughness': 0.029999999329447746, 'Coat IOR': 1.5, 'Coat Tint': [1.0, 1.0, 1.0, 1.0], 'Coat Normal': [0.0, 0.0, 0.0], 'Sheen Weight': 0.0, 'Sheen Roughness': 0.5, 'Sheen Tint': [1.0, 1.0, 1.0, 1.0], 'Emission Color': [1.0, 1.0, 1.0, 1.0], 'Emission Strength': 0.0, 'Thin Film Thickness': 0.0, 'Thin Film IOR': 1.3300000429153442}
NODE_TYPES['ShaderNodeBsdfPrincipled']=('Principled BSDF',PRINCIPLED_INPUTS,['BSDF'])
NODE_TYPES.update({'ShaderNodeMapping':('Mapping',{'Vector':[0.,0.,0.],'Location':[0.,0.,0.],'Rotation':[0.,0.,0.],'Scale':[1.,1.,1.]},['Vector']),'ShaderNodeTexCoord':('Texture Coordinate',{},['UV'])})
WORLD_NODE_TYPES={'ShaderNodeBackground':('Background',{'Color':[.05,.05,.05,1.],'Strength':1.},['Background']),'ShaderNodeOutputWorld':('World Output',{'Surface':None},[]),'ShaderNodeTexEnvironment':('Environment Texture',{'Vector':[0.,0.,0.]},['Color'])}
class Socket(Strict):
    _path='bpy.types.NodeSocket'
    def __init__(self,node,name,output=False):self._node,self._name,self._output=node,name,output
    @property
    def name(self):return self._name
    @property
    def default_value(self):
        if self._output:raise UnsupportedError(self._path+'.default_value','Output socket values are computed.')
        value=self._node._record()['inputs'][self._name]
        return NumericView(lambda:self._node._record()['inputs'][self._name],lambda v:self._set_value(v),self._path+'.default_value') if isinstance(value,list) else value
    @default_value.setter
    def default_value(self,value):self._set_value(value)
    def _set_value(self,value):
        if self._output:raise UnsupportedError(self._path+'.default_value')
        if self._node._record()['type']=='ShaderNodeNormalMap' and self._name=='Color':raise UnsupportedError(self._path+'.default_value','Use a linked normal-map image; explicit normal colors are outside the tested subset.')
        if self._node._record()['type'] in ('ShaderNodeTexImage','ShaderNodeTexEnvironment','ShaderNodeMapping') and self._name=='Vector':raise UnsupportedError(self._path+'.default_value','Use the documented UV Mapping/TexCoord chain for Image Texture; direct image/environment vectors are outside the tested subset.')
        old=self._node._record()['inputs'][self._name]
        if old is None:raise UnsupportedError(self._path+'.default_value','Shader sockets require links.')
        if self._node._record()['type']=='ShaderNodeBsdfPrincipled' and self._name in ('Normal','Coat Normal','Tangent'):raise UnsupportedError(self._path+'.default_value','Use a linked normal-map image; direct Normal/Coat Normal/Tangent writes are outside the tested subset.')
        if isinstance(old,list):
            value=list(value)
            if len(value)!=len(old):raise ValueError('Wrong socket vector length')
            value=[f32(max(0,x) if (self._node.bl_idname=='ShaderNodeBackground' and self._name=='Color' or self._node.bl_idname=='ShaderNodeBsdfPrincipled' and len(old)==4) else x) for x in value]
        else:
            value=f32(value)
            # Blender float node sockets retain values outside their UI slider ranges.
            if self._node.bl_idname=='ShaderNodeNormalMap' and self._name=='Strength':value=max(0,value)
        if self._node.bl_idname=='ShaderNodeMapping' and (self._name=='Location' and value[2]!=0 or self._name=='Rotation' and any(value[:2]) or self._name=='Scale' and value[2]!=1):raise UnsupportedError(self._path+'.default_value','Use planar UV Mapping: XY location/scale, Z rotation, scale Z=1.')
        nodes=self._node._material._read('nodes');nodes[self._node._index]['inputs'][self._name]=value;self._node._material._set('nodes',nodes)
class Sockets(Sequence):
    def __getitem__(self,key):
        try:return super().__getitem__(key)
        except KeyError:raise UnsupportedError(self._path+'['+repr(key)+']','This socket is outside the tested node subset; use the named inputs in hb api.')
class Node(Strict):
    _path='bpy.types.ShaderNode'
    def __init__(self,material,index):self._material,self._index=material,index
    def __eq__(self,other):return isinstance(other,Node) and self._material is other._material and self._index==other._index
    def _record(self):
        record=self._material._read('nodes')[self._index]
        if record['type']=='ShaderNodeBsdfPrincipled':record['inputs']={**PRINCIPLED_INPUTS,**record['inputs']}
        return record
    @property
    def bl_idname(self):return self._record()['type']
    @property
    def type(self):return {'ShaderNodeBsdfPrincipled':'BSDF_PRINCIPLED','ShaderNodeOutputMaterial':'OUTPUT_MATERIAL','ShaderNodeTexImage':'TEX_IMAGE','ShaderNodeNormalMap':'NORMAL_MAP','ShaderNodeBackground':'BACKGROUND','ShaderNodeOutputWorld':'OUTPUT_WORLD','ShaderNodeTexEnvironment':'TEX_ENVIRONMENT','ShaderNodeMapping':'MAPPING','ShaderNodeTexCoord':'TEX_COORD'}[self.bl_idname]
    @property
    def name(self):return self._record()['name']
    @name.setter
    def name(self,value):
        nodes=self._material._read('nodes');used={n['name'] for i,n in enumerate(nodes) if i!=self._index};name=str(value);base=name;n=1
        while name in used:name=base+'.'+str(n).zfill(3);n+=1
        nodes[self._index]['name']=name;self._material._set('nodes',nodes)
    @property
    def inputs(self):return Sockets(self._path+'.inputs',lambda:[Socket(self,n) for n in self._record()['inputs']])
    @property
    def outputs(self):return Sockets(self._path+'.outputs',lambda:[Socket(self,n,True) for n in {**NODE_TYPES,**WORLD_NODE_TYPES}[self._record()['type']][2]])
    @property
    def image(self):
        if self._record()['type'] not in ('ShaderNodeTexImage','ShaderNodeTexEnvironment'):raise UnsupportedError(self._path+'.image')
        return wrap('images',self._record().get('image'))
    @image.setter
    def image(self,value):
        if self._record()['type'] not in ('ShaderNodeTexImage','ShaderNodeTexEnvironment'):raise UnsupportedError(self._path+'.image')
        if value is not None and not isinstance(value,Image):raise TypeError('Expected image or None')
        nodes=self._material._read('nodes');nodes[self._index]['image']=None if value is None else value._id;self._material._set('nodes',nodes)
    def _read(self,name):
        defaults={'ShaderNodeTexEnvironment':{'projection':'EQUIRECTANGULAR','interpolation':'Linear'},'ShaderNodeTexImage':{'projection':'FLAT','interpolation':'Linear','extension':'REPEAT'},'ShaderNodeMapping':{'vector_type':'POINT'},'ShaderNodeTexCoord':{'object':None,'from_instancer':False}}
        allowed=defaults.get(self.bl_idname,{})
        if name not in allowed:raise UnsupportedError(self._path+'.'+name)
        return self._record().get(name,allowed[name])
    def _set(self,name,value):
        default=self._read(name)
        if name=='projection' and value!=default:raise UnsupportedError(self._path+'.projection','Use FLAT for Image Texture or EQUIRECTANGULAR for Environment Texture.')
        nodes=self._material._read('nodes');nodes[self._index][name]=value;self._material._set('nodes',nodes)
    projection=prop('projection',str,choices=('EQUIRECTANGULAR','FLAT'))
    interpolation=prop('interpolation',str,choices=('Linear',))
    extension=prop('extension',str,choices=('REPEAT','EXTEND','MIRROR'))
    vector_type=prop('vector_type',str,choices=('POINT',))
    object=property(lambda self:self._read('object'))
    from_instancer=property(lambda self:self._read('from_instancer'))
class Nodes(Sequence):
    def __init__(self,material):self._material=material;super().__init__(material._path+'.node_tree.nodes',lambda:[Node(material,i) for i in range(len(material._read('nodes') or []))])
    def new(self,type):
        types=WORLD_NODE_TYPES if self._material._kind=='worlds' else NODE_TYPES
        if type not in types:raise UnsupportedError(self._path+'.new('+repr(type)+')','Use only the node types listed for this tree in hb api; World trees allow Background, World Output and Environment Texture.')
        nodes=self._material._read('nodes') or []
        if type in ('ShaderNodeBsdfPrincipled','ShaderNodeOutputMaterial','ShaderNodeBackground','ShaderNodeOutputWorld','ShaderNodeTexEnvironment','ShaderNodeMapping','ShaderNodeTexCoord') and any(n['type']==type for n in nodes):raise UnsupportedError(self._path+'.new('+repr(type)+')','Only one shader/background, output, and World environment are supported in a tree; reuse the existing node.')
        name,inputs,_=types[type];used={n['name'] for n in nodes};base=name;i=1
        while name in used:name=base+'.'+str(i).zfill(3);i+=1
        nodes.append(dict(name=name,type=type,inputs=inputs,image=None));self._material._set('nodes',nodes);return Node(self._material,len(nodes)-1)
    def clear(self):self._material._set('nodes',[]);self._material._set('links',[])
class Links(Strict):
    _path='bpy.types.Material.node_tree.links'
    def __init__(self,material):self._material=material;self._path=material._path+'.node_tree.links'
    def new(self,input,output,*,verify_limits=True,handle_dynamic_sockets=False):
        a,b=input,output
        if not a._output and b._output:a,b=b,a
        if not a._output or b._output or a._node._material is not self._material or b._node._material is not self._material:raise ValueError('Expected output and input sockets in the same node tree')
        source=a._node._record()['type'];target=b._node._record()['type']
        allowed=(source,a._name,target,b._name) in [('ShaderNodeTexCoord','UV','ShaderNodeMapping','Vector'),('ShaderNodeTexCoord','UV','ShaderNodeTexImage','Vector'),('ShaderNodeMapping','Vector','ShaderNodeTexImage','Vector'),('ShaderNodeBackground','Background','ShaderNodeOutputWorld','Surface'),('ShaderNodeTexEnvironment','Color','ShaderNodeBackground','Color'),('ShaderNodeBsdfPrincipled','BSDF','ShaderNodeOutputMaterial','Surface'),('ShaderNodeTexImage','Color','ShaderNodeBsdfPrincipled','Base Color'),('ShaderNodeTexImage','Color','ShaderNodeBsdfPrincipled','Emission Color'),('ShaderNodeTexImage','Alpha','ShaderNodeBsdfPrincipled','Alpha'),('ShaderNodeTexImage','Color','ShaderNodeNormalMap','Color'),('ShaderNodeNormalMap','Normal','ShaderNodeBsdfPrincipled','Normal')]
        if not allowed or not verify_limits or handle_dynamic_sockets:raise UnsupportedError(self._path+'.new(...)','Use the documented Principled/Image/Mapping/TexCoord or World Background/Environment connections; legacy Normal Map links remain supported.')
        link=dict(source=a._node._index,output=a._name,target=b._node._index,input=b._name)
        links=[l for l in self._material._read('links') if (l['target'],l['input'])!=(link['target'],link['input'])];links.append(link);self._material._set('links',links)
        return Namespace('bpy.types.NodeLink',from_node=a._node,to_node=b._node,from_socket=a,to_socket=b)
class Material(DataBlock):
    _kind='materials';_path='bpy.types.Material'
    diffuse_color=vector_prop('diffuse_color',4,True);metallic=prop('metallic',float,0,1);roughness=prop('roughness',float,0,1)
    @property
    def use_nodes(self):return self._read('use_nodes')
    @use_nodes.setter
    def use_nodes(self,value):
        if value and self._read('nodes') is None:
            self._set('nodes',[]);nodes=Nodes(self);bsdf=nodes.new('ShaderNodeBsdfPrincipled');out=nodes.new('ShaderNodeOutputMaterial');Links(self).new(bsdf.outputs['BSDF'],out.inputs['Surface'])
        self._set('use_nodes',bool(value))
    @property
    def node_tree(self):return None if self._read('nodes') is None else Namespace(self._path+'.node_tree',nodes=Nodes(self),links=Links(self))
class Pixels(Strict):
    _path='bpy.types.Image.pixels'
    def __init__(self,image):self._image=image
    def __len__(self):return self._image.size[0]*self._image.size[1]*4
    def __getitem__(self,key):return tuple(request('image_pixels',id=self._image._id))[key]
    def __iter__(self):return iter(request('image_pixels',id=self._image._id))
    def __setitem__(self,key,value):
        data=request('image_pixels',id=self._image._id);data[key]=value
        if len(data)!=len(self):raise ValueError('Pixel count must remain unchanged')
        request('image_set_pixels',id=self._image._id,pixels=[f32(x) for x in data])
class ColorSpace(Strict):
    _path='bpy.types.Image.colorspace_settings'
    def __init__(self,image):self._image=image
    @property
    def name(self):return self._image._read('colorspace')
    @name.setter
    def name(self,value):
        if value not in ('sRGB','Non-Color'):raise UnsupportedError(self._path+'.name='+repr(value))
        self._image._set('colorspace',value)
class Image(DataBlock):
    _kind='images';_path='bpy.types.Image'
    filepath=prop('filepath',str)
    @property
    def size(self):return (self._read('width'),self._read('height'))
    @property
    def pixels(self):return Pixels(self)
    @pixels.setter
    def pixels(self,values):Pixels(self)[:]=list(values)
    @property
    def colorspace_settings(self):return ColorSpace(self)
class Images(Database):
    def __init__(self):super().__init__('images')
    def new(self,name,width,height,*,alpha=True,float_buffer=False,stereo3d=False,is_data=False,tiled=False):
        if stereo3d or tiled:raise UnsupportedError(self._path+'.new(stereo3d/tiled=True)')
        return wrap('images',request('image_new',name=name,width=int(width),height=int(height),alpha=bool(alpha),float_buffer=bool(float_buffer),is_data=bool(is_data)))
    def load(self,filepath,*,check_existing=False):return wrap('images',request('image_load',path=str(filepath),check_existing=bool(check_existing)))
class CloudsTexture(DataBlock):
    _kind='textures';_path='bpy.types.CloudsTexture'
    type=property(lambda self:self._read('type'))
    noise_basis=prop('noise_basis',str,choices=('BLENDER_ORIGINAL','CELL_NOISE'))
    noise_scale=prop('noise_scale',float,0.0001,3.4028234663852886e38)
    noise_depth=prop('noise_depth',int,0,30)
    noise_type=prop('noise_type',str,choices=('SOFT_NOISE','HARD_NOISE'))
    cloud_type=prop('cloud_type',str,choices=('GRAYSCALE',))
    intensity=prop('intensity',float,0.,2.);contrast=prop('contrast',float,0.,5.)
    def evaluate(self,value):
        value=list(value)
        if len(value)!=3:raise ValueError('Texture.evaluate requires three coordinates')
        return Vector(request('texture_evaluate',id=self._id,position=[f32(v) for v in value]))
class World(DataBlock):
    _kind='worlds';_path='bpy.types.World'
    def _read(self,field):return self._get().get(field,[] if field=='links' else None)
    def _set_color(self,value):
        value=list(value)
        if len(value)!=3:raise ValueError('World color requires three components')
        self._set('color',[f32(max(0.,min(3.4028234663852886e38,float(c)))) for c in value])
    color=property(lambda self:NumericView(lambda:self._read('color'),self._set_color,self._path+'.color'),_set_color)
    def _ensure_nodes(self):
        if self._read('nodes') is None:
            self._set('nodes',[]);self._set('links',[])
            nodes=Nodes(self);bg=nodes.new('ShaderNodeBackground');out=nodes.new('ShaderNodeOutputWorld')
            bg.inputs['Color'].default_value=(*self.color,1.)
            Links(self).new(bg.outputs['Background'],out.inputs['Surface'])
    @property
    def use_nodes(self):return self._read('use_nodes')
    @use_nodes.setter
    def use_nodes(self,value):
        if value:self._ensure_nodes()
        self._set('use_nodes',bool(value))
    @property
    def node_tree(self):
        if self.use_nodes:self._ensure_nodes()
        return None if self._read('nodes') is None else Namespace(self._path+'.node_tree',nodes=Nodes(self),links=Links(self))

CLASSES={'objects':Object,'meshes':Mesh,'materials':Material,'cameras':Camera,'lights':Light,'collections':Collection,'images':Image,'textures':CloudsTexture,'worlds':World}
class RenderSettings(Strict):
    _path='bpy.context.scene.render'
    def _read(self,key):return request('settings')['render'][key]
    def _set(self,key,value):request('set_render',field=key,value=value)
    resolution_x=prop('resolution_x',int,4,65536);resolution_y=prop('resolution_y',int,4,65536);resolution_percentage=prop('resolution_percentage',int,1,32767)
    pixel_aspect_x=prop('pixel_aspect_x',float,.01,200);pixel_aspect_y=prop('pixel_aspect_y',float,.01,200);filepath=prop('filepath',str)
class SceneContext(Strict):
    _path='bpy.context.scene'
    @property
    def objects(self):return Sequence(self._path+'.objects',lambda:[wrap('objects',k) for k in request('linked')])
    @property
    def collection(self):return wrap('collections',0)
    @property
    def camera(self):return wrap('objects',request('settings')['camera'])
    @camera.setter
    def camera(self,value):request('set_camera',value=None if value is None else value._id)
    @property
    def render(self):return RenderSettings()
    @property
    def world(self):return wrap('worlds',request('settings')['world'])
    @world.setter
    def world(self,value):
        if value is not None and not isinstance(value,World):raise TypeError('Expected World or None')
        request('set_world',value=None if value is None else value._id)
_UNSET=object()
def primitive_cube_add(*,size=2.,calc_uvs=True,enter_editmode=False,align='WORLD',location=(0.,0.,0.),rotation=(0.,0.,0.),scale=_UNSET):
    if enter_editmode or align!='WORLD':raise UnsupportedError('bpy.ops.mesh.primitive_cube_add','Only object-mode WORLD-aligned creation is supported.')
    scale=(1.,1.,1.) if scale is _UNSET else tuple(scale)
    request('cube',size=f32(size),calc_uvs=bool(calc_uvs),location=list(location),rotation=list(rotation),scale=list(scale));return {'FINISHED'}
def select_all(*,action='TOGGLE'):
    if action not in ('SELECT','DESELECT','INVERT','TOGGLE'):raise TypeError('Invalid selection action')
    objects=list(bpy.context.scene.objects)
    if action=='TOGGLE':action='DESELECT' if any(o.select_get() for o in objects) else 'SELECT'
    for obj in objects:obj.select_set(not obj.select_get() if action=='INVERT' else action=='SELECT')
    return {'FINISHED'}
def delete(*,use_global=False,confirm=True):
    for obj in list(bpy.context.selected_objects):
        if use_global:bpy.data.objects.remove(obj)
        else:
            for col in obj.users_collection:col.objects.unlink(obj)
            bpy.data.objects.remove(obj)
    return {'FINISHED'}
def shade_smooth(*,keep_sharp_edges=True):
    for obj in bpy.context.selected_objects:
        if isinstance(obj.data,Mesh):obj.data._set('smooth',[True]*len(obj.data.polygons))
    return {'FINISHED'}
def shade_flat():
    for obj in bpy.context.selected_objects:
        if isinstance(obj.data,Mesh):obj.data._set('smooth',[False]*len(obj.data.polygons))
    return {'FINISHED'}
class Module(types.ModuleType):
    def __getattr__(self,name):raise UnsupportedError(self.__name__+'.'+name)
    def __setattr__(self,name,value):
        if not name.startswith('_'):raise UnsupportedError(self.__name__+'.'+name)
        super().__setattr__(name,value)
def install_module(name,values):
    module=Module(name);module.__dict__['__path__']=[];module.__dict__.update(values);sys.modules[name]=module;return module
bpy=install_module('bpy',dict(data=Namespace('bpy.data',**{k:Database(k) for k in CLASSES if k!='images'},images=Images()),context=Namespace('bpy.context',object=Dynamic(lambda:wrap('objects',request('active'))),active_object=Dynamic(lambda:wrap('objects',request('active'))),selected_objects=Dynamic(lambda:[o for o in bpy.context.scene.objects if o.select_get()]),scene=SceneContext(),collection=Dynamic(lambda:wrap('collections',request('settings')['active_collection'])),view_layer=Namespace('bpy.context.view_layer',objects=ViewObjects(),update=lambda:request('update'))),ops=Namespace('bpy.ops',mesh=Namespace('bpy.ops.mesh',primitive_cube_add=primitive_cube_add),object=Namespace('bpy.ops.object',select_all=select_all,delete=delete,shade_smooth=shade_smooth,shade_flat=shade_flat))))
install_module('bmesh',{});install_module('mathutils',{})
install_module('hb',{'UnsupportedError':UnsupportedError,'snapshot':lambda:request('snapshot')})

_operation_warnings=[]

def execute(source, filename):
    # User prints go to stderr; stdout stays a single JSON document.
    _operation_warnings.clear()
    previous = sys.stdout
    sys.stdout = sys.stderr
    try:
        import random
        random.setstate((3, _hb.seed_state(SEED), None))
        exec(compile(source, filename, 'exec'), {'__name__':'__main__', '__file__':filename})
        if _edit_object() is not None:raise UnsupportedError('bpy.ops.object.mode_set','Finish primitive editing with mode_set(mode="OBJECT") before the script ends')
        _evaluate_curves()
        result = {'ok':True}
        if _operation_warnings:result['warnings']=_operation_warnings[:]
    except BaseException as exc:
        tb=exc.__traceback__
        frames=[]
        while tb:
            if tb.tb_frame.f_code.co_filename == filename:
                frames.append(dict(file=filename,line=tb.tb_lineno,function=tb.tb_frame.f_code.co_name))
            tb=tb.tb_next
        line=frames[-1]['line'] if frames else getattr(exc,'lineno',None)
        result={'ok':False,'error':dict(code='UNSUPPORTED_API' if isinstance(exc,UnsupportedError) else 'SCRIPT_ERROR',message=str(exc),location=f'{filename}:{line}' if line else filename,suggestion=getattr(exc,'suggestion','Correct the script and rerun; the scene was not saved.'),doc=getattr(exc,'doc','docs/compatibility.md#errors'),frames=frames)}
    finally: sys.stdout=previous
    _hb.request(json.dumps({'op':'execution_result','value':result}))
