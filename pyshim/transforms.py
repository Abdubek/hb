"""Independent rotation and bounded rectangular matrix algebra; storage rounds to float32."""
class _RotationValues(Strict):
    def _read_values(self):return self._values[:]
    def _write_values(self,values):self._values=[f32(v) for v in values]
    def __len__(self):return len(self._read_values())
    def __iter__(self):return iter(self._read_values())
    def __getitem__(self,key):return tuple(self._read_values())[key]
    def __setitem__(self,key,value):
        values=self._read_values()
        if isinstance(key,slice) and len(value)!=len(values[key]):raise ValueError('Slice size mismatch')
        values[key]=value;self._write_values(values)
    def __eq__(self,other):return type(self) is type(other) and Vector(self)==Vector(other)

def _component(index):return property(lambda self:self[index],lambda self,value:self.__setitem__(index,value))

class Quaternion(_RotationValues):
    _path='mathutils.Quaternion'
    w=_component(0);x=_component(1);y=_component(2);z=_component(3)
    def __init__(self,seq=(1.,0.,0.,0.),angle=None):
        values=[f32(v) for v in seq]
        if angle is None:
            if len(values)!=4:raise ValueError('Quaternion requires four components')
        else:
            if len(values)!=3:raise ValueError('Quaternion axis requires three components')
            axis=Vector(values).normalized();half=f32(f32(angle)*.5)
            values=[math.cos(half),*(v*math.sin(half) for v in axis)] if axis.length else [1,0,0,0]
        self._write_values(values)
    def copy(self):return Quaternion(self)
    def _square(self):
        total=0.
        for v in self:total=f32(total+f32(v*v))
        return total
    @property
    def magnitude(self):return f32(math.sqrt(self._square()))
    def dot(self,other):
        if not isinstance(other,Quaternion):raise TypeError('Expected Quaternion')
        return f32(sum(a*b for a,b in zip(self,other)))
    def normalize(self):
        length=self.magnitude
        if length:
            factor=f32(1/length);self._write_values([v*factor for v in self])
        else:self._write_values([0,1,0,0])
    def normalized(self):q=self.copy();q.normalize();return q
    def conjugate(self):self._write_values([self.w,-self.x,-self.y,-self.z])
    def conjugated(self):q=self.copy();q.conjugate();return q
    def invert(self):
        square=self._square()
        if square:
            factor=f32(1/square);self._write_values([self.w*factor,-self.x*factor,-self.y*factor,-self.z*factor])
    def inverted(self):q=self.copy();q.invert();return q
    def __matmul__(self,other):
        if isinstance(other,Vector):return self.to_matrix()@other
        if not isinstance(other,Quaternion):raise TypeError('Expected Quaternion or Vector')
        w,x,y,z=self;W,X,Y,Z=other
        return Quaternion((w*W-x*X-y*Y-z*Z,w*X+x*W+y*Z-z*Y,w*Y-x*Z+y*W+z*X,w*Z+x*Y-y*X+z*W))
    def slerp(self,other,factor):
        if not isinstance(other,Quaternion):raise TypeError('Expected Quaternion')
        factor=f32(factor)
        if not 0.<=factor<=1.:raise ValueError('Quaternion.slerp(): interpolation factor must be in [0, 1]')
        if any(not math.isfinite(x) or abs(x)>1e6 for x in (*self,*other)):raise UnsupportedError(self._path+'.slerp','Use finite quaternion components with magnitude at most 1e6.')
        cosine=self.dot(other);sign=-1. if cosine<0 else 1.;cosine=abs(cosine)
        if cosine<.999999:
            angle=f32(math.acos(cosine));sine=f32(math.sin(angle))
            a=f32(math.sin(f32(f32(1.-factor)*angle))/sine)
            b=f32(math.sin(f32(factor*angle))/sine)
        else:a=f32(1.-factor);b=factor
        return Quaternion(f32(f32(sign*a*x)+f32(b*y)) for x,y in zip(self,other))
    def to_matrix(self):
        w,x,y,z=self
        return Matrix(((1-2*(y*y+z*z),2*(x*y-w*z),2*(x*z+w*y)),(2*(x*y+w*z),1-2*(x*x+z*z),2*(y*z-w*x)),(2*(x*z-w*y),2*(y*z+w*x),1-2*(x*x+y*y))))
    def to_euler(self,order='XYZ'):return self.normalized().to_matrix().to_euler(order)

class QuaternionView(Quaternion):
    def __init__(self,get,set):self._get,self._set=get,set
    def _read_values(self):return self._get()
    def _write_values(self,values):self._set([f32(v) for v in values])

_ORDERS={'XYZ':(0,1,2,0),'XZY':(0,2,1,1),'YXZ':(1,0,2,1),'YZX':(1,2,0,0),'ZXY':(2,0,1,0),'ZYX':(2,1,0,1)}
class Euler(_RotationValues):
    _path='mathutils.Euler'
    x=_component(0);y=_component(1);z=_component(2)
    def __init__(self,seq=(0.,0.,0.),order='XYZ'):
        values=list(seq)
        if len(values)!=3:raise ValueError('Euler requires three angles')
        self._write_values(values);self.order=order
    @property
    def order(self):return self._order
    @order.setter
    def order(self,value):
        if value not in _ORDERS:raise ValueError('Invalid Euler order')
        self._order=value
    def copy(self):return Euler(self,self.order)
    def zero(self):self._write_values([0,0,0])
    def to_quaternion(self):
        result=Quaternion()
        for name in self.order:
            axis='XYZ'.index(name);result=Quaternion([int(i==axis) for i in range(3)],self[axis])@result
        return result
    def to_matrix(self):
        rows=[[float(i==j) for j in range(3)] for i in range(3)]
        for name in self.order:
            axis='XYZ'.index(name);a=(axis+1)%3;b=(axis+2)%3
            c=math.cos(self[axis]);s=math.sin(self[axis]);rotation=[[float(i==j) for j in range(3)] for i in range(3)]
            rotation[a][a]=rotation[b][b]=c;rotation[a][b]=-s;rotation[b][a]=s
            rows=[[sum(rotation[i][k]*rows[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
        return Matrix(rows)

class EulerView(Euler):
    def __init__(self,get,set,path,order):self._get,self._set,self._path,self._get_order=get,set,path,order
    def _read_values(self):return list(self._get())
    def _write_values(self,values):self._set([f32(v) for v in values])
    @property
    def order(self):return self._get_order() if self._get_order() in _ORDERS else 'XYZ'
    @order.setter
    def order(self,value):
        raise UnsupportedError(self._path+'.order','Set Object.rotation_mode to select an Euler order.')

class Matrix(Strict):
    _path='mathutils.Matrix'
    def __getattr__(self,name):
        if name=='translation' and (len(self)!=4 or len(self._rows[0])!=4):raise AttributeError('Matrix.translation requires a 4x4 matrix')
        return super().__getattr__(name)
    def __init__(self,rows=None):
        if rows is None:rows=[[int(i==j) for j in range(4)] for i in range(4)]
        rows=[list(row) for row in rows];n=len(rows)
        if n not in (2,3,4) or len(rows[0]) not in (2,3,4) or any(len(row)!=len(rows[0]) for row in rows):raise UnsupportedError(self._path,'Use 2..4 rows and 2..4 equally sized columns.')
        self._rows=[[f32(v) for v in row] for row in rows]
    def __len__(self):return len(self._rows)
    def __iter__(self):return iter([self[i] for i in range(len(self))])
    def __getitem__(self,index):
        if isinstance(index,slice):return tuple(self[i] for i in range(len(self))[index])
        if not -len(self)<=index<len(self):raise IndexError('Matrix row index out of range')
        return VectorView(lambda:self._rows[index][:],lambda values:self.__setitem__(index,values),self._path+'.row')
    def __setitem__(self,index,values):
        values=list(values)
        if len(values)!=len(self._rows[0]):raise ValueError('Matrix row size mismatch')
        self._rows[index]=[f32(v) for v in values]
    def copy(self):return Matrix(self._rows)
    @classmethod
    def Identity(cls,size):
        if size not in (2,3,4):raise ValueError('Matrix size must be 2, 3 or 4')
        return cls([[int(i==j) for j in range(size)] for i in range(size)])
    @classmethod
    def Diagonal(cls,values):
        values=list(values)
        if len(values) not in (2,3,4):raise ValueError('Diagonal size must be 2, 3 or 4')
        return cls([[values[i] if i==j else 0 for j in range(len(values))] for i in range(len(values))])
    @classmethod
    def Translation(cls,vector):
        m=cls.Identity(4);m.translation=vector;return m
    @classmethod
    def Rotation(cls,angle,size,axis=None):
        if size==2:
            c=math.cos(f32(angle));s=math.sin(f32(angle));return cls(((c,-s),(s,c)))
        if size not in (3,4):raise ValueError('Rotation size must be 2, 3 or 4')
        if isinstance(axis,str):
            if axis not in ('X','Y','Z'):raise ValueError('Invalid rotation axis')
            axis=[int(i=='XYZ'.index(axis)) for i in range(3)]
        if axis is None:raise ValueError('Rotation axis required')
        matrix=Quaternion(axis,angle).to_matrix();return matrix if size==3 else matrix.to_4x4()
    @classmethod
    def Scale(cls,factor,size,axis=None):
        m=cls.Identity(size);factor=f32(factor)
        if axis is None:
            for i in range(min(size,3)):m._rows[i][i]=factor
        else:
            axis=Vector(axis).normalized()
            if len(axis)!=min(size,3):raise ValueError('Scale axis dimension mismatch')
            for i in range(len(axis)):
                for j in range(len(axis)):m._rows[i][j]=f32((int(i==j))+(factor-1)*axis[i]*axis[j])
        return m
    def __matmul__(self,other):
        rows=len(self);cols=len(self._rows[0])
        if isinstance(other,Matrix):
            if len(other)!=cols:raise ValueError('Matrix dimensions must match')
            return Matrix([[sum(self._rows[i][k]*other._rows[k][j] for k in range(cols)) for j in range(len(other._rows[0]))] for i in range(rows)])
        if isinstance(other,Vector):
            values=list(other);homogeneous=cols==4 and len(values)==3
            if homogeneous:
                if rows==2:raise UnsupportedError(self._path+'.__matmul__','Use a four-component vector for a 2x4 matrix; Blender 4.5 returns an uninitialized third component for 2x4 @ 3D.')
                values.append(1.)
            if len(values)!=cols:raise ValueError('Matrix and Vector dimensions must match')
            result=[sum(a*b for a,b in zip(row,values)) for row in self._rows]
            return Vector(result[:3] if homogeneous else result)
        raise TypeError('Matrix multiplication expects Matrix or Vector')
    def _square_required(self):
        if len(self)!=len(self._rows[0]):raise ValueError('This Matrix operation requires a square matrix')
    def transposed(self):self._square_required();return Matrix(zip(*self._rows))
    def transpose(self):self._rows=self.transposed()._rows
    def determinant(self):
        self._square_required()
        def det(rows):
            if len(rows)==1:return rows[0][0]
            return sum((-1)**j*rows[0][j]*det([row[:j]+row[j+1:] for row in rows[1:]]) for j in range(len(rows)))
        return f32(det(self._rows))
    def inverted(self,*fallback):
        self._square_required()
        if len(fallback)>1:raise TypeError('One optional fallback expected')
        n=len(self);rows=[row[:]+[int(i==j) for j in range(n)] for i,row in enumerate(self._rows)]
        for col in range(n):
            pivot=max(range(col,n),key=lambda i:abs(rows[i][col]))
            if rows[pivot][col]==0:
                if fallback:return fallback[0]
                raise ValueError('Matrix is singular')
            rows[col],rows[pivot]=rows[pivot],rows[col];div=rows[col][col];rows[col]=[v/div for v in rows[col]]
            for i in range(n):
                if i!=col:
                    factor=rows[i][col];rows[i]=[a-factor*b for a,b in zip(rows[i],rows[col])]
        return Matrix([row[n:] for row in rows])
    def invert(self,*fallback):
        value=self.inverted(*fallback)
        if not isinstance(value,Matrix):raise TypeError('Matrix fallback required for in-place inversion')
        self._rows=value._rows
    def _resize(self,size):return Matrix([[self._rows[i][j] if i<len(self) and j<len(self._rows[0]) else int(i==j) for j in range(size)] for i in range(size)])
    def to_3x3(self):return self._resize(3)
    def to_4x4(self):return self._resize(4)
    def _set_translation(self,value):
        if len(self)!=4 or len(self._rows[0])!=4:raise AttributeError('Translation requires a 4x4 matrix')
        value=list(value)
        if len(value)!=3:raise ValueError('Translation requires three coordinates')
        for i,v in enumerate(value):self._rows[i][3]=f32(v)
    @property
    def translation(self):
        if len(self)!=4 or len(self._rows[0])!=4:raise AttributeError('Translation requires a 4x4 matrix')
        return VectorView(lambda:[row[3] for row in self._rows[:3]],self._set_translation,self._path+'.translation')
    @translation.setter
    def translation(self,value):self._set_translation(value)
    def decompose(self):
        if len(self)!=4 or len(self._rows[0])!=4:raise ValueError('Matrix.decompose() expects a 4x4 matrix')
        if any(not math.isfinite(x) or abs(x)>1e6 for row in self._rows for x in row):raise UnsupportedError(self._path+'.decompose','Use finite matrix components with magnitude at most 1e6.')
        columns=[Vector(self._rows[i][j] for i in range(3)) for j in range(3)]
        scales=[f32(c.length) for c in columns]
        rotation=Matrix([[f32(columns[j][i]*f32(1./scales[j])) if scales[j] else columns[j][i] for j in range(3)] for i in range(3)])
        if rotation.determinant()<0:
            scales=[-x for x in scales]
            rotation=Matrix([[-x for x in row] for row in rotation])
        # Solve the quadratic rotation identities for one quaternion column.
        # The diagonal-pair pivot remains stable for singular/sheared inputs.
        m=rotation._rows;x,y,z=(m[i][i] for i in range(3))
        diagonal=[f32(f32(f32(1+x)+y)+z),f32(f32(f32(1+x)-y)-z),f32(f32(f32(1-x)+y)-z),f32(f32(f32(1-x)-y)+z)]
        pivot=(1 if x>y else 2) if z<0 else (3 if x < -y else 0)
        products=[[0.]*4 for _ in range(4)]
        for i in range(4):products[i][i]=diagonal[i]
        for i,j,value in [(0,1,m[2][1]-m[1][2]),(0,2,m[0][2]-m[2][0]),(0,3,m[1][0]-m[0][1]),(1,2,m[0][1]+m[1][0]),(1,3,m[0][2]+m[2][0]),(2,3,m[1][2]+m[2][1])]:products[i][j]=products[j][i]=f32(value)
        factor=f32(.5/f32(math.sqrt(max(0.,diagonal[pivot])))) if diagonal[pivot]>0 else 0.
        if products[0][pivot]<0:factor=-factor
        q=Quaternion(products[i][pivot]*factor for i in range(4))
        if abs(q._square()-1.)>=.0006:q.normalize()
        return Vector(self._rows[i][3] for i in range(3)),q,Vector(scales)
    def _rotation_rows(self,correct_reflection=False):
        if len(self)<3 or len(self)!=len(self._rows[0]):raise ValueError('Rotation conversion requires 3x3 or 4x4 matrix')
        cols=[Vector([self._rows[i][j] for i in range(3)]).normalized() for j in range(3)]
        m=Matrix(zip(*cols))
        if correct_reflection and m.determinant()<0:m=Matrix([[-v for v in row] for row in m])
        return m._rows
    def to_quaternion(self):
        m=self._rotation_rows(True)
        if not any(v for row in m for v in row):return Quaternion()
        trace=sum(m[i][i] for i in range(3))
        if trace>0:
            s=2*math.sqrt(trace+1);q=[s/4,(m[2][1]-m[1][2])/s,(m[0][2]-m[2][0])/s,(m[1][0]-m[0][1])/s]
        else:
            i=max(range(3),key=lambda i:m[i][i]);j=(i+1)%3;k=(i+2)%3
            s=2*math.sqrt(max(0,1+m[i][i]-m[j][j]-m[k][k]));q=[0,0,0,0]
            if s==0:return Quaternion()
            q[0]=(m[k][j]-m[j][k])/s;q[i+1]=s/4;q[j+1]=(m[i][j]+m[j][i])/s;q[k+1]=(m[i][k]+m[k][i])/s
        if q[0]<0:q=[-v for v in q]
        return Quaternion(q).normalized()
    def to_euler(self,order='XYZ'):
        if order not in _ORDERS:raise ValueError('Invalid Euler order')
        i,j,k,parity=_ORDERS[order];m=self._rotation_rows();cy=math.hypot(m[i][i],m[j][i])
        if cy>1e-6:angles=[math.atan2(m[k][j],m[k][k]),math.atan2(-m[k][i],cy),math.atan2(m[j][i],m[i][i])]
        else:angles=[math.atan2(-m[j][k],m[j][j]),math.atan2(-m[k][i],cy),0.]
        if parity:angles=[-v for v in angles]
        def wrap(v):return (v+math.pi)%(2*math.pi)-math.pi
        other=[wrap(angles[0]+math.pi),wrap(math.pi-angles[1]),wrap(angles[2]+math.pi)]
        if sum(map(abs,other))<sum(map(abs,angles)):angles=other
        values=[0.,0.,0.]
        for axis,value in zip((i,j,k),angles):values[axis]=value
        return Euler(values,order)

def _to_track_quat(self,track='Z',up='Y'):
    if len(self)!=3:raise ValueError('Tracking requires a 3D vector')
    if track not in ('X','Y','Z','-X','-Y','-Z') or up not in ('X','Y','Z'):raise ValueError('Invalid tracking axis')
    t='XYZ'.index(track[-1]);u='XYZ'.index(up)
    if t==u:raise ValueError('Track and up axes must differ')
    if self.length==0:return Quaternion()
    direction=self.normalized()*(-1 if track.startswith('-') else 1)
    # An algebraic projection avoids cancellation in 1-z*z near vertical.
    projected=Vector((-direction.x*direction.z,-direction.y*direction.z,direction.x*direction.x+direction.y*direction.y))
    if projected.length<1e-10:
        # Axial defaults measured for each axis pair in Blender 4.5.
        if t==0:projected=Vector((-direction.z,0,0))
        elif t==1:projected=Vector((0,-direction.z,0))
        else:
            projected=Vector((-1,0,0)) if u==0 and direction.z>0 else Vector((0,1,0)) if u==0 else Vector((0,-1 if direction.z>0 else 1,0))
            if track=='-Z' and direction.z>0 and u==1:projected=Vector((0,1,0))
    cols=[None,None,None];cols[t]=direction;cols[u]=projected.normalized();other=3-t-u
    cols[other]=cols[(other+1)%3].cross(cols[(other+2)%3])
    return Matrix(zip(*cols)).to_quaternion()

Vector.to_track_quat=_to_track_quat
sys.modules['mathutils'].__dict__.update(Matrix=Matrix,Euler=Euler,Quaternion=Quaternion)
Object.rotation_euler=property(lambda self:EulerView(lambda:self._read('rotation_euler'),lambda value:self._set('rotation_euler',value),'bpy.types.Object.rotation_euler',lambda:self.rotation_mode),lambda self,value:self._set('rotation_euler',[f32(v) for v in value]))
