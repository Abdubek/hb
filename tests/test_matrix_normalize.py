"""Column normalization must execute correctly and retain checker provenance."""
import unittest

import test_cli


class MatrixNormalize(unittest.TestCase):
    setUp = test_cli.CLI.setUp
    tearDown = test_cli.CLI.tearDown
    hb = test_cli.CLI.hb
    script = test_cli.CLI.script

    def test_blender_reference_and_mesh_transform(self):
        fixture = test_cli.ROOT / 'compat/golden/m3_matrix_normalize.py'
        self.hb('check', fixture)
        self.hb('run', fixture, '--out', 'normalized.glb')
        self.assertEqual(self.hb('query', 'stats')['result']['objects'], 1)
        self.assertEqual((self.path / 'normalized.glb').read_bytes()[:4], b'glTF')

    def test_checker_retains_normalized_matrix_and_row_types(self):
        source = self.script('''from mathutils import Matrix,Vector
direction=(Matrix.Identity(3).normalized() @ Vector((1,2,3))).normalized()
assert abs(direction.length-1)<1e-6
assert direction.cross(Vector((0,0,1))).length>0
product=(Matrix.Identity(3).normalized() @ Matrix.Identity(3)).normalized()
assert product.determinant()==1
import bpy
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object
obj.scale=(2,3,4)
def world_point(obj, point):return obj.matrix_world @ Vector(point)
axis=(world_point(obj,(1,0,0))-world_point(obj,(0,0,0))).normalized()
assert axis.length==1 and axis.cross(Vector((0,1,0))).length==1
assert (obj.matrix_world.normalized() @ Vector((1,0,0))).length==1
''')
        self.hb('check', source)
        self.hb('run', source)
        for expression in (
            'Matrix.Identity(3).normalized().unsupported_magic()',
            'Matrix.Identity(4).normalized()[0].unsupported_magic()',
            'm=Matrix.Identity(3).normalized()\nm.normalized().unsupported_magic()',
            '(Matrix.Identity(3).normalized() @ Vector((1,2,3))).unsupported_magic()',
            '(Matrix.Identity(3).normalized() @ Matrix.Identity(3)).length',
        ):
            with self.subTest(expression=expression):
                result = self.hb('check', self.script('from mathutils import Matrix,Vector\n' + expression), ok=False)
                expected = 'mathutils.Matrix.length' if expression.endswith('.length') else 'unsupported_magic'
                self.assertTrue(any(expected in error['message'] for error in result['errors']))
        result = self.hb('check', self.script('''import bpy
from mathutils import Matrix,Vector
matrix=Matrix.Identity(3) if True else bpy.context.object.unsupported_magic
direction=(matrix @ Vector((1,2,3))).normalized()
'''), ok=False)
        self.assertTrue(any('unsupported_magic' in error['message'] for error in result['errors']))

    def test_limits_validate_before_mutation_and_preserve_revision(self):
        self.hb('run', self.script('import bpy\nbpy.ops.mesh.primitive_cube_add()'))
        self.hb('run', self.script('''from mathutils import Matrix
for bad in (float('nan'), float('inf'), 1e7):
    for size in (3, 4):
        matrix=Matrix.Identity(size)
        matrix[size-1][size-1]=bad
        original=repr([list(row) for row in matrix])
        for operation in (matrix.normalize, matrix.normalized):
            try:operation()
            except Exception as error:assert type(error).__name__=='UnsupportedError'
            else:raise AssertionError('Out-of-contract normalization accepted')
            assert repr([list(row) for row in matrix])==original
for rows in (2, 3, 4):
    for columns in (2, 3, 4):
        if rows==columns and rows in (3,4):continue
        matrix=Matrix([[1]*columns for _ in range(rows)])
        original=[list(row) for row in matrix]
        for operation in (matrix.normalize, matrix.normalized):
            try:operation()
            except ValueError:pass
            else:raise AssertionError('Unsupported dimensions accepted')
            assert [list(row) for row in matrix]==original
'''))
        # An unhandled rejection also leaves the previously saved scene unchanged.
        before = (self.path / 'scene.hb').read_bytes()
        result = self.hb('run', self.script('''import bpy
from mathutils import Matrix
bpy.context.object.location.x=9
Matrix.Diagonal((1,1,1e7)).normalize()
'''), ok=False)
        self.assertEqual(result['error']['code'], 'UNSUPPORTED_API')
        self.assertEqual((self.path / 'scene.hb').read_bytes(), before)
