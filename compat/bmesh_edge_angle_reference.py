"""Capture unsigned BMesh edge angles from Blender.

blender --background --factory-startup --python-exit-code 1 \
  --python compat/bmesh_edge_angle_reference.py -- /tmp/edge-angle-reference.json
"""
import json
import math
from pathlib import Path
import random
import sys

import bmesh
import bpy
from mathutils import Quaternion, Vector


def wedge(angle):
    return [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, -math.cos(angle), math.sin(angle))]


faces = [(0, 1, 2), (1, 0, 3)]
cases = []
for angle in (0, 1e-8, 1e-6, .001, .2, .7, math.pi/2, 2.4, math.pi-1e-6, math.pi):
    for sign in (-1, 1):
        cases.append((wedge(sign*angle), faces))
for c, d in (((2, 0, 0), (0, 0, 1)), ((0, 1, 0), (2, 0, 0)),
             ((2, 0, 0), (-1, 0, 0))):
    cases.append(([(0, 0, 0), (1, 0, 0), c, d], faces))
cases.append((wedge(0), [(0, 1, 2), (0, 1, 3)]))
rng = random.Random(20261109)
for _ in range(24):
    rotation = Quaternion([rng.uniform(-1, 1) for _ in range(3)], rng.uniform(-3, 3))
    offset = Vector([rng.uniform(-2, 2) for _ in range(3)])
    scale = rng.uniform(.5, 10)
    cases.append(([list((rotation @ Vector(p))*scale+offset)
                   for p in wedge(rng.uniform(0, math.pi))], faces))

records = []
for points, indices in cases:
    bm = bmesh.new()
    verts = [bm.verts.new(p) for p in points]
    for face in indices:
        bm.faces.new([verts[i] for i in face])
    edge = next(e for e in bm.edges if set(e.verts) == set(verts[:2]))
    fresh = edge.calc_face_angle()
    bm.normal_update()
    records.append({'vertices': [list(v.co) for v in verts], 'faces': indices,
                    'fresh_angle': fresh, 'angle': edge.calc_face_angle(),
                    'normals': [list(f.normal) for f in bm.faces]})
    bm.free()
Path(sys.argv[sys.argv.index('--')+1]).write_text(
    json.dumps({'blender': bpy.app.version_string, 'cases': records}, indent=2) + '\n')
print(f'EDGE_ANGLE_REFERENCE_OK: {len(records)} cases')
