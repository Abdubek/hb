"""Capture Vector.rotate observations without Blender implementation code.

blender --background --factory-startup --python-exit-code 1 \\
  --python compat/vector_rotate_reference.py -- /tmp/vector-rotate-reference.json
"""
import json
from pathlib import Path
import random
import sys

import bpy
from mathutils import Euler,Matrix,Quaternion,Vector

rotations = [
    {'kind':'matrix','value':[[1,2],[3,4]]},
    {'kind':'matrix','value':[[0,-1],[1,0]]},
    {'kind':'matrix','value':[[0,0],[0,0]]},
    {'kind':'matrix','value':[[1e-20,0],[0,1e-16]]},
    {'kind':'matrix','value':[[1,2,3],[4,5,6],[7,8,9]]},
    {'kind':'matrix','value':[[-2,0,0],[0,3,0],[0,0,4]]},
    {'kind':'matrix','value':[[0,0,0],[0,0,0],[0,0,0]]},
    {'kind':'matrix','value':[[1e-20,0,0],[0,1e-16,0],[0,0,1e-18]]},
    {'kind':'matrix','value':[[1,2,3,9],[4,5,6,8],[7,8,9,7]]},
    {'kind':'matrix','value':[[1,2,3],[4,5,6],[7,8,9],[9,8,7]]},
    {'kind':'matrix','value':[[1,0,0,8],[0,1,0,-9],[0,0,1,10],[2,3,4,5]]},
    {'kind':'matrix','value':[[1,2,3],[4,5,6]]},
    {'kind':'quaternion','value':[1,2,3,4]},
    {'kind':'quaternion','value':[0,0,0,0]},
    {'kind':'quaternion','value':[-2,0,0,0]},
    {'kind':'quaternion','value':[1e-20,0,0,0]},
    {'kind':'quaternion','value':[1e6,-1e6,1e6,-1e6]},
    *[{'kind':'euler','value':[.5,-.7,1.1],'order':order}
      for order in ('XYZ','XZY','YXZ','YZX','ZXY','ZYX')],
]
rng=random.Random(20261121)
for i in range(12):
    kind=('matrix','quaternion','euler')[i%3]
    if kind=='matrix':value=[[rng.uniform(-10,10) for _ in range(3)] for _ in range(3)]
    elif kind=='quaternion':value=[rng.uniform(-10,10) for _ in range(4)]
    else:value=[rng.uniform(-3,3) for _ in range(3)]
    rotations.append({'kind':kind,'value':value})
records=[]
for rotation in rotations:
    for dimension in (2,3,4):
        source=Vector((1.25,-2.5,.75,7)[:dimension])
        kind,value=rotation['kind'],rotation['value']
        other=Matrix(value) if kind=='matrix' else Quaternion(value) if kind=='quaternion' else Euler(value,rotation.get('order','XYZ'))
        before=[list(row) for row in other] if kind=='matrix' else list(other)
        row={'vector':list(source),'rotation':rotation}
        try:
            assert source.rotate(other) is None
            row['result']=list(source)
        except (TypeError,ValueError) as error:
            row['error']=type(error).__name__
            assert list(source)==row['vector']
        assert before==([list(row) for row in other] if kind=='matrix' else list(other))
        records.append(row)
output={'blender':bpy.app.version_string,'cases':records}
Path(sys.argv[sys.argv.index('--')+1]).write_text(
    '{"blender": '+json.dumps(output['blender'])+', "cases": [\n'+
    ',\n'.join(json.dumps(row) for row in records)+'\n]}\n')
print('VECTOR_ROTATE_REFERENCE_OK: %d cases'%len(records))
