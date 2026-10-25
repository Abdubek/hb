import unittest,json,zlib
import test_cli

class MatrixWorld(unittest.TestCase):
    setUp=test_cli.CLI.setUp;tearDown=test_cli.CLI.tearDown;hb=test_cli.CLI.hb;script=test_cli.CLI.script

    def test_parented_affine_blender_references(self):
        references=json.loads(zlib.decompress((test_cli.ROOT/'compat/fixtures/matrix-world-reference.json.zlib').read_bytes()))
        script=self.script('references='+repr(references)+'\n'+(test_cli.ROOT/'compat/matrix_world_probe.py').read_text())
        self.hb('check',script)
        self.hb('run',script)

    def test_snapshot_assignment_and_atomic_invalid_basis(self):
        self.hb('run',self.script('''import bpy
from mathutils import Matrix,Vector
bpy.ops.mesh.primitive_cube_add();obj=bpy.context.object
snapshot=obj.matrix_world;snapshot.translation=(2,3,4)
assert tuple(obj.location)==(0,0,0)
obj.matrix_world=snapshot
assert tuple(obj.location)==(2,3,4)
assert tuple(obj.matrix_world @ Vector((1,0,0)))==(3,3,4)
old=[list(r) for r in obj.matrix_world]
for bad in (Matrix.Identity(3),Matrix(((1,0,0,0),(0,1,0,0),(0,0,1,0),(0,0,.1,1))),Matrix.Translation((1e7,0,0))):
    try:obj.matrix_world=bad
    except Exception:pass
    else:raise AssertionError('Invalid matrix accepted')
    assert [list(r) for r in obj.matrix_world]==old
parent=bpy.data.objects.new('Parent',None);bpy.context.collection.objects.link(parent)
obj.parent=parent;parent.scale=(0,1,1);old=tuple(obj.location)
try:obj.matrix_world=Matrix.Identity(4)
except Exception:pass
else:raise AssertionError('Singular parent accepted')
assert tuple(obj.location)==old
'''))
