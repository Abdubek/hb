"""Actual Blender 4.5.9 records captured before the Lane 2 math implementation."""
import json,math,os
from mathutils import Matrix,Quaternion,Vector
with open(os.path.join(os.path.dirname(__file__),'../fixtures/mathutils-lane2-reference.json')) as f:reference=json.load(f)
def plain(value):
    if isinstance(value,(Matrix,Quaternion,Vector,tuple,list)):return [plain(v) for v in value]
    return value

def check(function,expected):
    if isinstance(expected,dict) and 'error' in expected:
        try:function()
        except Exception as e:assert type(e).__name__==expected['error'],(type(e).__name__,expected)
        else:raise AssertionError('Expected '+expected['error'])
    else:
        actual=plain(function())
        def close(a,b):
            if isinstance(b,list):
                assert len(a)==len(b),(a,b)
                for x,y in zip(a,b):close(x,y)
            else:assert math.isclose(a,b,rel_tol=2e-6,abs_tol=2e-6),(a,b)
        close(actual,expected)
for row in reference['rectangular']:
    m=Matrix(row['values'])
    assert len(m)==row['rows'] and len(m[0])==row['cols']
    check(lambda:m.copy(),row['values'])
    edited=Matrix(row['values']);edited[0]=list(edited[0]);edited[0][0]=1;assert edited[0][0]==1
    check(lambda:m.to_3x3(),row['to_3x3'])
    check(lambda:m.to_4x4(),row['to_4x4'])
    if row['rows']!=row['cols']:
        check(lambda:m.copy().transposed(),row['transposed'])
        check(lambda:m.copy().transpose(),row['transpose'])
        check(lambda:m.determinant(),row['determinant'])
        check(lambda:m.inverted(),row['inverted'])
        check(lambda:m.decompose(),row['decompose'])
        check(lambda:m.translation,row['translation'])
    for n in (2,3,4):
        # Blender 4.5 reads uninitialized memory for 2x4 @ 3-vector; excluded.
        if row['rows']==2 and row['cols']==4 and n==3:continue
        check(lambda:m@Vector(range(1,n+1)),row['vector'+str(n)])
    other=Matrix([[int(i==j) for j in range(2)] for i in range(row['cols'])])
    check(lambda:m@other,[[r[0],r[1]] for r in row['values']])
for row in reference['slerp']:
    a=Quaternion(row['a']);b=Quaternion(row['b'])
    check(lambda:a.slerp(b,row['t']),row['value'])
    assert tuple(a)==tuple(Quaternion(row['a'])) and tuple(b)==tuple(Quaternion(row['b']))
for row in reference['decompose']:check(lambda:Matrix(row['matrix']).decompose(),row['value'])
with open(os.path.join(os.path.dirname(__file__),'../fixtures/mathutils-lane2-fuzz-reference.json')) as f:fuzz=json.load(f)
for row in fuzz['cases']:
    if row['op']=='decompose':check(lambda:Matrix(row['matrix']).decompose(),row['result'])
    else:check(lambda:Quaternion(row['a']).slerp(Quaternion(row['b']),row['t']),row['result'])
# Include a normal scene so this fixture also runs through the existing GLB gate.
import bpy
bpy.ops.mesh.primitive_cube_add()
