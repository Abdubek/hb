"""Capture Vector.angle observations without using Blender implementation code.

blender --background --factory-startup --python-exit-code 1 \
  --python compat/vector_angle_reference.py -- /tmp/vector-angle-reference.json
"""
import json
from pathlib import Path
import random
import sys

import bpy
from mathutils import Vector

pairs=[]
for dimension in (2,3,4):
    def vector(x,y=0):return (x,y,0,7)[:dimension]
    for a,b in ((vector(1),vector(0,1)),(vector(1),vector(1)),
                (vector(1),vector(-1)),(vector(0),vector(1)),
                (vector(1),vector(0)),(vector(0),vector(0))):
        pairs.append((a,b))
    for epsilon in (1e-7,1e-5,1e-4,.001,.01):
        for sign in (1,-1):pairs.append((vector(1),vector(sign,epsilon)))
    for scale in (1e-45,1e-38,1e-30,1e-20,1e-17,1e-10,1e10,1e20,1e38):
        pairs.append((vector(scale),vector(0,scale)))
    a=(1,2,3,8)[:dimension]
    pairs.extend(((a,a),(a,tuple(-x for x in a))))
rng=random.Random(20261111)
for i in range(72):
    dimension=2+i%3
    a=[rng.uniform(-1,1)*10**rng.uniform(-10,10) for _ in range(dimension)]
    b=[rng.uniform(-1,1)*10**rng.uniform(-10,10) for _ in range(dimension)]
    pairs.append((a,b))
for a,b in (((1,0,0,1),(0,1,0,1)),((0,0,0,1),(0,0,0,2))):pairs.append((a,b))
records=[]
for a,b in pairs:
    source,target=Vector(a),Vector(b)
    before=(list(source),list(target))
    row={'a':list(source),'b':list(target)}
    try:row['angle']=source.angle(target)
    except ValueError:row['error']='ValueError'
    assert before==(list(source),list(target))
    records.append(row)
Path(sys.argv[sys.argv.index('--')+1]).write_text(
    json.dumps({'blender':bpy.app.version_string,'cases':records},indent=2)+'\n')
print('VECTOR_ANGLE_REFERENCE_OK: %d cases'%len(records))
