"""Object vertex groups and read-only mesh membership views."""
class VertexGroup(Strict):
    _path='bpy.types.VertexGroup'
    def __init__(self,owner,key):self._owner,self._key=owner,key
    def _groups(self):return self._owner._get().get('vertex_groups',[])
    @property
    def index(self):
        for index,group in enumerate(self._groups()):
            if group['key']==self._key:return index
        raise ReferenceError('Vertex group has been removed')
    @property
    def name(self):return self._groups()[self.index]['name']
    @name.setter
    def name(self,value):self._edit('rename',name=str(value))
    def _edit(self,action,**kwargs):
        self.index
        return request('group_edit',id=self._owner._id,group=self._key,action=action,**kwargs)
    def add(self,index,weight,type):
        weight=float(weight)
        if not math.isfinite(weight):raise ValueError('Vertex-group weight must be finite')
        self._edit('add',vertices=[int(v) for v in index],weight=f32(max(0.,min(1.,weight))),mode=type)
    def remove(self,index):self._edit('remove_weights',vertices=[int(v) for v in index])
    def weight(self,index):
        group=self.index;index=max(0,int(index));mesh=self._owner.data._get()
        if index>=len(mesh['vertices']):return 0.
        weights=mesh.get('deform_weights')
        for member,value in weights[index] if weights else []:
            if member==group:return value
        raise RuntimeError('Vertex not in group')
class VertexGroups(Sequence):
    def __init__(self,owner):
        self._owner=owner
        super().__init__('bpy.types.Object.vertex_groups',lambda:[VertexGroup(owner,g['key']) for g in owner._get().get('vertex_groups',[])])
    def new(self,*,name='Group'):return VertexGroup(self._owner,request('group_edit',id=self._owner._id,action='new',name=str(name)))
    def remove(self,group):
        if not isinstance(group,VertexGroup) or group._owner is not self._owner:raise TypeError('Expected a vertex group from this object')
        group._edit('remove')
    def clear(self):request('group_edit',id=self._owner._id,action='clear')
class VertexGroupElement(Strict):
    _path='bpy.types.VertexGroupElement'
    def __init__(self,group,weight):self._group,self._weight=group,weight
    @property
    def group(self):return self._group
    @property
    def weight(self):return self._weight

def vertex_memberships(vertex):
    if vertex._field!='vertices':raise UnsupportedError(vertex._path+'.groups')
    def values():
        mesh=vertex._mesh._get();weights=mesh.get('deform_weights')
        if vertex._index>=len(mesh['vertices']):raise ReferenceError('Mesh vertex has been removed')
        return [VertexGroupElement(group,weight) for group,weight in weights[vertex._index]] if weights else []
    return Sequence('bpy.types.MeshVertex.groups',values)
Object.vertex_groups=property(lambda self:VertexGroups(self))
MeshElement.groups=property(vertex_memberships)
