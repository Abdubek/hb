"""Float32 mathutils Vector contract, authored before implementation."""
HB_SYMBOLS = {
'mathutils.Vector':'Mutable 2D/3D/4D float32 vector; default is zero 3D',
'mathutils.Vector.copy':'Independent vector copy',
'mathutils.Vector.x':'X component', 'mathutils.Vector.y':'Y component', 'mathutils.Vector.z':'Z component', 'mathutils.Vector.w':'W component',
'mathutils.Vector.xy':'Two-component swizzle','mathutils.Vector.xyz':'Three-component swizzle','mathutils.Vector.yxz':'Swizzle assignment',
'mathutils.Vector.length':'Euclidean length, assignable', 'mathutils.Vector.length_squared':'Squared Euclidean length',
'mathutils.Vector.dot':'Dot product of equal-sized vectors', 'mathutils.Vector.cross':'3D cross product',
'mathutils.Vector.normalize':'Normalize in place; zero vector remains zero', 'mathutils.Vector.normalized':'Normalized copy',
'mathutils.Vector.lerp':'Linear interpolation', 'mathutils.Vector.angle':'Angle in radians, with optional fallback for zero vectors',
'mathutils.Vector.negate':'Negate in place', 'mathutils.Vector.zero':'Set all components to zero',
'mathutils.Vector.to_2d':'Copy as 2D', 'mathutils.Vector.to_3d':'Copy as 3D', 'mathutils.Vector.to_4d':'Copy as homogeneous 4D',
'mathutils.Vector.project':'Projection onto a vector', 'mathutils.Vector.reflect':'Reflection across a normal',
}
from mathutils import Vector
import math
v=Vector((1,2,3));w=Vector((3,2,1))
assert tuple(v+w)==(4,4,4) and tuple(v-w)==(-2,0,2)
assert tuple(v*2)==(2,4,6) and tuple(2*v)==(2,4,6)
assert tuple(v/2)==(.5,1,1.5) and tuple(-v)==(-1,-2,-3)
assert v@w==10 and v.dot(w)==10 and tuple(v.cross(w))==(-4,8,-4)
assert abs(v.length-math.sqrt(14))<1e-6 and v.length_squared==14
assert tuple(v.xy)==(1,2) and tuple(v.xyz)==(1,2,3)
v.yxz=(4,5,6);assert tuple(v)==(5,4,6)
v.x=1;v.y=2;v.z=3
q=v.copy();q[0]=9;assert v.x==1
assert tuple(Vector((1,2)).to_3d())==(1,2,0)
assert tuple(v.to_4d())==(1,2,3,1) and v.to_4d().w==1
assert tuple(v.to_2d())==(1,2)
assert tuple(v.lerp(w,.25))==(1.5,2,2.5)
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
