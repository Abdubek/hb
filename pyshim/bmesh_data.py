"""Bounded editable UV, float-color and relative shape-key layers."""
class ShapePoint(Strict):
    _path='bpy.types.ShapeKeyPoint'
    def __init__(self,mesh,key,index):self._mesh,self._key,self._index=mesh,key,index
    def _get(self):return request('read',kind='meshes',id=self._mesh._id,path=['shape_keys',self._key,'points',self._index])
    def _set(self,value):
        value=[f32(v) for v in value]
        if len(value)!=3 or not all(math.isfinite(v) for v in value):raise ValueError('Shape coordinates require three finite components')
        request('write',kind='meshes',id=self._mesh._id,path=['shape_keys',self._key,'points',self._index],value=value)
    co=property(lambda s:VectorView(s._get,s._set,s._path+'.co'),_set)
class ShapeKey(Strict):
    _path='bpy.types.ShapeKey'
    def __init__(self,mesh,index):self._mesh,self._index=mesh,index
    @property
    def name(self):return self._mesh._read('shape_keys')[self._index]['name']
    @property
    def data(self):return Sequence(self._path+'.data',lambda:[ShapePoint(self._mesh,self._index,i) for i in range(len(self._mesh._read('vertices')))])
class Key(Strict):
    _path='bpy.types.Key'
    def __init__(self,mesh):self._mesh=mesh
    @property
    def key_blocks(self):return Sequence(self._path+'.key_blocks',lambda:[ShapeKey(self._mesh,i) for i in range(len(self._mesh._read('shape_keys')))])
def _shape_key_add(obj,*,name='Key',from_mix=True):
    mesh=obj.data
    if not isinstance(mesh,Mesh):raise UnsupportedError('bpy.types.Object.shape_key_add','Shape keys require mesh data')
    values=mesh._get().get('shape_keys',[])
    if len(values)>=64:raise UnsupportedError('bpy.types.Object.shape_key_add','At most 64 relative shape keys')
    name=str(name)
    if not name or len(name.encode())>63:raise ValueError('Shape-key name needs 1..63 UTF-8 bytes')
    names={v['name'] for v in values};base=name;i=1
    while name in names:name=base[:59]+'.'+str(i).zfill(3);i+=1
    values.append(dict(name=name,points=mesh._read('vertices')))
    mesh._set('shape_keys',values)
    return ShapeKey(mesh,len(values)-1)
Object.shape_key_add=_shape_key_add
Mesh.shape_keys=property(lambda mesh:Key(mesh) if mesh._get().get('shape_keys') else None)

class BMLayerItem(Strict):
    _path='bmesh.types.BMLayerItem'
    def __init__(self,collection,name):self._collection,self._name,self._valid=collection,name,True
    def _check(self):
        self._collection._bm._check()
        if not self._valid:raise ReferenceError('BMesh layer has been removed')
    @property
    def name(self):self._check();return self._name
class BMLayerCollection(Strict):
    _path='bmesh.types.BMLayerCollection'
    def __init__(self,bm,kind):self._bm,self._kind,self._items,self._active=bm,kind,[],0
    def __len__(self):self._bm._check();return len(self._items)
    def __iter__(self):self._bm._check();return iter(self._items)
    def __getitem__(self,key):
        self._bm._check()
        if isinstance(key,int):return self._items[key]
        for item in self._items:
            if item.name==key:return item
        raise KeyError(key)
    def get(self,name,default=None):
        try:return self[name]
        except KeyError:return default
    def keys(self):return [item.name for item in self]
    @property
    def active(self):return self._items[min(self._active,len(self)-1)] if len(self) else None
    def new(self,name):
        self._bm._check();name=str(name)
        if not name or len(name.encode())>63:raise ValueError('Layer name needs 1..63 UTF-8 bytes')
        limit={'uv':8,'float_color':1,'shape':64}[self._kind]
        if len(self)>=limit:raise UnsupportedError(self._path+'.new','Layer count exceeds the manifest bound')
        if self.get(name) is not None:raise ValueError('Duplicate BMesh layer name')
        item=BMLayerItem(self,name);self._items.append(item);return item
    def verify(self):return self.active or self.new({'uv':'Float2','float_color':'Color','shape':'ShapeKey'}[self._kind])
    def remove(self,item):
        self._bm._check()
        if item not in self._items:raise ValueError('Layer belongs to another collection')
        index=self._items.index(item);self._items.remove(item);item._valid=False
        if index<self._active:self._active-=1
        elements=self._bm.verts if self._kind=='shape' else (loop for face in self._bm.faces for loop in face.loops)
        for element in elements:element._layers.pop(item,None)
def _bm_layer_value(element,layer,value=_UNSET):
    element._check()
    if not isinstance(layer,BMLayerItem):raise TypeError('Expected BMLayerItem')
    layer._check();kind=layer._collection._kind
    if layer._collection._bm is not element._bm or (kind=='shape')!=isinstance(element,BMVert):raise ValueError('Layer belongs to another BMesh or element domain')
    size={'uv':2,'float_color':4,'shape':3}[kind]
    if value is not _UNSET:
        value=[f32(v) for v in value]
        if len(value)!=size or not all(math.isfinite(v) for v in value):raise ValueError('Layer value has invalid component count or nonfinite values')
        element._layers[layer]=value
    if layer not in element._layers:element._layers[layer]=([1.]*4 if kind=='float_color' else [0.]*size)
    return element._layers[layer]
class BMLoopUV(Strict):
    _path='bmesh.types.BMLoopUV'
    def __init__(self,loop,layer):self._loop,self._layer=loop,layer
    uv=property(lambda s:VectorView(lambda:_bm_layer_value(s._loop,s._layer),lambda v:_bm_layer_value(s._loop,s._layer,v),s._path+'.uv'),lambda s,v:_bm_layer_value(s._loop,s._layer,v))
class BMLoop(Strict):
    _path='bmesh.types.BMLoop'
    def __init__(self,face,vert,edge):self._face,self._bm,self._vert,self._edge,self._layers=face,face._bm,vert,edge,{}
    def _check(self):self._face._check()
    @property
    def vert(self):self._check();return self._vert
    @property
    def edge(self):self._check();return self._edge
    @property
    def face(self):self._check();return self._face
    def __getitem__(self,layer):
        _bm_layer_value(self,layer)
        if layer._collection._kind=='uv':return BMLoopUV(self,layer)
        return VectorView(lambda:_bm_layer_value(self,layer),lambda v:_bm_layer_value(self,layer,v),self._path+'.color')
    def __setitem__(self,layer,value):
        if layer._collection._kind=='uv':raise TypeError('Assign through loop[layer].uv')
        _bm_layer_value(self,layer,value)
def _bm_init_layers(bm):
    bm._uv_layers=BMLayerCollection(bm,'uv');bm._color_layers=BMLayerCollection(bm,'float_color');bm._shape_layers=BMLayerCollection(bm,'shape')
    bm._source_custom=None
    bm._loop_access=Namespace('bmesh.types.BMesh.loops',layers=Namespace('bmesh.types.BMesh.loops.layers',uv=bm._uv_layers,float_color=bm._color_layers))
def _bm_plain_topology(bm,path):
    bm._check()
    if len(bm._uv_layers) or len(bm._color_layers) or len(bm._shape_layers) or bm._source_custom is not None:
        raise UnsupportedError(path,'Topology-changing operators on editable custom layers are outside the verified subset; edit topology before adding layers')
def _bm_from_mesh(bm,mesh):
    bm._check()
    if not isinstance(mesh,Mesh):raise TypeError('Expected a Mesh')
    m=mesh._get()
    if any(m.get(k) for k in ('deform_weights','crease_edge','crease_vert','face_strength')):raise UnsupportedError(bm._path+'.from_mesh','BMesh deform, crease and face-strength domains are outside this layer subset')
    custom=bool(m['uv_layers'] or m['loop_normals'] or m['colors'] or m.get('shape_keys'))
    if custom and (len(bm.verts) or len(bm._uv_layers) or len(bm._color_layers) or len(bm._shape_layers)):raise UnsupportedError(bm._path+'.from_mesh','Custom-layer import requires an empty BMesh')
    if m['loop_normals'] and any(m['smooth']):raise UnsupportedError(bm._path+'.from_mesh','Packed-normal round trips require flat input faces')
    if m['loop_normals']:bm._source_custom=dict(vertices=m['vertices'],faces=m['faces'],normals=m['loop_normals'])
    uv=[bm._uv_layers.new(layer['name']) for layer in m['uv_layers']]
    bm._uv_layers._active=m.get('active_uv',0)
    color=bm._color_layers.new(m.get('color_attribute_name','Color')) if m['colors'] else None
    shape=[bm._shape_layers.new(key['name']) for key in m.get('shape_keys',[])]
    verts=[bm.verts.new(v) for v in m['vertices']]
    for i,v in enumerate(verts):
        for layer,key in zip(shape,m.get('shape_keys',[])):_bm_layer_value(v,layer,key['points'][i])
    for edge in m['edges']:bm.edges.new([verts[i] for i in edge])
    corner=0
    for i,face in enumerate(m['faces']):
        f=bm.faces.new([verts[j] for j in face]);f.material_index=m['material_indices'][i];f.smooth=m['smooth'][i]
        for loop in f.loops:
            for layer,data in zip(uv,m['uv_layers']):_bm_layer_value(loop,layer,data['data'][corner])
            if color:_bm_layer_value(loop,color,m['colors'][corner])
            corner+=1
    bm.normal_update()
def _bm_to_mesh(bm,mesh):
    bm._check()
    if not isinstance(mesh,Mesh):raise TypeError('Expected a Mesh')
    target=mesh._get()
    if any(target.get(k) for k in ('deform_weights','crease_edge','crease_vert','face_strength')):raise UnsupportedError(bm._path+'.to_mesh','Target has unsupported BMesh attribute domains')
    lookup={v:i for i,v in enumerate(bm.verts)}
    vertices=[list(v.co) for v in bm.verts];faces=[[lookup[v] for v in f.verts] for f in bm.faces]
    loops=[loop for face in bm.faces for loop in face.loops]
    data=dict(vertices=vertices,edges=[[lookup[v] for v in e.verts] for e in bm.edges],faces=faces,material_indices=[f.material_index for f in bm.faces],smooth=[f.smooth for f in bm.faces],uv_layers=[dict(name=layer.name,data=[list(_bm_layer_value(loop,layer)) for loop in loops]) for layer in bm._uv_layers],active_uv=min(bm._uv_layers._active,max(0,len(bm._uv_layers)-1)),loop_normals=[],colors=[])
    if len(bm._color_layers):
        layer=bm._color_layers.active;data['color_attribute_name']=layer.name;data['colors']=[list(_bm_layer_value(loop,layer)) for loop in loops]
    if bm._source_custom is not None:
        src=bm._source_custom
        if src['vertices']!=vertices or src['faces']!=faces:raise UnsupportedError(bm._path+'.to_mesh','Packed custom normals can round-trip only with unchanged geometry/topology; edit normals through Mesh.normals_split_custom_set')
        data['loop_normals']=src['normals']
    if target.get('shape_keys'):
        if not len(bm._shape_layers):raise UnsupportedError(bm._path+'.to_mesh','Target shape keys require imported shape layers')
        basis=bm._shape_layers.active
        keys=[]
        for layer in bm._shape_layers:
            points=[list(v.co) if layer is basis else [f32(f32(_bm_layer_value(v,layer)[k]+v.co[k])-_bm_layer_value(v,basis)[k]) for k in range(3)] for v in bm.verts]
            keys.append(dict(name=layer.name,points=points))
        data['shape_keys']=keys
    request('bmesh_publish',kind='meshes',id=mesh._id,mesh=data)
