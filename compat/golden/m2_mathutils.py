import math,bpy
from mathutils import Vector,Matrix,Quaternion,Euler
HB_SYMBOLS={
'mathutils.Matrix':'Mutable square float32 matrices of size 2, 3 or 4',
'mathutils.Matrix.Identity':'Identity matrix', 'mathutils.Matrix.Translation':'Homogeneous translation matrix',
'mathutils.Matrix.Rotation':'Axis-angle rotation matrix','mathutils.Matrix.Scale':'Uniform or directional scaling matrix',
'mathutils.Matrix.Diagonal':'Diagonal matrix','mathutils.Matrix.copy':'Independent copy',
'mathutils.Matrix.inverted':'Inverse with optional fallback','mathutils.Matrix.invert':'In-place inverse',
'mathutils.Matrix.transposed':'Transposed copy','mathutils.Matrix.transpose':'In-place transpose',
'mathutils.Matrix.determinant':'Matrix determinant','mathutils.Matrix.to_3x3':'Resize to 3x3','mathutils.Matrix.to_4x4':'Resize to 4x4',
'mathutils.Matrix.to_quaternion':'Rotation quaternion from a matrix','mathutils.Matrix.to_euler':'Euler rotation from a matrix',
'mathutils.Matrix.translation':'Mutable homogeneous translation vector',
'mathutils.Euler':'Mutable float32 Euler angles, six rotation orders','mathutils.Euler.x':'X angle','mathutils.Euler.y':'Y angle','mathutils.Euler.z':'Z angle',
'mathutils.Euler.order':'Rotation order','mathutils.Euler.copy':'Independent copy','mathutils.Euler.to_matrix':'Rotation matrix','mathutils.Euler.to_quaternion':'Rotation quaternion','mathutils.Euler.zero':'Zero angles',
'mathutils.Quaternion':'Float32 quaternion from components or axis and angle','mathutils.Quaternion.copy':'Independent copy',
'mathutils.Quaternion.w':'Scalar component','mathutils.Quaternion.x':'X component','mathutils.Quaternion.y':'Y component','mathutils.Quaternion.z':'Z component',
'mathutils.Quaternion.magnitude':'Quaternion norm','mathutils.Quaternion.normalize':'Normalize in place','mathutils.Quaternion.normalized':'Normalized copy',
'mathutils.Quaternion.conjugate':'Conjugate in place','mathutils.Quaternion.conjugated':'Conjugated copy','mathutils.Quaternion.invert':'Invert in place','mathutils.Quaternion.inverted':'Inverted copy',
'mathutils.Quaternion.to_matrix':'3x3 rotation matrix','mathutils.Quaternion.to_euler':'Euler conversion in six orders','mathutils.Quaternion.dot':'Quaternion dot product',
'mathutils.Vector.to_track_quat':'Track signed local axis toward vector with world Z as up; quaternion signs are rotation-equivalent',
'bpy.types.Object.rotation_euler.x':'Mutable X Euler angle','bpy.types.Object.rotation_euler.y':'Mutable Y Euler angle','bpy.types.Object.rotation_euler.z':'Mutable Z Euler angle',
'bpy.types.Object.rotation_euler.to_matrix':'Object rotation matrix','bpy.types.Object.rotation_euler.to_quaternion':'Object rotation quaternion',
}
def close(a,b):return all(abs(x-y)<1e-5 for x,y in zip(a,b))
def flat(m):return [v for row in m for v in row]
for order in ('XYZ','XZY','YXZ','YZX','ZXY','ZYX'):
 e=Euler((.2,-.3,.4),order);assert e.order==order
 m=e.to_matrix();q=e.to_quaternion();assert close(flat(m),flat(q.to_matrix()))
 assert close(flat(m),flat(m.to_euler(order).to_matrix()))
 assert close(flat(m),flat(q.to_euler(order).to_matrix()))
 ec=e.copy();ec.x=.9;assert abs(e.x-.2)<1e-6;ec.zero();assert tuple(ec)==(0,0,0)
for n in (2,3,4):
 m=Matrix.Identity(n);assert m.determinant()==1
 assert close(flat(m),flat(m.inverted()))
 mc=m.copy();mc[0][0]=2;assert m[0][0]==1 and mc[0][0]==2
 d=Matrix.Diagonal(tuple(range(1,n+1)));assert abs(d.determinant()-math.factorial(n))<1e-5
 assert close(flat(d@d.inverted()),flat(m))
t=Matrix.Translation((1,2,3));assert tuple(t.translation)==(1,2,3)
t.translation.z=4;assert tuple(t@Vector((2,3,4)))==(3,5,8)
t.translation=(0,0,0);assert close(flat(t),flat(Matrix.Identity(4)))
r=Matrix.Rotation(.4,4,'Z');assert close(flat(r.transposed()),flat(r.inverted()))
r.transpose();r.invert();assert close(flat(r),flat(Matrix.Rotation(.4,4,'Z')))
assert close(flat(Matrix.Scale(2,3)),flat(Matrix.Diagonal((2,2,2))))
assert close(flat(Matrix.Scale(3,3,Vector((1,0,0)))),flat(Matrix.Diagonal((3,1,1))))
q=Quaternion((0,0,1),.4);v=Vector((1,2,3));assert close(q@v,q.to_matrix()@v)
c=q.copy();c.conjugate();assert close(c,q.conjugated());c.invert();assert close(c,q)
c=Quaternion((2,1,3,4));c.normalize();assert abs(c.magnitude-1)<1e-6
assert abs(c.dot(c)-1)<1e-6
for d in ((1,2,3),(0,0,-1),(0,0,1),(1,0,0),(0,1,0),(-2,3,-4)):
 q=Vector(d).to_track_quat('-Z','Y');assert close(q@Vector((0,0,-1)),Vector(d).normalized())
bpy.ops.mesh.primitive_cube_add();o=bpy.context.object
o.rotation_euler=Vector((2,-4,-3)).to_track_quat('-Z','Y').to_euler()
o.rotation_euler.z+=.1
assert close(flat(o.rotation_euler.to_matrix()),flat(o.rotation_euler.to_quaternion().to_matrix()))

assert tuple(Quaternion((0,0,0,0)).normalized())==(0,1,0,0)
assert tuple(Quaternion((0,0,0),1))==(1,0,0,0)

assert tuple(Quaternion((1e-30,0,0,0)).normalized())==(0,1,0,0)
assert tuple(Quaternion((1e-30,0,0,0)).inverted())==tuple(Quaternion((1e-30,0,0,0)))
assert abs(Quaternion((0,0,0,0)).to_euler().x-math.pi)<1e-6
assert tuple(Matrix.Diagonal((0,0,0)).to_quaternion())==(1,0,0,0)
assert abs(Matrix.Diagonal((-1,1,1)).to_euler().z-math.pi)<1e-6
assert close(flat(Quaternion((2,1,3,4)).to_euler().to_matrix()),flat(Quaternion((2,1,3,4)).normalized().to_matrix()))
