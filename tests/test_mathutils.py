import unittest
import test_cli
from pathlib import Path
class Mathutils(unittest.TestCase):
    setUp=test_cli.CLI.setUp;tearDown=test_cli.CLI.tearDown;hb=test_cli.CLI.hb;script=test_cli.CLI.script
    def test_tracking_views_and_scene_restore(self):
        self.hb('run',self.script('''import bpy
from mathutils import Vector,Matrix
bpy.ops.object.camera_add(location=(4,-6,4));o=bpy.context.object
o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
r=o.rotation_euler;r.z+=.25
q=r.to_quaternion();direction=q@Vector((0,0,-1))
assert abs(direction.length-1)<1e-5
m=Matrix.Translation((1,2,3));v=m.translation;v.y=5
assert tuple(m@Vector((0,0,0)))==(1,5,3)
assert tuple(Matrix.Identity(3)@Vector((1,2,3)))==(1,2,3)
bpy.context.scene.camera=o
'''))
        self.hb('run',self.script('''import bpy
assert abs(bpy.context.scene.camera.rotation_euler.z-.8380026)<1e-5
'''))
        self.hb('render','--views','camera','--size','32')
    def test_singular_fallback_and_rotation_orders(self):
        self.hb('run',self.script('''from mathutils import Matrix,Quaternion,Euler,Vector
m=Matrix.Diagonal((1,0,1));fallback=Matrix.Identity(3)
assert m.inverted(fallback) is fallback
for order in ('XYZ','XZY','YXZ','YZX','ZXY','ZYX'):
    e=Euler((.5,-.7,1.1),order);r=e.to_matrix().to_euler(order).to_matrix()
    assert max(abs(a-b) for x,y in zip(e.to_matrix(),r) for a,b in zip(x,y))<1e-5
assert tuple(Vector().to_track_quat())==(1,0,0,0)
assert tuple(Quaternion((0,0,0,0)).normalized())==(0,1,0,0)
assert abs(Quaternion((1,2,3,4)).normalized().magnitude-1)<1e-6
'''))
    def test_tracking_axis_fixture(self):
        fixture=Path(__file__).resolve().parents[1]/'compat/fixtures/tracking_axes.json'
        self.hb('run',self.script('''import json
from mathutils import Vector
records=json.load(open('''+repr(str(fixture))+'''))
for row in records:
    matrix=Vector(row['d']).to_track_quat(row['track'],row['up']).to_matrix()
    assert max(abs(x-y) for a,b in zip(matrix,row['matrix']) for x,y in zip(a,b))<1e-5
'''))
    def test_invalid_math_keeps_revision(self):
        self.hb('run',self.script('import bpy\nbpy.ops.mesh.primitive_cube_add()'))
        before=(self.path/'scene.hb').read_bytes()
        for source in ("Matrix.Diagonal((1,0,1)).inverted()","Matrix.Identity(5)","Euler((1,2,3),'BAD')","Vector((1,2,3)).to_track_quat('X','X')","Quaternion((1,2))","Matrix.Identity(3)@Vector((1,2))"):
            self.hb('run',self.script('from mathutils import Matrix,Vector,Quaternion,Euler\n'+source),ok=False)
            self.assertEqual((self.path/'scene.hb').read_bytes(),before)
