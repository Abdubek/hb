"""Standalone editable topology. Mesh data is published through the Rust bridge."""
class BMElement(Strict):
    def __init__(self,bm):self._bm=bm;self._valid=True;self._index=-1;self._layers={}
    @property
    def is_valid(self):return self._valid and self._bm._valid
    def _check(self):
        if not self.is_valid:raise ReferenceError('BMesh element has been removed')
    @property
    def index(self):self._check();return self._index
    @index.setter
    def index(self,value):self._check();self._index=int(value)

class _BMAdjacency(Strict):
    def __init__(self,owner,kind):
        self._owner,self._kind=owner,kind
        self._path=owner._path+'.link_'+kind
    def _items(self):
        self._owner._check()
        field='verts' if isinstance(self._owner,BMVert) else 'edges'
        return [item for item in getattr(self._owner._bm,self._kind) if self._owner in getattr(item,field)]
    def __len__(self):return len(self._items())
    def __iter__(self):return iter(self._items())
    def __contains__(self,value):return value in self._items()
    def __getitem__(self,key):
        items=self._items()
        if isinstance(key,slice) and key.step is not None:raise TypeError('BMesh adjacency slices do not support a step')
        if not isinstance(key,(int,slice)):raise AttributeError('BMesh adjacency expects an integer or slice')
        return items[key]

class BMVert(BMElement):
    _path='bmesh.types.BMVert'
    def __init__(self,bm,co):super().__init__(bm);self._co=Vector(co);self._normal=Vector()
    @property
    def co(self):
        self._check()
        def get():self._check();return list(self._co)
        def set(v):self._check();self._co=Vector(v)
        return VectorView(get,set,self._path+'.co')
    @co.setter
    def co(self,value):
        self._check()
        if len(value)!=3:raise ValueError('Expected three coordinates')
        self._co=Vector(value)
    def __getitem__(self,layer):
        _bm_layer_value(self,layer)
        return VectorView(lambda:_bm_layer_value(self,layer),lambda v:_bm_layer_value(self,layer,v),self._path+'.shape')
    def __setitem__(self,layer,value):_bm_layer_value(self,layer,value)
    @property
    def link_edges(self):self._check();return _BMAdjacency(self,'edges')
    @property
    def link_faces(self):self._check();return _BMAdjacency(self,'faces')
class BMEdge(BMElement):
    _path='bmesh.types.BMEdge'
    def __init__(self,bm,verts):super().__init__(bm);self._verts=tuple(verts)
    @property
    def verts(self):self._check();return self._verts
    @property
    def link_faces(self):self._check();return _BMAdjacency(self,'faces')
class BMFace(BMElement):
    _path='bmesh.types.BMFace'
    def __init__(self,bm,verts,edges):
        super().__init__(bm);self._verts=tuple(verts);self._edges=tuple(edges);self._normal=Vector();self._material=0;self._smooth=False
        self._loops=tuple(BMLoop(self,v,e) for v,e in zip(verts,edges))
    @property
    def loops(self):
        self._check()
        if tuple(loop._vert for loop in self._loops)!=self._verts:self._loops=tuple(BMLoop(self,v,e) for v,e in zip(self._verts,self._edges))
        return self._loops
    @property
    def verts(self):self._check();return self._verts
    @property
    def edges(self):self._check();return self._edges
    @property
    def normal(self):self._check();return self._normal.copy()
    @property
    def material_index(self):self._check();return self._material
    @material_index.setter
    def material_index(self,v):self._check();self._material=max(0,min(32767,int(v)))
    @property
    def smooth(self):self._check();return self._smooth
    @smooth.setter
    def smooth(self,v):self._check();self._smooth=bool(v)

def _bm_face_normal(face):
    # Shift before summing cross products to avoid cancellation far from the origin.
    origin=face._verts[0]._co
    points=[tuple(float(v._co[k])-origin[k] for k in range(3)) for v in face._verts]
    n=[math.fsum(a[(k+1)%3]*b[(k+2)%3]-a[(k+2)%3]*b[(k+1)%3] for a,b in zip(points,points[1:]+points[:1])) for k in range(3)]
    length=math.sqrt(sum(x*x for x in n))
    return Vector([x/length for x in n]) if length else Vector()

class BMSequence(Strict):
    def __init__(self,bm,kind):self._bm=bm;self._kind=kind;self._items=[];self._lookup=False;self._path='bmesh.types.BMesh.'+kind
    @property
    def layers(self):
        self._bm._check()
        if self._kind!='verts':raise UnsupportedError(self._path+'.layers','Only vertex shape layers and loop UV/float-color layers are supported')
        return Namespace('bmesh.types.BMesh.verts.layers',shape=self._bm._shape_layers)
    def __len__(self):self._bm._check();return len(self._items)
    def __iter__(self):self._bm._check();return iter(self._items)
    def __getitem__(self,key):
        self._bm._check()
        if not isinstance(key,slice) and not self._lookup:raise IndexError('BMesh lookup table is outdated; call ensure_lookup_table()')
        return self._items[key]
    def ensure_lookup_table(self):self._bm._check();self._lookup=True
    def index_update(self):
        for i,v in enumerate(self):v.index=i
    def _vertices(self,values,n=None):
        values=tuple(values)
        if n and len(values)!=n:raise ValueError('Wrong number of vertices')
        if len(set(map(id,values)))!=len(values):raise ValueError('Vertices must be distinct')
        for v in values:
            if not isinstance(v,BMVert) or v._bm is not self._bm:raise ValueError('Vertex belongs to another BMesh')
            v._check()
        return values
    def new(self,value):
        self._bm._check()
        if self._kind=='verts':
            if len(value)!=3:raise ValueError('Expected three coordinates')
            result=BMVert(self._bm,value)
        elif self._kind=='edges':
            verts=self._vertices(value,2)
            if any(set(map(id,e.verts))==set(map(id,verts)) for e in self):raise ValueError('Edge already exists')
            result=BMEdge(self._bm,verts)
        else:
            verts=self._vertices(value)
            if len(verts)<3:raise ValueError('Face needs at least three vertices')
            if any(set(map(id,f.verts))==set(map(id,verts)) for f in self):raise ValueError('Face already exists')
            edges=[]
            for a,b in zip(verts,verts[1:]+verts[:1]):
                edge=next((e for e in self._bm.edges if set(map(id,e.verts))=={id(a),id(b)}),None)
                edges.append(edge if edge is not None else self._bm.edges.new((a,b)))
            result=BMFace(self._bm,verts,edges)
        self._items.append(result);self._lookup=False;return result
    def remove(self,value):
        self._bm._check()
        if value not in self._items:raise ValueError('Element is not in this sequence')
        if self._kind=='verts':
            for e in list(self._bm.edges):
                if value in e.verts:self._bm.edges.remove(e)
        elif self._kind=='edges':
            for f in list(self._bm.faces):
                if value in f.edges:self._bm.faces.remove(f)
        self._items.remove(value);value._valid=False;self._lookup=False
class BMesh(Strict):
    _path='bmesh.types.BMesh'
    def __init__(self,*,use_operators=True):
        self._valid=True;self._operators=bool(use_operators);_bm_init_layers(self)
        self._verts=BMSequence(self,'verts');self._edges=BMSequence(self,'edges');self._faces=BMSequence(self,'faces')
    def _check(self):
        if not self._valid:raise ReferenceError('BMesh has been freed')
    @property
    def verts(self):self._check();return self._verts
    @property
    def edges(self):self._check();return self._edges
    @property
    def faces(self):self._check();return self._faces
    @property
    def loops(self):self._check();return self._loop_access
    def free(self):
        self._check();self._valid=False
        for seq in (self._verts,self._edges,self._faces):seq._items.clear()
    def normal_update(self):
        self._check()
        for v in self.verts:v._normal=Vector()
        for f in self.faces:
            f._normal=_bm_face_normal(f)
            for v in f.verts:v._normal=v._normal+f._normal
        for v in self.verts:v._normal.normalize()
    def from_mesh(self,mesh):return _bm_from_mesh(self,mesh)
    def to_mesh(self,mesh):return _bm_to_mesh(self,mesh)

def _bm_verts(bm,verts):
    bm._check()
    if not bm._operators:raise ValueError('BMesh was created without operator support')
    values=list(verts)
    if len({id(v) for v in values})!=len(values):raise ValueError('verts contains a duplicate BMVert')
    for v in values:
        if not isinstance(v,BMVert) or v._bm is not bm:raise ValueError('Expected vertices from this BMesh')
        v._check()
    return values

def _bm_matrix(value,path):
    if value is _UNSET:return Matrix.Identity(4)
    if not isinstance(value,Matrix) or len(value) not in (3,4):raise TypeError(path+' requires a 3x3 or 4x4 Matrix')
    if not all(math.isfinite(v) for row in value for v in row):raise ValueError('Matrix components must be finite')
    return value.to_4x4()
def _bm_point(matrix,point):
    return [f32(f32(f32(f32(matrix[i][0]*point[0])+f32(matrix[i][1]*point[1]))+f32(matrix[i][2]*point[2]))+matrix[i][3]) for i in range(3)]
def _bm_matmul(a,b):
    return Matrix([[f32(f32(f32(f32(a[i][0]*b[0][j])+f32(a[i][1]*b[1][j]))+f32(a[i][2]*b[2][j]))+f32(a[i][3]*b[3][j])) for j in range(4)] for i in range(4)])
def _bm_edit_transform(bm,verts,matrix,space,use_shapekey,path):
    values=_bm_verts(bm,verts)

    space=_bm_matrix(space,path+'.space')
    try:inverse=space.inverted()
    except ValueError:raise UnsupportedError(path+'(space=...)','Transform space must be nonsingular.') from None
    combined=_bm_matmul(_bm_matmul(inverse,matrix),space)
    points=[_bm_point(combined,v.co) for v in values]
    if not all(math.isfinite(x) for p in points for x in p):raise ValueError('Transform output must be finite')
    shapes=[(vertex,layer,_bm_point(combined,_bm_layer_value(vertex,layer))) for vertex in values for layer in bm._shape_layers] if use_shapekey else []
    if not all(math.isfinite(x) for _,_,point in shapes for x in point):raise ValueError('Shape transform output must be finite')
    for vertex,point in zip(values,points):vertex.co=point
    for vertex,layer,point in shapes:_bm_layer_value(vertex,layer,point)

def bm_translate(bm,*,vec=(0,0,0),verts=(),space=_UNSET,use_shapekey=False):
    matrix=Matrix.Translation(vec)
    return _bm_edit_transform(bm,verts,matrix,space,use_shapekey,'bmesh.ops.translate')
def bm_scale(bm,*,vec=(0,0,0),verts=(),space=_UNSET,use_shapekey=False):
    vec=Vector(vec)
    if len(vec)!=3:raise ValueError('Expected 3D scale')
    matrix=Matrix.Diagonal((*vec,1))
    return _bm_edit_transform(bm,verts,matrix,space,use_shapekey,'bmesh.ops.scale')
def bm_transform(bm,*,matrix=_UNSET,verts=(),space=_UNSET,use_shapekey=False):
    matrix=_bm_matrix(matrix,'bmesh.ops.transform.matrix')
    return _bm_edit_transform(bm,verts,matrix,space,use_shapekey,'bmesh.ops.transform')
def bm_rotate(bm,*,cent=(0,0,0),matrix=_UNSET,verts=(),space=_UNSET,use_shapekey=False):
    matrix=_bm_matrix(matrix,'bmesh.ops.rotate.matrix');cent=Vector(cent)
    if len(cent)!=3:raise ValueError('Expected 3D center')
    matrix=_bm_matmul(_bm_matmul(Matrix.Translation(cent),matrix),Matrix.Translation(-cent))
    return _bm_edit_transform(bm,verts,matrix,space,use_shapekey,'bmesh.ops.rotate')
def bm_delete(bm,*,geom,context='VERTS'):
    _bm_plain_topology(bm,'bmesh.ops.delete')
    bm._check()
    if not bm._operators:raise ValueError('BMesh was created without operator support')
    kinds={'VERTS':('verts',BMVert),'EDGES':('edges',BMEdge),'FACES_ONLY':('faces',BMFace)}
    if context not in kinds:raise UnsupportedError('bmesh.ops.delete(context='+repr(context)+')','Supported contexts: VERTS, EDGES, FACES_ONLY')
    kind,cls=kinds[context];values=list(geom)
    for v in values:
        if not isinstance(v,cls) or v._bm is not bm:raise ValueError('Incorrect geometry for delete context')
        v._check()
    endpoints={v for e in values for v in e.verts} if context=='EDGES' else set()
    for v in values:
        if v.is_valid:getattr(bm,kind).remove(v)
    for v in endpoints:
        if v.is_valid and not any(v in e.verts for e in bm.edges):bm.verts.remove(v)
    return {}

install_module('bmesh',dict(new=BMesh,types=Namespace('bmesh.types',BMesh=BMesh,BMVert=BMVert,BMEdge=BMEdge,BMFace=BMFace),ops=Namespace('bmesh.ops',translate=bm_translate,scale=bm_scale,rotate=bm_rotate,transform=bm_transform,delete=bm_delete)))

# Primitive builders append to the editable topology and return new vertices.
def _bm_primitive_options(bm,path,matrix,calc_uvs):
    bm._check()
    if not bm._operators:raise ValueError('BMesh was created without operator support')
    matrix=_bm_matrix(matrix,path+'.matrix')
    if calc_uvs:raise UnsupportedError(path+'(calc_uvs=True)','Construction-time UV generation is a separate primitive contract; editable UV layers are available')
    return matrix

def bm_create_cube(bm,*,size=0.,matrix=_UNSET,calc_uvs=False):
    matrix=_bm_primitive_options(bm,'bmesh.ops.create_cube',matrix,calc_uvs)
    size=f32(size);half=f32(size*.5)
    points=[_bm_point(matrix,(x*half,y*half,z*half)) for x,y,z in ((-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1))]
    verts=[bm.verts.new(point) for point in points]
    for face in ((0,1,3,2),(2,3,7,6),(6,7,5,4),(4,5,1,0),(2,6,4,0),(7,3,1,5)):bm.faces.new([verts[i] for i in face])
    return {'verts':verts}

def bm_create_grid(bm,*,x_segments=0,y_segments=0,size=0.,matrix=_UNSET,calc_uvs=False):
    matrix=_bm_primitive_options(bm,'bmesh.ops.create_grid',matrix,calc_uvs)
    x=max(1,int(x_segments));y=max(1,int(y_segments));size=f32(size)
    if (x+1)*(y+1)>100000:raise UnsupportedError('bmesh.ops.create_grid','Editable grid limit is 100,000 vertices; reduce segment counts.')
    points=[_bm_point(matrix,(f32(f32(-1+f32(2*i/x))*size),f32(f32(-1+f32(2*j/y))*size),0)) for j in range(y+1) for i in range(x+1)]
    verts=[bm.verts.new(point) for point in points]
    for j in range(y):
        for i in range(x):
            a=j*(x+1)+i;bm.faces.new([verts[k] for k in (a,a+1,a+x+2,a+x+1)])
    return {'verts':verts}

sys.modules['bmesh'].ops._values.update(create_cube=bm_create_cube,create_grid=bm_create_grid)

def _bm_append_geometry(bm,vertices,edges,faces):
    # All vertices are fresh, so local edge keys cannot collide with old topology.
    verts=[bm.verts.new(v) for v in vertices];known={}
    def edge(a,b):
        key=(min(a,b),max(a,b))
        if key not in known:
            e=BMEdge(bm,(verts[a],verts[b]));bm._edges._items.append(e);known[key]=e
        return known[key]
    for a,b in edges:edge(a,b)
    for f in faces:
        es=[edge(a,b) for a,b in zip(f,f[1:]+f[:1])]
        bm._faces._items.append(BMFace(bm,tuple(verts[i] for i in f),es))
    bm._edges._lookup=False;bm._faces._lookup=False
    return {'verts':verts}

def bm_create_uvsphere(bm,*,u_segments=0,v_segments=0,radius=0.,matrix=_UNSET,calc_uvs=False):
    matrix=_bm_primitive_options(bm,'bmesh.ops.create_uvsphere',matrix,calc_uvs)
    n=int(u_segments);rings=int(v_segments);r=_construction_float(radius)
    if n<3 or rings<3:raise UnsupportedError('bmesh.ops.create_uvsphere','Use at least three u_segments and v_segments.')
    v,e,f,uv=_sphere_geometry(n,rings,r)
    return _bm_append_geometry(bm,[_bm_point(matrix,point) for point in v],e,f)

def bm_create_cone(bm,*,cap_ends=False,cap_tris=False,segments=0,radius1=0.,radius2=0.,depth=0.,matrix=_UNSET,calc_uvs=False):
    matrix=_bm_primitive_options(bm,'bmesh.ops.create_cone',matrix,calc_uvs)
    n=int(segments);r1,r2,d=[_construction_float(v) for v in (radius1,radius2,depth)]
    if n<3 or r1<0 or r2<0 or d<0:raise UnsupportedError('bmesh.ops.create_cone','Use at least three segments and nonnegative radii/depth.')
    fill='TRIFAN' if cap_ends and cap_tris else 'NGON' if cap_ends else 'NOTHING'
    v,e,f,uv=_cone_geometry(n,r1,r2,d,fill)
    return _bm_append_geometry(bm,[_bm_point(matrix,point) for point in v],e,f)

def bm_create_circle(bm,*,cap_ends=False,cap_tris=False,segments=0,radius=0.,matrix=_UNSET,calc_uvs=False):
    matrix=_bm_primitive_options(bm,'bmesh.ops.create_circle',matrix,calc_uvs)
    n=int(segments);r=_construction_float(radius)
    if n<3 or n>100000 or r<=0:raise UnsupportedError('bmesh.ops.create_circle','Use 3..100,000 segments and a positive radius.')
    v=[(x,y,0) for x,y in _ring(n,r,True)];e=[];f=[]
    if cap_ends and cap_tris:
        v.insert(0,(0,0,0));f=[[0,i+1,(i+1)%n+1] for i in range(n)]
    elif cap_ends:f=[list(range(n))]
    else:e=[[i,(i+1)%n] for i in range(n)]
    return _bm_append_geometry(bm,[_bm_point(matrix,point) for point in v],e,f)

sys.modules['bmesh'].ops._values.update(create_uvsphere=bm_create_uvsphere,create_cone=bm_create_cone,create_circle=bm_create_circle)


def bm_extrude_face_region(bm,*,geom=(),edges_exclude=(),use_keep_orig=False,use_normal_flip=False,use_normal_from_adjacent=False,use_dissolve_ortho_edges=False,use_select_history=False):
    _bm_plain_topology(bm,'bmesh.ops.extrude_face_region')
    bm._check()
    if not bm._operators:raise ValueError('BMesh was created without operator support')
    path='bmesh.ops.extrude_face_region'
    if edges_exclude or use_normal_flip or use_normal_from_adjacent or use_dissolve_ortho_edges or use_select_history:
        raise UnsupportedError(path,'This subset supports mixed vertices/edges/faces, no excluded edges, and default winding/adjacent-normal/dissolve/history options.')
    geom=list(geom)
    if any(isinstance(value,(BMVert,BMEdge)) for value in geom):return _bm_extrude_mixed(bm,geom,use_keep_orig)
    selected=set()
    for face in geom:
        if not isinstance(face,BMFace):raise UnsupportedError(path,'Pass faces only; mixed vertex/edge input and wire extrusion are not implemented.')
        if face._bm is not bm:raise ValueError('Face belongs to another BMesh')
        face._check();selected.add(face)
    if not selected:return {'geom':[]}
    faces=[f for f in bm.faces if f in selected]
    # Face order and first encountered corners define stable duplicate indices.
    vertices={};edge_faces={}
    for face in faces:
        for v in face.verts:vertices.setdefault(v,None)
        for i,e in enumerate(face.edges):edge_faces.setdefault(e,[]).append((face,face.verts[i],face.verts[(i+1)%len(face.verts)]))
    boundary=[];degree={}
    for edge,uses in edge_faces.items():
        if len(uses)>2 or (len(uses)==2 and uses[0][1:]==uses[1][1:]):
            raise UnsupportedError(path,'Selected faces must form a consistently oriented manifold region.')
        if len(uses)==1:
            boundary.append((edge,uses[0]))
            for v in edge.verts:degree[v]=degree.get(v,0)+1
    if any(n!=2 for n in degree.values()):raise UnsupportedError(path,'Region boundaries must be separate closed loops without shared corner junctions.')
    if len(bm.verts)+len(vertices)>100000 or len(bm.faces)+len(faces)+len(boundary)>100000:
        raise UnsupportedError(path,'Editable extrusion limit is 100,000 vertices/faces; reduce the region or extrusion count.')
    for v in vertices:vertices[v]=bm.verts.new(v.co)
    new_edges={}
    for edge in edge_faces:
        new=BMEdge(bm,tuple(vertices[v] for v in edge.verts));bm._edges._items.append(new);new_edges[edge]=new
    caps=[]
    for face in faces:
        cap=BMFace(bm,tuple(vertices[v] for v in face.verts),tuple(new_edges[e] for e in face.edges))
        cap._material=face._material;cap._smooth=face._smooth;cap._normal=face._normal.copy()
        bm._faces._items.append(cap);caps.append(cap)
    # The face-only Blender operator retains and reverses the original caps,
    # including when use_keep_orig=False. Mixed geometry has different semantics.
    for face in faces:
        face._verts=(face._verts[0],)+tuple(reversed(face._verts[1:]))
        face._edges=tuple(reversed(face._edges));face._normal=-face._normal
    edges={frozenset(e.verts):e for e in bm.edges}
    def wall_edge(a,b):
        key=frozenset((a,b))
        if key not in edges:
            edges[key]=BMEdge(bm,(a,b));bm._edges._items.append(edges[key])
        return edges[key]
    # Unlike Blender's hash-dependent order, walls follow original edge order.
    edge_order={e:i for i,e in enumerate(bm.edges)}
    boundary.sort(key=lambda item:edge_order[item[0]])
    for edge,(source,a,b) in boundary:
        vs=(a,b,vertices[b],vertices[a])
        es=tuple(wall_edge(x,y) for x,y in zip(vs,vs[1:]+vs[:1]))
        face=BMFace(bm,vs,es);face._material=source._material;face._smooth=source._smooth
        bm._faces._items.append(face)
    bm._edges._lookup=False;bm._faces._lookup=False
    return {'geom':list(vertices.values())+list(new_edges.values())+caps}

sys.modules['bmesh'].ops._values['extrude_face_region']=bm_extrude_face_region

def bm_recalc_face_normals(bm,*,faces=()):
    _bm_plain_topology(bm,'bmesh.ops.recalc_face_normals')
    bm._check()
    if not bm._operators:raise ValueError('BMesh was created without operator support')
    path='bmesh.ops.recalc_face_normals';values=list(faces)
    for face in values:
        if not isinstance(face,BMFace) or face._bm is not bm:raise ValueError('Expected faces from this BMesh')
        face._check()
    selected=set(values);requested=set(values)
    if len(selected)!=len(values):raise ValueError('faces: found the same (BMFace) used multiple times')
    if len(bm.verts)>100000 or len(bm.faces)>100000:raise UnsupportedError(path,'Normal repair is limited to 100,000 vertices/faces.')
    if not all(math.isfinite(x) for v in bm.verts for x in v._co):raise ValueError('Normal repair requires finite coordinates')
    # Plan every component before changing handles, winding or cached normals.
    edge_faces={};vertex_faces={}
    for face in bm.faces:
        for v in face._verts:vertex_faces.setdefault(v,set()).add(face)
        for edge,a in zip(face._edges,face._verts):edge_faces.setdefault(edge,[]).append((face,a is edge._verts[0]))
    pending=list(selected)
    while pending:
        for edge in pending.pop().edges:
            for face,_ in edge_faces[edge]:
                if face not in selected:selected.add(face);pending.append(face)
    adjacent={f:[] for f in selected};vertex_links={}
    for face in selected:
        for edge in face._edges:
            linked=edge_faces[edge]
            if len(linked)>2:raise UnsupportedError(path,'Non-manifold edges are outside the normal-repair subset')
            if len(linked)==1:continue
            (a,ad),(b,bd)=linked
            adjacent[face].append((b if a is face else a,ad==bd))
            for v in edge._verts:
                links=vertex_links.setdefault(v,{})
                links.setdefault(a,set()).add(b);links.setdefault(b,set()).add(a)
    flips={}
    for seed in bm.faces:
        if seed not in selected or seed in flips:continue
        flips[seed]=False;component=[];pending=[seed]
        while pending:
            face=pending.pop();component.append(face)
            for other,invert in adjacent[face]:
                expected=flips[face]^invert
                if other in flips:
                    if flips[other]!=expected:raise UnsupportedError(path,'Non-orientable components cannot be repaired by this subset.')
                else:flips[other]=expected;pending.append(other)
        component_set=set(component);verts={v for f in component for v in f._verts}
        if any(not vertex_faces[v]<=component_set for v in verts):
            raise UnsupportedError(path,'Components sharing only a vertex are non-manifold; split the shared vertex first.')
        for v in verts:
            links={f:set(vertex_links.get(v,{}).get(f,())) for f in vertex_faces[v]};seen=set();pending=[next(iter(links))]
            while pending:
                face=pending.pop()
                if face in seen:continue
                seen.add(face);pending.extend(links[face]-seen)
            if len(seen)!=len(vertex_faces[v]):
                raise UnsupportedError(path,'A vertex has disconnected face fans; split the non-manifold vertex first.')
        coords={v:tuple(v._co) for v in verts}
        if not all(math.isfinite(x) for p in coords.values() for x in p):raise ValueError('Normal repair requires finite coordinates')
        lo=[min(p[k] for p in coords.values()) for k in range(3)]
        extent=max(max(p[k] for p in coords.values())-lo[k] for k in range(3))
        if not extent:raise UnsupportedError(path,'Zero-volume or collapsed components are unsupported.')
        # Normalize component coordinates: signed volume is independent of position and scale.
        points={v:tuple((p[k]-lo[k])/extent for k in range(3)) for v,p in coords.items()}
        volumes=[]
        for face in component:
            ps=[points[v] for v in face._verts];a=ps[0]
            normal=[math.fsum((b[(k+1)%3]-a[(k+1)%3])*(c[(k+2)%3]-a[(k+2)%3])-(b[(k+2)%3]-a[(k+2)%3])*(c[(k+1)%3]-a[(k+1)%3]) for b,c in zip(ps[1:-1],ps[2:])) for k in range(3)]
            length=math.sqrt(sum(x*x for x in normal))
            if length<=1e-12:raise UnsupportedError(path,'Degenerate faces are unsupported; remove zero-area faces first.')
            if any(abs(sum((p[k]-a[k])*normal[k] for k in range(3)))>1e-6*length for p in ps):
                raise UnsupportedError(path,'Non-planar polygons are unsupported; triangulate them before normal repair.')
            for b,c in zip(ps[1:-1],ps[2:]):
                term=sum(a[k]*(b[(k+1)%3]*c[(k+2)%3]-b[(k+2)%3]*c[(k+1)%3]) for k in range(3))
                volumes.append(-term if flips[face] else term)
        volume=math.fsum(volumes)
        is_open=any(len(edge_faces[e])==1 for f in component for e in f.edges)
        if not is_open and abs(volume)<=1e-10:raise UnsupportedError(path,'Near-zero signed volume is ambiguous; use a non-degenerate closed solid.')
        if is_open:
            anchor,reverse=_bm_open_normal_seed(component)
            if flips[anchor]!=reverse:
                for face in component:flips[face]=not flips[face]
        elif volume<0:
            for face in component:flips[face]=not flips[face]
    for face,flip in flips.items():
        if flip and face in requested:
            face._verts=(face._verts[0],)+tuple(reversed(face._verts[1:]))
            face._edges=tuple(reversed(face._edges))
    # Blender refreshes all face normals, including unselected geometry and empty selections.
    bm.normal_update()
    bm.verts.index_update();bm.edges.index_update();bm.faces.index_update()
    return None

sys.modules['bmesh'].ops._values['recalc_face_normals']=bm_recalc_face_normals

def bm_inset_region(bm,*,faces=(),faces_exclude=(),use_boundary=False,use_even_offset=False,use_interpolate=False,use_relative_offset=False,use_edge_rail=False,thickness=0.,depth=0.,use_outset=False):
    _bm_plain_topology(bm,'bmesh.ops.inset_region')
    bm._check();path='bmesh.ops.inset_region'
    if not bm._operators:raise ValueError('BMesh was created without operator support')
    if faces_exclude or use_relative_offset or use_edge_rail or use_outset:raise UnsupportedError(path,'Use planar regions with default exclusion, relative-offset, edge-rail and outset flags.')
    thickness,depth=f32(thickness),f32(depth)
    if not math.isfinite(thickness) or not math.isfinite(depth):raise ValueError('Inset distances must be finite')
    selected=set(faces)
    for face in selected:
        if not isinstance(face,BMFace) or face._bm is not bm:raise ValueError('Expected faces from this BMesh')
        face._check()
    ordered=[face for face in bm.faces if face in selected]
    if not ordered:return {'faces':[]}
    # Each connected planar region may have holes, but no branched boundary.
    uses={};all_uses={};vertices={}
    for face in bm.faces:
        for edge in face.edges:all_uses.setdefault(edge,[]).append(face)
    for face in ordered:
        normal=_bm_face_normal(face)
        if normal.length<.5:raise UnsupportedError(path,'Inset requires nondegenerate planar faces.')
        origin=face.verts[0].co;extent=max((v.co-origin).length for v in face.verts)
        if any(abs((v.co-origin).dot(normal))>1e-5*extent for v in face.verts):raise UnsupportedError(path,'Triangulate nonplanar faces before inset.')
        for vertex in face.verts:vertices.setdefault(vertex,[]).append(normal)
        for i,edge in enumerate(face.edges):uses.setdefault(edge,[]).append((face,face.verts[i],face.verts[(i+1)%len(face.verts)],normal))
    boundary=[];inward={}
    for edge,regions in uses.items():
        if len(all_uses[edge])>2:raise UnsupportedError(path,'Inset edges must be manifold.')
        if len(regions)>2 or (len(regions)==2 and regions[0][3].dot(regions[1][3])<1-1e-5):raise UnsupportedError(path,'Selected regions must be consistently oriented and coplanar.')
        if len(regions)==1 and (use_boundary or len(all_uses[edge])>1):
            face,a,b,normal=regions[0];direction=(b.co-a.co).normalized()
            if direction.length<.5:raise UnsupportedError(path,'Zero-length boundary edge')
            n=normal.cross(direction);boundary.append((edge,face,a,b))
            inward.setdefault(a,[]).append(n);inward.setdefault(b,[]).append(n)
    if any(len(values)!=2 for values in inward.values()):raise UnsupportedError(path,'Inset boundaries must be closed loops without shared junctions.')
    points={}
    for vertex,normals in vertices.items():
        normal=sum(normals,Vector()).normalized();delta=normal*depth
        if vertex in inward:
            a,b=inward[vertex];offset=a+b
            if use_even_offset:
                divisor=1+a.dot(b)
                if divisor<1e-6:raise UnsupportedError(path,'Inset corner has an ambiguous miter')
                offset=offset/divisor
            else:offset.normalize()
            delta=delta+offset*thickness
        points[vertex]=vertex.co+delta
    for face in ordered:
        for a,b in zip(face.verts,face.verts[1:]+face.verts[:1]):
            if (points[b]-points[a]).dot(b.co-a.co)<=0:raise UnsupportedError(path,'Inset thickness collapses an edge; reduce thickness.')
    if len(bm.verts)+len(inward)>100000 or len(bm.faces)+len(boundary)>100000:raise UnsupportedError(path,'Inset limit is 100,000 vertices/faces.')
    mapped={v:bm.verts.new(points[v]) if v in inward else v for v in vertices}
    for vertex in vertices:
        if vertex not in inward:vertex.co=points[vertex]
    for edge,regions in uses.items():
        if len(regions)==2:edge._verts=tuple(mapped[v] for v in edge.verts)
    edges={frozenset(e.verts):e for e in bm.edges}
    def edge_for(a,b):
        key=frozenset((a,b))
        if key not in edges:edges[key]=bm.edges.new((a,b))
        return edges[key]
    for face in ordered:
        face._verts=tuple(mapped[v] for v in face.verts)
        face._edges=tuple(edge_for(a,b) for a,b in zip(face.verts,face.verts[1:]+face.verts[:1]))
    result=[]
    for edge,source,a,b in boundary:
        face=bm.faces.new((a,b,mapped[b],mapped[a]));face.material_index=source.material_index;face.smooth=source.smooth;result.append(face)
    bm.normal_update();bm._edges._lookup=False;bm._faces._lookup=False
    return {'faces':result}

sys.modules['bmesh'].ops._values['inset_region']=bm_inset_region

def bm_bevel(bm,*,geom=(),offset=0.,offset_type='OFFSET',segments=1,profile=.5,affect='EDGES',clamp_overlap=False,loop_slide=True,material=-1,harden_normals=False):
    _bm_plain_topology(bm,'bmesh.ops.bevel')
    bm._check();path='bmesh.ops.bevel'
    if not bm._operators:raise ValueError('BMesh was created without operator support')
    values=list(geom);offset=f32(offset);segments=max(1,int(segments))
    for value in values:
        if not isinstance(value,(BMVert,BMEdge,BMFace)) or value._bm is not bm:raise ValueError('Geometry belongs to another BMesh')
        value._check()
    if not values or offset==0:return {'faces':[],'edges':[],'verts':[]}
    if not math.isfinite(offset) or offset<0:raise ValueError('Bevel offset must be finite and nonnegative')
    if affect!='EDGES' or offset_type!='OFFSET' or profile!=.5 or segments>8 or clamp_overlap or not loop_slide or material!=-1 or harden_normals:raise UnsupportedError(path,'Complete closed convex mesh edges, OFFSET, profile 0.5, segments 1..8, default material/normals, no overlap clamping.')
    edges={value for value in values if isinstance(value,BMEdge)}
    if edges!=set(bm.edges):raise UnsupportedError(path,'Select every edge of the closed convex mesh.')
    vertices=list(bm.verts);faces=list(bm.faces);lookup={v:i for i,v in enumerate(vertices)}
    source=dict(vertices=[list(v.co) for v in vertices],faces=[[lookup[v] for v in face.verts] for face in faces],material_indices=[face.material_index for face in faces],smooth=[face.smooth for face in faces])
    result=request('bmesh_bevel',mesh=source,width=offset,segments=segments)
    planes=[(face.verts[0].co,_bm_face_normal(face)) for face in faces]
    # Validate/build independently before invalidating the original handles.
    replacement=BMesh()
    new_vertices=[replacement.verts.new(co) for co in result['vertices']]
    for i,indices in enumerate(result['faces']):
        face=replacement.faces.new([new_vertices[j] for j in indices]);face.material_index=result['material_indices'][i];face.smooth=result['smooth'][i]
    replacement.normal_update()
    caps=set()
    for origin,normal in planes:
        # Several original faces can share a plane after triangulation. Exclude
        # every surviving inset face, not just one nearest face per plane.
        caps.update(face for face in replacement.faces if face.normal.dot(normal)>1-1e-5 and all(abs((v.co-origin).dot(normal))<1e-6 for v in face.verts))
    for sequence in (bm.verts,bm.edges,bm.faces):
        for value in sequence:value._valid=False
    for old,new in ((bm.verts,replacement.verts),(bm.edges,replacement.edges),(bm.faces,replacement.faces)):
        old._items=new._items;old._lookup=False
        for value in old._items:value._bm=bm
    return {'faces':[face for face in bm.faces if face not in caps],'edges':list(bm.edges),'verts':list(bm.verts)}

sys.modules['bmesh'].ops._values['bevel']=bm_bevel

def _bm_merge_targets(vertices,distance):
    # A balanced spatial partition supplies deterministic greedy representatives.
    # Float32 partition bounds are significant at exactly the requested radius.
    points=[tuple(v.co) for v in vertices];order=list(range(len(vertices)))
    axes=[0]*len(order);children={}
    def balance(start,stop,axis):
        if start==stop:return None
        if stop-start==1:return start
        middle=(start+stop)//2;low,high=start,stop-1
        while low<high:
            pivot=points[order[high]][axis];a,b=low,high-1
            while True:
                while points[order[a]][axis]<pivot:a+=1
                while b>low and points[order[b]][axis]>pivot:b-=1
                if a>=b:break
                order[a],order[b]=order[b],order[a];a+=1;b-=1
            order[a],order[high]=order[high],order[a]
            if a>=middle:high=a-1
            if a<=middle:low=a+1
        axes[middle]=axis
        children[middle]=(balance(start,middle,(axis+1)%3),balance(middle+1,stop,(axis+1)%3))
        return middle
    root=balance(0,len(order),0);targets=[-1]*len(order);radius2=f32(distance*distance)
    for seed in order:
        if targets[seed] not in (-1,seed):continue
        stack=[root];found=False
        while stack:
            node=stack.pop()
            if node is None:continue
            index=order[node];axis=axes[node];left,right=children.get(node,(None,None));a,b=points[seed],points[index]
            if f32(a[axis]+distance)<=b[axis]:stack.append(left);continue
            if f32(a[axis]-distance)>=b[axis]:stack.append(right);continue
            if index!=seed and targets[index]==-1:
                delta=[f32(x-y) for x,y in zip(a,b)]
                square=f32(f32(f32(delta[0]*delta[0])+f32(delta[1]*delta[1]))+f32(delta[2]*delta[2]))
                if square<=radius2:targets[index]=seed;found=True
            stack.extend((right,left))
        if found:targets[seed]=seed
    return {vertices[i]:vertices[target] for i,target in enumerate(targets) if target not in (-1,i)}

def _bm_weld(bm,mapping):
    if not mapping:return
    def target(vertex):return mapping.get(vertex,vertex)
    # Resolve all resulting polygon cycles before changing the editable mesh.
    plans=[]
    for face in bm.faces:
        if not any(v in mapping for v in face.verts):continue
        path=[];positions={};cycles=[]
        for vertex in [target(v) for v in face.verts]+[target(face.verts[0])]:
            if vertex in positions:
                start=positions[vertex];cycle=path[start:]
                if len(cycle)>=3:cycles.append(tuple(cycle))
                path=path[:start+1];positions={v:i for i,v in enumerate(path)}
            else:positions[vertex]=len(path);path.append(vertex)
        plans.append((face,cycles))
    edges={frozenset(e.verts):e for e in bm.edges if all(v not in mapping for v in e.verts)}
    created_edges=[]
    for edge in list(bm.edges):
        if all(v not in mapping for v in edge.verts):continue
        a,b=map(target,edge.verts);edge._valid=False
        key=frozenset((a,b))
        if a is not b and key not in edges:edges[key]=BMEdge(bm,(a,b));created_edges.append(edges[key])
    faces={frozenset(f.verts):f for f in bm.faces if all(v not in mapping for v in f.verts)}
    created_faces=[]
    for face,cycles in plans:
        retained=False
        for cycle in cycles:
            key=frozenset(cycle)
            if key in faces:continue
            boundary=tuple(edges[frozenset((a,b))] for a,b in zip(cycle,cycle[1:]+cycle[:1]))
            if not retained:
                result=face;result._verts=cycle;result._edges=boundary;retained=True
            else:
                result=BMFace(bm,cycle,boundary);result._material=face._material;result._smooth=face._smooth;created_faces.append(result)
            faces[key]=result
        if not retained:face._valid=False
    for vertex in mapping:vertex._valid=False
    bm._verts._items=[v for v in bm._verts._items if v._valid]
    bm._edges._items=[e for e in bm._edges._items if e._valid]+created_edges
    bm._faces._items=[f for f in bm._faces._items if f._valid]+created_faces
    for sequence in (bm.verts,bm.edges,bm.faces):sequence._lookup=False
    bm.normal_update()

def bm_remove_doubles(bm,*,verts=(),dist=0.):
    _bm_plain_topology(bm,'bmesh.ops.remove_doubles')
    vertices=_bm_verts(bm,verts);distance=f32(dist)
    if not math.isfinite(distance) or distance<0:raise ValueError('Merge distance must be finite and nonnegative')
    if not all(math.isfinite(x) for v in vertices for x in v.co):raise ValueError('Merge coordinates must be finite')
    if distance and vertices:_bm_weld(bm,_bm_merge_targets(vertices,distance))
    return None

sys.modules['bmesh'].ops._values['remove_doubles']=bm_remove_doubles

def bm_subdivide_edges(bm,*,edges=(),cuts=0,use_grid_fill=False,smooth=0.,fractal=0.,along_normal=0.,seed=0,quad_corner_type='STRAIGHT_CUT',use_single_edge=False,use_only_quads=False):
    _bm_plain_topology(bm,'bmesh.ops.subdivide_edges')
    bm._check();path='bmesh.ops.subdivide_edges'
    if not bm._operators:raise ValueError('BMesh was created without operator support')
    selected=set(edges);cuts=int(cuts)
    for edge in selected:
        if not isinstance(edge,BMEdge) or edge._bm is not bm:raise ValueError('Expected edges from this BMesh')
        edge._check()
    if cuts<0 or cuts>64:raise UnsupportedError(path,'Use cuts in 0..64.')
    if smooth or fractal or along_normal or quad_corner_type!='STRAIGHT_CUT' or use_single_edge or use_only_quads:raise UnsupportedError(path,'Linear subdivision, STRAIGHT_CUT corners, default single-edge/quad-only flags.')
    ordered=[edge for edge in bm.edges if edge in selected]
    affected=[face for face in bm.faces if any(e in selected for e in face.edges)]
    if not cuts:return {'geom_inner':[],'geom_split':[],'geom':ordered+affected}
    steps=cuts+1;plans=[]
    for face in affected:
        indices=[i for i,e in enumerate(face.edges) if e in selected];count=len(face.verts)
        if len(indices)==count and use_grid_fill and count in (3,4):kind='grid'
        elif count==4 and len(indices)==2 and any((i+1)%4 in indices for i in indices):kind='corner'
        elif len(indices) in (1,count) and not use_grid_fill:kind='ring'
        else:raise UnsupportedError(path,'Use complete triangle/quad grid boundaries, unfilled whole/one-edge boundaries, adjacent quad corner pairs or wire edges.')
        plans.append((face,tuple(face.verts),tuple(face.edges),kind))
    if len(bm.verts)+len(ordered)*cuts+len(plans)*cuts*cuts>100000 or len(bm.faces)+len(plans)*steps*steps>100000:raise UnsupportedError(path,'Subdivision limit is 100,000 vertices/faces.')
    if any(not math.isfinite(x) or abs(x)>1e30 for edge in ordered for v in edge.verts for x in v.co):raise ValueError('Subdivision coordinates must be finite and within 1e30')
    chains={};split_vertices=[];split_edges=[]
    for edge in ordered:
        a,b=edge.verts
        middle=[bm.verts.new(a.co*(1-i/steps)+b.co*(i/steps)) for i in range(1,steps)]
        chain=[a]+middle+[b];chains[edge]=chain;split_vertices.extend(middle)
        edge._verts=(chain[-2],chain[-1]);pieces=[]
        for a,b in zip(chain[:-2],chain[1:-1]):
            piece=BMEdge(bm,(a,b));bm._edges._items.append(piece);pieces.append(piece)
        split_edges.extend(pieces+[edge])
    edge_map={frozenset(edge.verts):edge for edge in bm.edges};inner_edges=[];inner_vertices=[];inner_faces=[];tagged_faces=[]
    def edge_for(a,b):
        key=frozenset((a,b))
        if key not in edge_map:
            edge_map[key]=BMEdge(bm,(a,b));bm._edges._items.append(edge_map[key]);inner_edges.append(edge_map[key])
        return edge_map[key]
    def oriented(edge,start):
        chain=chains.get(edge,list(edge.verts))
        return chain if chain[0] is start else list(reversed(chain))
    def install(face,cycle):
        face._verts=tuple(cycle);face._edges=tuple(edge_for(a,b) for a,b in zip(face.verts,face.verts[1:]+face.verts[:1]))
    for face,vertices,boundary,kind in plans:
        sequences=[oriented(edge,vertices[i]) for i,edge in enumerate(boundary)]
        if kind=='ring':
            install(face,[v for sequence in sequences for v in sequence[:-1]]);tagged_faces.append(face);continue
        if kind=='corner':
            indices=[i for i,e in enumerate(boundary) if e in selected]
            start=next(i for i in indices if (i+1)%4 in indices)
            first,second=sequences[start],sequences[(start+1)%4]
            pairs=[(first[-1-i],second[i]) for i in range(1,steps)]
            polygons=[(pairs[0][0],vertices[(start+1)%4],pairs[0][1])]
            polygons.extend((a,pa,pb,b) for (pa,pb),(a,b) in zip(pairs,pairs[1:]))
            install(face,(*pairs[-1],vertices[(start+2)%4],vertices[(start+3)%4],vertices[start]))
            tagged_faces.append(face)
            for polygon in polygons:
                created=BMFace(bm,polygon,tuple(edge_for(a,b) for a,b in zip(polygon,polygon[1:]+polygon[:1])));created._material=face._material;created._smooth=face._smooth;bm._faces._items.append(created)
            continue
        grid={};polygons=[]
        if len(vertices)==4:
            for i in range(steps+1):
                grid[i,0]=sequences[0][i];grid[steps,i]=sequences[1][i];grid[steps-i,steps]=sequences[2][i];grid[0,steps-i]=sequences[3][i]
            a,b,c,d=[v.co for v in vertices]
            for j in range(1,steps):
                for i in range(1,steps):
                    u,v=i/steps,j/steps;vertex=bm.verts.new(a*((1-u)*(1-v))+b*(u*(1-v))+c*(u*v)+d*((1-u)*v));grid[i,j]=vertex;inner_vertices.append(vertex)
            polygons=[(grid[i,j],grid[i+1,j],grid[i+1,j+1],grid[i,j+1]) for j in range(steps) for i in range(steps)]
            original=polygons.pop()
        else:
            for i in range(steps+1):grid[i,0]=sequences[0][i];grid[steps-i,i]=sequences[1][i];grid[0,steps-i]=sequences[2][i]
            a,b,c=[v.co for v in vertices]
            for j in range(1,steps):
                for i in range(1,steps-j):
                    vertex=bm.verts.new(a*(1-(i+j)/steps)+b*(i/steps)+c*(j/steps));grid[i,j]=vertex;inner_vertices.append(vertex)
            for j in range(steps):
                for i in range(steps-j):
                    polygons.append((grid[i,j],grid[i+1,j],grid[i,j+1]))
                    if i+j<steps-1:polygons.append((grid[i+1,j],grid[i+1,j+1],grid[i,j+1]))
            original=polygons.pop(0)
        install(face,original);tagged_faces.append(face)
        for polygon in polygons:
            created=BMFace(bm,polygon,tuple(edge_for(a,b) for a,b in zip(polygon,polygon[1:]+polygon[:1])));created._material=face._material;created._smooth=face._smooth;bm._faces._items.append(created);inner_faces.append(created);tagged_faces.append(created)
    bm.normal_update()
    for sequence in (bm.verts,bm.edges,bm.faces):sequence._lookup=False
    vertices=split_vertices+inner_vertices
    return {'geom_inner':vertices+inner_edges+inner_faces,'geom_split':split_vertices+split_edges,'geom':vertices+split_edges+inner_edges+tagged_faces}

sys.modules['bmesh'].ops._values['subdivide_edges']=bm_subdivide_edges

def bm_bisect_plane(bm,*,geom=(),dist=0.,plane_co=(0,0,0),plane_no=(0,0,0),use_snap_center=False,clear_outer=False,clear_inner=False):
    _bm_plain_topology(bm,'bmesh.ops.bisect_plane')
    bm._check();path='bmesh.ops.bisect_plane'
    if not bm._operators:raise ValueError('BMesh was created without operator support')
    selected=set(geom);origin=Vector(plane_co);normal=Vector(plane_no);distance=float(dist)
    for element in selected:
        if not isinstance(element,(BMVert,BMEdge,BMFace)) or element._bm is not bm:raise ValueError('Expected geometry from this BMesh')
        element._check()
    if len(origin)!=3 or len(normal)!=3 or not all(math.isfinite(x) for x in (*origin,*normal,distance)) or distance<0:raise ValueError('Expected finite 3D plane and nonnegative distance')
    if not normal.length:return {'geom_cut':[],'geom':[]}
    normal.normalize();offset=normal.dot(origin)
    values={v:f32(normal.dot(v.co)-offset) for v in bm.verts}
    if any(not math.isfinite(d) for d in values.values()):raise ValueError('Plane distance must be finite')
    side={v:(1 if d>distance else (-1 if d < -distance else 0)) for v,d in values.items()}
    selected_edges=[e for e in bm.edges if e in selected]
    splitting=[e for e in selected_edges if side[e.verts[0]]*side[e.verts[1]]<0]
    plans=[]
    for face in bm.faces:
        edges=tuple(face.edges);vertices=tuple(face.verts)
        if any(e in splitting for e in edges) or face in selected:
            if face in selected and any(side[v]>0 for v in vertices) and any(side[v]<0 for v in vertices):
                crossings=sum(side[a]*side[b]<0 for a,b in zip(vertices,vertices[1:]+vertices[:1]))
                available=sum(e in splitting for e in edges)
                if crossings and not available:continue
                if crossings!=available:raise UnsupportedError(path,'Include all crossing boundary edges when splitting a face.')
                cuts=available+sum(side[v]==0 for v in vertices)
                if cuts!=2:raise UnsupportedError(path,'Selected polygons must have a single plane intersection segment.')
            plans.append((face,vertices,edges))
    if len(bm.verts)+len(splitting)>100000 or len(bm.faces)+len(plans)>100000:raise UnsupportedError(path,'Bisect limit is 100,000 vertices/faces.')
    connected={v for e in selected_edges for v in e.verts};cut_vertices=[v for v in bm.verts if v in connected and side[v]==0]
    if use_snap_center:
        for v in cut_vertices:v.co=v.co-normal*values[v]
    chains={};created=set();cut_edges=[]
    for edge in splitting:
        a,b=edge.verts;t=values[a]/(values[a]-values[b]);vertex=bm.verts.new(a.co*(1-t)+b.co*t);side[vertex]=0
        cut_vertices.append(vertex);created.add(vertex);chains[edge]=[a,vertex,b]
        edge._verts=(vertex,b);piece=BMEdge(bm,(a,vertex));bm._edges._items.append(piece);created.add(piece)
    edge_map={frozenset(e.verts):e for e in bm.edges}
    def edge_for(a,b):
        key=frozenset((a,b))
        if key not in edge_map:
            edge_map[key]=BMEdge(bm,(a,b));bm._edges._items.append(edge_map[key]);created.add(edge_map[key]);cut_edges.append(edge_map[key])
        return edge_map[key]
    def install(face,cycle):
        face._verts=tuple(cycle);face._edges=tuple(edge_for(a,b) for a,b in zip(cycle,cycle[1:]+cycle[:1]))
    for face,vertices,edges in plans:
        ring=[]
        for i,edge in enumerate(edges):
            chain=chains.get(edge)
            if chain is None:ring.append(vertices[i])
            else:ring.extend(chain[:-1] if chain[0] is vertices[i] else list(reversed(chain))[:-1])
        if face in selected and any(side[v]>0 for v in ring) and any(side[v]<0 for v in ring):
            first=next(i for i,v in enumerate(ring) if side[v]==0);sign=next(side[ring[(first+i)%len(ring)]] for i in range(1,len(ring)) if side[ring[(first+i)%len(ring)]])
            retained=[v for v in ring if side[v]*sign>=0];opposite=[v for v in ring if side[v]*sign<=0]
            install(face,retained)
            other=BMFace(bm,opposite,());other._material=face._material;other._smooth=face._smooth;install(other,opposite);bm._faces._items.append(other);created.add(other)
        else:install(face,ring)
    for edge in selected_edges:
        if edge not in splitting and all(side[v]==0 for v in edge.verts):cut_edges.append(edge)
    # Clearing is explicitly gated by input vertex selection, not incident edges/faces.
    for vertex in list(bm.verts):
        if vertex in selected and ((clear_inner and side[vertex]<0) or (clear_outer and side[vertex]>0)):bm.verts.remove(vertex)
    bm.normal_update()
    for sequence in (bm.verts,bm.edges,bm.faces):sequence._lookup=False
    return {'geom_cut':[e for e in cut_vertices+cut_edges if e.is_valid],'geom':[e for seq in (bm.verts,bm.edges,bm.faces) for e in seq if e in selected or e in created]}

sys.modules['bmesh'].ops._values['bisect_plane']=bm_bisect_plane

def bm_solidify(bm,*,geom=(),thickness=0.):
    _bm_plain_topology(bm,'bmesh.ops.solidify')
    bm._check();path='bmesh.ops.solidify';thickness=float(thickness)
    if not bm._operators:raise ValueError('BMesh was created without operator support')
    if not math.isfinite(thickness):raise ValueError('Thickness must be finite')
    selected=set(geom)
    for element in selected:
        if not isinstance(element,(BMVert,BMEdge,BMFace)) or element._bm is not bm:raise ValueError('Expected geometry from this BMesh')
        element._check()
    faces=[f for f in bm.faces if f in selected];edge_set={e for f in faces for e in f.edges}|{e for e in selected if isinstance(e,BMEdge)}
    edges=[e for e in bm.edges if e in edge_set];vertex_set={v for e in edges for v in e.verts}|{v for v in selected if isinstance(v,BMVert)}
    vertices=[v for v in bm.verts if v in vertex_set]
    uses={e:[] for e in edges};incident={v:[] for v in vertices};normals={}
    for face in faces:
        normal=_bm_face_normal(face);normals[face]=normal
        if not normal.length:raise UnsupportedError(path,'Selected faces must have nonzero area.')
        for i,v in enumerate(face.verts):
            a=(face.verts[i-1].co-v.co).normalized();b=(face.verts[(i+1)%len(face.verts)].co-v.co).normalized()
            angle=math.acos(max(-1.,min(1.,a.dot(b))));incident[v].append((normal,angle))
            uses[face.edges[i]].append((face,v,face.verts[(i+1)%len(face.verts)]))
    if any(len(items)>2 or (len(items)==2 and items[0][1:]==items[1][1:]) for items in uses.values()):raise UnsupportedError(path,'Selected faces must form a consistently oriented manifold shell.')
    boundary=[(edge,items[0] if items else None) for edge,items in uses.items() if len(items)<2]
    if len(bm.verts)+len(vertices)>100000 or len(bm.faces)+len(faces)+len(boundary)>100000:raise UnsupportedError(path,'Solidify limit is 100,000 vertices/faces.')
    directions={v:Vector() for v in vertices}
    for edge,items in uses.items():
        if len(items)==2:
            n1,n2=(normals[item[0]] for item in items);angle=math.acos(max(-1.,min(1.,n1.dot(n2))))
            direction=(n1+n2).normalized()*angle
        elif items:direction=normals[items[0][0]]*(math.pi/2)
        else:continue
        for v in edge.verts:directions[v]=directions[v]+direction
    points={}
    for vertex in vertices:
        terms=incident[vertex];normal=directions[vertex]
        if terms and normal.length<1e-8:normal=terms[0][0].copy()
        if terms:
            if normal.length<1e-8:raise UnsupportedError(path,'Shell offset normals cancel at a selected vertex.')
            normal.normalize();weight=sum(angle for _,angle in terms);cosines=[abs(normal.dot(n)) for n,_ in terms]
            if min(cosines)<1e-5:raise UnsupportedError(path,'Shell offset has a singular corner.')
            factor=sum(angle/cosine for (_,angle),cosine in zip(terms,cosines))/weight
            point=vertex.co-normal*(thickness*factor)
        else:point=vertex.co.copy()
        if not all(math.isfinite(x) for x in point):raise ValueError('Shell coordinates must be finite')
        points[vertex]=point
    copies={v:bm.verts.new(points[v]) for v in vertices};copy_edges={}
    for edge in edges:
        new=BMEdge(bm,tuple(copies[v] for v in edge.verts));bm._edges._items.append(new);copy_edges[edge]=new
    caps=[]
    edge_map={frozenset(e.verts):e for e in bm.edges}
    def edge_for(a,b):
        key=frozenset((a,b))
        if key not in edge_map:edge_map[key]=BMEdge(bm,(a,b));bm._edges._items.append(edge_map[key])
        return edge_map[key]
    def create(cycle,source=None):
        face=BMFace(bm,cycle,tuple(edge_for(a,b) for a,b in zip(cycle,cycle[1:]+cycle[:1])))
        if source is not None:face._material=source._material;face._smooth=source._smooth
        bm._faces._items.append(face);return face
    for face in faces:caps.append(create(tuple(copies[v] for v in reversed(face.verts)),face))
    for edge,use in boundary:
        if use:source,a,b=use
        else:source=None;a,b=edge.verts
        create((b,a,copies[a],copies[b]),source)
    for vertex in vertices:
        if not any(vertex in edge.verts for edge in edges):edge_for(vertex,copies[vertex])
    bm.normal_update()
    for sequence in (bm.verts,bm.edges,bm.faces):sequence._lookup=False
    return {'geom':list(copies.values())+list(copy_edges.values())+caps}

sys.modules['bmesh'].ops._values['solidify']=bm_solidify

def bm_triangulate(bm,*,faces=(),quad_method='BEAUTY',ngon_method='BEAUTY'):
    _bm_plain_topology(bm,'bmesh.ops.triangulate')
    bm._check();path='bmesh.ops.triangulate'
    if not bm._operators:raise ValueError('BMesh was created without operator support')
    values=list(faces)
    if len(set(values))!=len(values):raise ValueError('faces contains a duplicate face')
    for face in values:
        if not isinstance(face,BMFace) or face._bm is not bm:raise ValueError('Expected faces from this BMesh')
        face._check()
    if quad_method not in ('BEAUTY','FIXED','ALTERNATE','SHORT_EDGE','LONG_EDGE') or ngon_method not in ('BEAUTY','EAR_CLIP'):raise ValueError('Unknown triangulation method')
    if len(bm.faces)+sum(len(f.verts)-3 for f in values)>100000:raise UnsupportedError(path,'Triangulation limit is 100,000 faces.')
    groups=request('bmesh_triangulate',polygons=[[list(v.co) for v in f.verts] for f in values],quad_method=quad_method,ngon_method=ngon_method)
    edges={frozenset(e.verts):e for e in bm.edges};new_edges=[];output=[];mapping={};duplicates={}
    cycles={frozenset(f.verts) for f in bm.faces if f not in values or len(f.verts)==3}
    def install(face,cycle):
        face._verts=tuple(cycle);face_edges=[]
        for a,b in zip(cycle,cycle[1:]+cycle[:1]):
            key=frozenset((a,b))
            if key not in edges:edges[key]=BMEdge(bm,(a,b));bm._edges._items.append(edges[key]);new_edges.append(edges[key])
            face_edges.append(edges[key])
        face._edges=tuple(face_edges)
    for face,triangles in zip(values,groups):
        vertices=tuple(face.verts)
        if len(vertices)==3:output.append(face);continue
        for i,indices in enumerate(triangles):
            cycle=tuple(vertices[j] for j in indices)
            if i==0:created=face
            else:
                created=BMFace(bm,(),());created._material=face._material;created._smooth=face._smooth;bm._faces._items.append(created)
            install(created,cycle);output.append(created);mapping[created]=face
            key=frozenset(cycle)
            if key in cycles:duplicates[created]=face
            cycles.add(key)
    bm.normal_update();bm._edges._lookup=False;bm._faces._lookup=False
    return {'edges':new_edges,'faces':output,'face_map':mapping,'face_map_double':duplicates}

sys.modules['bmesh'].ops._values['triangulate']=bm_triangulate

def _bm_extrude_mixed(bm,geom,use_keep_orig):
    path='bmesh.ops.extrude_face_region'
    for value in geom:
        if not isinstance(value,(BMVert,BMEdge,BMFace)) or value._bm is not bm:raise ValueError('Expected geometry from this BMesh')
        value._check()
    selected=set(geom);faces=[f for f in bm.faces if f in selected]
    explicit_edges=[e for e in bm.edges if e in selected];explicit_verts=[v for v in bm.verts if v in selected]
    vertices={v:None for v in explicit_verts}
    for edge in explicit_edges:
        for v in edge.verts:vertices.setdefault(v,None)
    face_uses={};all_uses={}
    for face in bm.faces:
        for i,edge in enumerate(face.edges):all_uses.setdefault(edge,[]).append((face,face.verts[i],face.verts[(i+1)%len(face.verts)]))
    for face in faces:
        for v in face.verts:vertices.setdefault(v,None)
        for i,edge in enumerate(face.edges):face_uses.setdefault(edge,[]).append((face,face.verts[i],face.verts[(i+1)%len(face.verts)]))
    if faces:
        connected={faces[0]};pending=[faces[0]]
        while pending:
            for edge in pending.pop().edges:
                for f,_,_ in face_uses.get(edge,[]):
                    if f not in connected:connected.add(f);pending.append(f)
        if len(connected)!=len(faces):raise UnsupportedError(path,'Mixed face input requires one connected selected face region')
    walls=[];degree={}
    for edge,uses in face_uses.items():
        if len(uses)>2 or (len(uses)==2 and uses[0][1:]==uses[1][1:]):raise UnsupportedError(path,'Selected faces must form a consistently oriented manifold region')
        if len(uses)==1:
            walls.append(uses[0])
            for v in edge.verts:degree[v]=degree.get(v,0)+1
    if any(n!=2 for n in degree.values()):raise UnsupportedError(path,'Selected face boundaries require disjoint closed loops')
    for edge in explicit_edges:
        if edge in face_uses:continue
        uses=all_uses.get(edge,[])
        if len(uses)>2:raise UnsupportedError(path,'Mixed edge extrusion requires at most two incident faces per edge')
        if uses:
            face,a,b=uses[-1];walls.append((face,b,a))
        else:walls.append((None,*edge.verts))
    duplicate_edges={e:None for e in bm.edges if e in face_uses or e in selected}
    delete_faces=not use_keep_orig and any(e in face_uses and any(f not in selected for f,_,_ in all_uses.get(e,[])) for e in explicit_edges)
    attached={v for edge,uses in face_uses.items() if len(uses)==1 and any(f not in selected for f,_,_ in all_uses.get(edge,[])) for v in edge.verts}
    if not delete_faces and attached and any(f.smooth and any(v in attached for v in f.verts) for f in bm.faces):raise UnsupportedError(path,'Retained attached caps require flat incident faces; smooth non-manifold export is outside the verified subset')
    if delete_faces:
        exterior={frozenset(e.verts):next((f for f,_,_ in all_uses.get(e,[]) if f not in selected),None) for e in face_uses}
        walls=[(exterior.get(frozenset((a,b))) or source,a,b) for source,a,b in walls]
    if len(bm.verts)+len(vertices)>100000 or len(bm.faces)+len(faces)+len(walls)>100000:raise UnsupportedError(path,'Editable extrusion limit is 100,000 vertices/faces')
    for v in vertices:vertices[v]=bm.verts.new(v.co)
    for edge in duplicate_edges:
        new=BMEdge(bm,tuple(vertices[v] for v in edge.verts));bm._edges._items.append(new);duplicate_edges[edge]=new
    caps=[]
    for face in faces:
        cap=BMFace(bm,tuple(vertices[v] for v in face.verts),tuple(duplicate_edges[e] for e in face.edges));cap._material=face._material;cap._smooth=face._smooth;cap._normal=face._normal.copy();caps.append(cap);bm._faces._items.append(cap)
    participating={v for e in duplicate_edges for v in e.verts}
    face_vertices={v for f in faces for v in f.verts}
    if delete_faces:
        for face in faces:bm.faces.remove(face)
        for edge in explicit_edges:
            if edge in face_uses and not any(edge in f.edges for f in bm.faces):bm.edges.remove(edge)
        for v in explicit_verts:
            if v in face_vertices and not any(v in e.verts for e in bm.edges):bm.verts.remove(v)
    else:
        for face in faces:
            face._verts=(face._verts[0],)+tuple(reversed(face._verts[1:]));face._edges=tuple(reversed(face._edges));face._normal=-face._normal
    edges={frozenset(e.verts):e for e in bm.edges}
    def connect(a,b):
        key=frozenset((a,b))
        if key not in edges:edges[key]=BMEdge(bm,(a,b));bm._edges._items.append(edges[key])
        return edges[key]
    for source,a,b in walls:
        vs=(a,b,vertices[b],vertices[a]);es=tuple(connect(x,y) for x,y in zip(vs,vs[1:]+vs[:1]));face=BMFace(bm,vs,es)
        if source is not None:face._material=source._material;face._smooth=source._smooth
        bm._faces._items.append(face)
    for v,new in vertices.items():
        if v not in participating:connect(v,new)
    bm._edges._lookup=False;bm._faces._lookup=False
    return {'geom':list(vertices.values())+list(duplicate_edges.values())+caps}

def _bm_open_normal_seed(component):
    # Area-weighted perimeter centers and lexicographic extremal corner scores.
    # The component-count factor is part of the measured Blender convention.
    def dot(a,b):return sum(x*y for x,y in zip(a,b))
    def sub(a,b):return tuple(x-y for x,y in zip(a,b))
    def unit(v):
        length=math.sqrt(dot(v,v));return tuple(x/length for x in v) if length else (0.,0.,0.)
    def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
    polygons={f:[tuple(v.co) for v in f.verts] for f in component}
    weighted=[0.,0.,0.];total=0.
    for face,points in polygons.items():
        lengths=[math.sqrt(dot(sub(b,a),sub(b,a))) for a,b in zip(points,points[1:]+points[:1])]
        weights=[lengths[i-1]+lengths[i] for i in range(len(points))];perimeter=sum(weights)
        normal=[sum((a[(k+1)%3]-b[(k+1)%3])*(a[(k+2)%3]+b[(k+2)%3]) for a,b in zip(points,points[1:]+points[:1])) for k in range(3)]
        area=math.sqrt(dot(normal,normal))*.5
        center=[sum(p[k]*w for p,w in zip(points,weights))/perimeter for k in range(3)] if perimeter else [0.,0.,0.]
        for k in range(3):weighted[k]+=center[k]*area/len(component)
        total+=area
    center=[x/total for x in weighted] if total else [0.,0.,0.]
    best=None;choice=(component[0],False)
    for face,points in polygons.items():
        normal=tuple(_bm_face_normal(face))
        for i,point in enumerate(points):
            delta=sub(point,center);distance=dot(delta,delta)
            if distance<=1.1920928955078125e-7:continue
            forward=unit(sub(points[(i+1)%len(points)],point));backward=unit(sub(points[i-1],point));direction=unit(delta)
            corner=unit(cross(forward,backward))
            if corner==(0.,0.,0.):continue
            if dot(corner,normal)<0:corner=tuple(-x for x in corner)
            outward=dot(direction,corner)
            score=(distance,max(dot(direction,forward),dot(direction,backward)),abs(outward))
            if not all(math.isfinite(x) for x in score):raise UnsupportedError('bmesh.ops.recalc_face_normals','Open-region seed arithmetic must remain finite')
            if best is None or score>best:best=score;choice=(face,outward<0)
    return choice
