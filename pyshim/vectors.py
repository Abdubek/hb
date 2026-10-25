"""Independent float32 Vector implementation. No Blender source is embedded."""
import math

class Vector(Strict):
    _path='mathutils.Vector'
    def __init__(self,seq=(0.,0.,0.)):
        values=[f32(x) for x in seq]
        if len(values) not in (2,3,4):raise ValueError('Vector: sequence size is 2D, 3D or 4D')
        self._values=values
    def _read_values(self):return self._values[:]
    def _write_values(self,values):self._values=[f32(x) for x in values]
    def __len__(self):return len(self._read_values())
    def __iter__(self):return iter(self._read_values())
    def __getitem__(self,key):
        values=self._read_values()
        return tuple(values[key]) if isinstance(key,slice) else values[key]
    def __setitem__(self,key,value):
        values=self._read_values()
        if isinstance(key,slice):
            value=list(value)
            if len(value)!=len(values[key]):raise ValueError('Vector slice size mismatch')
        values[key]=value
        self._write_values(values)
    def __getattr__(self,name):
        if 1<=len(name)<=4 and all(c in 'xyzw' for c in name):
            ix=['xyzw'.index(c) for c in name]
            if max(ix)>=len(self):raise AttributeError('Vector has no '+name+' component')
            return self[ix[0]] if len(ix)==1 else Vector(self[i] for i in ix)
        return super().__getattr__(name)
    def __setattr__(self,name,value):
        if 1<=len(name)<=4 and all(c in 'xyzw' for c in name):
            ix=['xyzw'.index(c) for c in name]
            if len(set(ix))!=len(ix):raise AttributeError('Swizzle assignment contains duplicate axes')
            if max(ix)>=len(self):raise AttributeError('Vector has no '+name+' component')
            values=self._read_values();new=[value] if len(ix)==1 else list(value)
            if len(new)!=len(ix):raise ValueError('Swizzle size mismatch')
            for i,x in zip(ix,new):values[i]=x
            self._write_values(values)
        else:super().__setattr__(name,value)
    def __repr__(self):return 'Vector('+repr(tuple(self))+')'
    def copy(self):return Vector(self)
    def _pair(self,other):
        if not isinstance(other,Vector):raise TypeError('Expected a Vector')
        if len(self)!=len(other):raise ValueError('Vector dimensions must match')
        return zip(self,other)
    def __add__(self,other):return Vector(f32(a+b) for a,b in self._pair(other))
    def __sub__(self,other):return Vector(f32(a-b) for a,b in self._pair(other))
    def __mul__(self,other):
        if isinstance(other,Vector):return Vector(f32(a*b) for a,b in self._pair(other))
        s=f32(other);return Vector(f32(a*s) for a in self)
    __rmul__=__mul__
    def __iadd__(self,other):self._write_values(self+other);return self
    def __isub__(self,other):self._write_values(self-other);return self
    def __imul__(self,other):self._write_values(self*other);return self
    def __itruediv__(self,other):self._write_values(self/other);return self
    def __truediv__(self,other):
        s=f32(other)
        if s==0:raise ZeroDivisionError('Vector division by zero')
        inv=f32(1/s);return Vector(f32(a*inv) for a in self)
    def __neg__(self):return Vector(-a for a in self)
    def __pos__(self):return self.copy()
    def __matmul__(self,other):return self.dot(other)
    def __eq__(self,other):
        if not isinstance(other,Vector) or len(self)!=len(other):return False
        def ordered(v):
            bits=struct.unpack('i',struct.pack('f',v))[0]
            return -2147483648-bits if bits<0 else bits
        return all(a==b or (math.isfinite(a) and math.isfinite(b) and abs(ordered(a)-ordered(b))<=1) for a,b in zip(self,other))
    def dot(self,other):
        return sum(f32(a*b) for a,b in self._pair(other))
    def cross(self,other):
        if len(self)!=3 or len(other)!=3:raise ValueError('cross requires two 3D vectors')
        return Vector(f32(f32(self[(i+1)%3]*other[(i+2)%3])-f32(self[(i+2)%3]*other[(i+1)%3])) for i in range(3))
    @property
    def length_squared(self):return self.dot(self)
    @property
    def length(self):return math.sqrt(self.length_squared)
    @length.setter
    def length(self,value):
        value=f32(value)
        if value<0:raise ValueError('Vector length cannot be negative')
        length=self.length
        if length:self._write_values(self*f32(value/length))
    def normalize(self):
        values=self._read_values();n=min(3,len(values));squared=0.
        for x in values[:n]:squared=f32(squared+f32(x*x))
        if squared>1e-35:
            factor=f32(1/f32(math.sqrt(squared)))
            values[:n]=[f32(x*factor) for x in values[:n]]
        else:values[:n]=[0.]*n
        self._write_values(values)
    def normalized(self):
        v=self.copy();v.normalize();return v
    def negate(self):self._write_values(-self)
    def zero(self):self._write_values([0.]*len(self))
    def lerp(self,other,factor):
        t=f32(factor);u=f32(1-t)
        return Vector(f32(f32(u*a)+f32(t*b)) for a,b in self._pair(other))
    def angle(self,other,*fallback):
        if len(fallback)>1:raise TypeError('angle expects one optional fallback')
        self._pair(other)
        a=self.normalized();b=other.normalized()
        if self.length==0 or other.length==0:
            if fallback:return fallback[0]
            raise ValueError('Vector.angle: zero length vectors have no valid angle')
        return f32(math.acos(max(-1.,min(1.,a.dot(b)))))
    def project(self,other):
        return other*(self.dot(other)/other.length_squared) if other.length_squared else Vector([float('nan')]*len(self))
    def reflect(self,normal):return self-normal.normalized()*f32(2*self.dot(normal.normalized()))
    def to_2d(self):return Vector(tuple(self)[:2])
    def to_3d(self):return Vector((tuple(self)+(0.,))[:3])
    def to_4d(self):return Vector((tuple(self)+(0.,)*(3-len(self))+(1.,))[:4])

class VectorView(Vector):
    def __init__(self,get,set,path):self._get,self._set,self._path=get,set,path
    def _read_values(self):return list(self._get())
    def _write_values(self,values):self._set([f32(x) for x in values])

install_module('mathutils',dict(Vector=Vector))
