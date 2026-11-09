"""Blender edge-angle references, cached normals, fallbacks and real editing."""
import json
import math
import os
import bmesh

with open(os.path.join(os.path.dirname(__file__), '../fixtures/bmesh-edge-angle-reference.json')) as source:
    reference = json.load(source)
for record in reference['cases']:
    bm = bmesh.new()
    verts = [bm.verts.new(p) for p in record['vertices']]
    for face in record['faces']:
        bm.faces.new([verts[i] for i in face])
    edge = next(e for e in bm.edges if set(e.verts) == set(verts[:2]))
    assert abs(edge.calc_face_angle()-record['fresh_angle']) <= 2e-6
    bm.normal_update()
    before = [tuple(v.co) for v in verts]
    assert abs(edge.calc_face_angle()-record['angle']) <= 2e-6, record
    assert abs(edge.calc_face_angle(None)-record['angle']) <= 2e-6
    assert [tuple(v.co) for v in verts] == before
    bm.free()

bm = bmesh.new()
a, b, c, d, e = [bm.verts.new(p) for p in ((0,0,0),(1,0,0),(0,1,0),(0,-1,0),(0,0,1))]
edge = bm.edges.new((a,b))
fallback = {'unchanged': True}
for count in range(4):
    if count != 2:
        try:edge.calc_face_angle()
        except ValueError:pass
        else:raise AssertionError('Missing radial faces accepted')
        assert edge.calc_face_angle(None) is None
        assert edge.calc_face_angle(fallback) is fallback
        assert edge.calc_face_angle(0) == 0
    if count < 3:
        bm.faces.new(((a,b,c),(b,a,d),(a,b,e))[count])
        bm.normal_update()
bm.faces.remove(list(bm.faces)[-1])
assert edge.calc_face_angle() == 0
d.co = (0,0,1)
assert edge.calc_face_angle() == 0  # Normals remain cached until normal_update.
bm.normal_update()
assert abs(edge.calc_face_angle()-math.pi/2) < 2e-6
bm.edges.remove(edge)
try:edge.calc_face_angle(fallback)
except ReferenceError:pass
else:raise AssertionError('Removed edge accepted')
edge = bm.edges.new((a,b))
bm.free()
try:edge.calc_face_angle(None)
except ReferenceError:pass
else:raise AssertionError('Freed edge accepted')

# The angle selects only the folded join, leaving the flat join untouched.
import bpy
bm = bmesh.new()
verts = [bm.verts.new(p) for p in ((0,0,0),(1,0,0),(0,1,0),(1,1,0),(1,1,1))]
for face in ((0,1,2),(1,3,2),(1,4,3)):
    bm.faces.new([verts[i] for i in face])
bm.normal_update()
selected = {v for edge in bm.edges if edge.calc_face_angle(0) > .5 for v in edge.verts}
assert selected == {verts[1], verts[3]}
bmesh.ops.translate(bm, verts=list(selected), vec=(0,0,2))
mesh = bpy.data.meshes.new('Angles')
bm.to_mesh(mesh)
obj = bpy.data.objects.new('Angles', mesh)
bpy.context.collection.objects.link(obj)
bm.free()
