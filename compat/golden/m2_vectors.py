"""Float32 mathutils Vector contract, authored before implementation."""
HB_SYMBOLS = {
'mathutils.Vector':'Mutable 2D/3D/4D float32 vector; default is zero 3D',
'mathutils.Vector.copy':'Independent vector copy',
'mathutils.Vector.x':'X component', 'mathutils.Vector.y':'Y component', 'mathutils.Vector.z':'Z component', 'mathutils.Vector.w':'W component',
'mathutils.Vector.xy':'Two-component swizzle','mathutils.Vector.xyz':'Three-component swizzle','mathutils.Vector.yxz':'Swizzle assignment',
'mathutils.Vector.length':'Euclidean length, assignable', 'mathutils.Vector.length_squared':'Squared Euclidean length',
'mathutils.Vector.dot':'dot(other, /); numeric iterable with at least the receiver dimensions; uses the leading components', 'mathutils.Vector.cross':'cross(other, /); nonmutating 2D scalar or independent 3D Vector; numeric iterable with exactly matching dimensions',
'mathutils.Vector.normalize':'Normalize in place; zero vector remains zero', 'mathutils.Vector.normalized':'Normalized copy',
'mathutils.Vector.lerp':'lerp(other, factor, /); nonmutating float32 interpolation with numeric iterable of at least the receiver dimensions; validates all and uses leading components',
'mathutils.Vector.negate':'Negate in place', 'mathutils.Vector.zero':'Set all components to zero',
'mathutils.Vector.to_2d':'Copy as 2D', 'mathutils.Vector.to_3d':'Copy as 3D', 'mathutils.Vector.to_4d':'Copy as homogeneous 4D',
'mathutils.Vector.to_tuple':'to_tuple(precision=-1, /); independent float tuple; -1 preserves float32 components, 0..22 rounds decimal places to nearest even',
'mathutils.Vector.rotate':'rotate(other, /); mutate 2D with 2x2 Matrix or XYZ with Euler/normalized Quaternion/column-normalized Matrix; preserve W; finite active components up to magnitude 1e6',
'mathutils.Vector.project':'Projection onto a vector', 'mathutils.Vector.reflect':'Reflection across a normal',
}
from mathutils import Vector
import math
v=Vector((1,2,3));w=Vector((3,2,1))
assert tuple(v+w)==(4,4,4) and tuple(v-w)==(-2,0,2)
assert tuple(v*2)==(2,4,6) and tuple(2*v)==(2,4,6)
assert tuple(v/2)==(.5,1,1.5) and tuple(-v)==(-1,-2,-3)
assert v@w==10 and v.dot(w)==10 and tuple(v.cross(w))==(-4,8,-4)
# Dot accepts coordinate iterables, while @ retains vector-only equal dimensions.
for dimension in (2,3,4):
    a=Vector(range(1,dimension+1));values=list(range(2,2*dimension+1,2))
    before=(tuple(a),values[:])
    expected=2*sum(x*x for x in range(1,dimension+1))
    for other in (Vector(values),tuple(values),values,iter(values),range(2,2*dimension+1,2),values+[99,100]):
        assert a.dot(other)==expected
    assert (tuple(a),values)==before
assert Vector((1,2)).dot(Vector((3,4,100,200)))==11
assert Vector((1,2)).dot({3:8,4:9})==11
assert Vector((1,2)).dot(b'34')==155
assert Vector((1,2)).dot([1.1,2.2])==5.5000001192092896
assert Vector((1e10,1,1e10)).dot((1,1,-1))==1
assert abs(v.length-math.sqrt(14))<1e-6 and v.length_squared==14
assert tuple(v.xy)==(1,2) and tuple(v.xyz)==(1,2,3)
v.yxz=(4,5,6);assert tuple(v)==(5,4,6)
v.x=1;v.y=2;v.z=3
q=v.copy();q[0]=9;assert v.x==1
assert tuple(Vector((1,2)).to_3d())==(1,2,0)
assert tuple(v.to_4d())==(1,2,3,1) and v.to_4d().w==1
assert tuple(v.to_2d())==(1,2)
assert tuple(v.lerp(w,.25))==(1.5,2,2.5)
assert tuple(v.lerp((3,2,1),.25))==(1.5,2,2.5)
assert abs(Vector((1,0,0)).angle(Vector((0,1,0)))-math.pi/2)<1e-6
assert Vector().angle(v,7)==7
assert tuple(v.project(Vector((0,1,0))))==(0,2,0)
assert tuple(v.reflect(Vector((0,1,0))))==(1,-2,3)
q=Vector((3,4,0));q.normalize();assert abs(q.length-1)<1e-6
q.length=5;assert (q-Vector((3,4,0))).length<1e-6
assert abs(v.normalized().length-1)<1e-6
q.negate();q.zero();assert tuple(q)==(0,0,0)
# RNA vector arithmetic and mutations retain their owning object.
import bpy
bpy.ops.mesh.primitive_cube_add()
o=bpy.context.object
o.location += Vector((1,2,3))
p=o.location;p.x=4
assert tuple(o.location)==(4,2,3)

assert Vector((1,0,0))==Vector((1+1e-7,0,0))
assert Vector((1,0,0))!=Vector((1+2e-7,0,0))
assert Vector((0,0,0))!=Vector((1e-9,0,0))
assert Vector((1,2,3))==Vector((1,2,3)).copy()
assert Vector((1,2))!=Vector((1,2,0))

p=o.location;p+=Vector((1,0,0));assert tuple(o.location)==(5,2,3)
p*=2;assert tuple(o.location)==(10,4,6)
p/=2;p-=Vector((1,0,0));assert tuple(o.location)==(4,2,3)

# Exact Python float results (including signed zero) captured in Blender 5.2.3.
import json,os
with open(os.path.join(os.path.dirname(__file__),'../fixtures/vector-tuple-reference.json')) as source:
    reference=json.load(source)
for row in reference['cases']:
    vector=Vector(float.fromhex(x) for x in row['values'])
    before=[x.hex() for x in vector]
    result=vector.to_tuple(*row['args'])
    assert type(result) is tuple and all(type(x) is float for x in result)
    assert [x.hex() for x in result]==row['result'],row
    assert [x.hex() for x in vector]==before

# Captured rotation values, dimension/type errors and non-mutating inputs.
from mathutils import Matrix,Quaternion,Euler
with open(os.path.join(os.path.dirname(__file__),'../fixtures/vector-rotate-reference.json')) as source:
    reference=json.load(source)
for row in reference['cases']:
    vector=Vector(row['vector']);data=row['rotation'];kind=data['kind']
    rotation=Matrix(data['value']) if kind=='matrix' else Quaternion(data['value']) if kind=='quaternion' else Euler(data['value'],data.get('order','XYZ'))
    before=[list(value) for value in rotation] if kind=='matrix' else list(rotation)
    try:
        assert vector.rotate(rotation) is None
    except (TypeError,ValueError) as error:
        assert type(error).__name__==row.get('error'),(row,error)
        assert tuple(vector)==tuple(row['vector'])
    else:
        assert 'error' not in row,row
        assert len(vector)==len(row['vector']),row
        assert all(math.isclose(a,b,abs_tol=2e-6,rel_tol=2e-6) for a,b in zip(vector,row['result'])),(row,tuple(vector))
    assert before==([list(value) for value in rotation] if kind=='matrix' else list(rotation))

# Numeric iterables, surplus coordinates, extrapolation and native error classes.
def lerp_endpoint(kind,values):
    if kind=='vector':return Vector(values)
    if kind=='tuple':return tuple(values)
    if kind=='iterator':return iter(values)
    if kind=='generator':return (x for x in values)
    if kind=='range':return range(*values)
    if kind=='dict':return {x:None for x in values}
    if kind=='bytes':return bytes(values)
    return values

with open(os.path.join(os.path.dirname(__file__),'../fixtures/vector-lerp-reference.json')) as source:
    reference=json.load(source)
for row in reference['cases']:
    vector=Vector(row['a']);other=lerp_endpoint(row['kind'],row['other'])
    before=[x.hex() for x in vector]
    other_before=list(other) if isinstance(other,(Vector,list,tuple)) else None
    try:result=vector.lerp(other,row['factor'])
    except (TypeError,ValueError) as error:
        assert type(error).__name__==row.get('error'),(row,error)
    else:
        assert 'error' not in row and type(result) is Vector and result is not vector,row
        assert len(result)==len(vector),row
        assert all(math.isclose(a,b,abs_tol=1e-30,rel_tol=2e-6)
                   for a,b in zip(result,row['result'])),(row,list(result))
    assert [x.hex() for x in vector]==before
    if other_before is not None:assert list(other)==other_before

# Signed 2D area, independent 3D normals and native dimensional/type errors.
with open(os.path.join(os.path.dirname(__file__),'../fixtures/vector-cross-reference.json')) as source:
    reference=json.load(source)
for row in reference['cases']:
    vector=Vector(row['a']);other=lerp_endpoint(row['kind'],row['b'])
    before=[x.hex() for x in vector]
    other_before=list(other) if isinstance(other,(Vector,list,tuple)) else None
    try:result=vector.cross(other)
    except (TypeError,ValueError) as error:
        assert type(error).__name__==row.get('error'),(row,error)
    else:
        assert 'error' not in row and type(result).__name__==row['type'],row
        if isinstance(result,Vector):
            assert result is not vector and result is not other and len(result)==3,row
            result=list(result)
        assert result==row['result'],(row,result)
    assert [x.hex() for x in vector]==before
    if other_before is not None:assert list(other)==other_before
