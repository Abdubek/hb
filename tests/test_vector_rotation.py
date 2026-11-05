"""Rotation differences must execute, preserve operands and retain API types."""
import json
import struct
import unittest

import test_cli
from normalize import revision


def exported_positions(path):
    data = path.read_bytes()
    length = struct.unpack_from('<I', data, 12)[0]
    doc = json.loads(data[20:20+length])
    binary = data[28+length:]
    result = []
    for mesh in doc['meshes']:
        for primitive in mesh['primitives']:
            accessor = doc['accessors'][primitive['attributes']['POSITION']]
            view = doc['bufferViews'][accessor['bufferView']]
            offset = view.get('byteOffset', 0) + accessor.get('byteOffset', 0)
            assert accessor['componentType'] == 5126 and accessor['type'] == 'VEC3'
            result.extend(struct.unpack_from('<3f', binary, offset + i*view.get('byteStride', 12))
                          for i in range(accessor['count']))
    return result


class VectorRotation(unittest.TestCase):
    setUp = test_cli.CLI.setUp
    tearDown = test_cli.CLI.tearDown
    hb = test_cli.CLI.hb
    script = test_cli.CLI.script

    def test_blender_reference_and_exported_mesh(self):
        fixture = test_cli.ROOT / 'compat/golden/m3_vector_rotation_difference.py'
        self.hb('check', fixture)
        self.hb('run', fixture, '--out', 'rotation.glb')
        self.hb('run', self.script('''import bpy
from mathutils import Matrix
bpy.ops.mesh.primitive_cube_add()
matrix=Matrix(((0,0,1),(0,1,0),(-1,0,0)))
for vertex in bpy.context.object.data.vertices:vertex.co=matrix @ vertex.co
'''), '--scene', 'control.hb', '--out', 'control.glb')
        actual = revision(self.path / 'scene.hb')['scene']['meshes'][0]
        control = revision(self.path / 'control.hb')['scene']['meshes'][0]
        self.assertEqual(actual['faces'], control['faces'])
        self.assertEqual(actual['uv_layers'], control['uv_layers'])
        self.assertEqual(len(actual['vertices']), len(control['vertices']))
        for a, b in zip(actual['vertices'], control['vertices']):
            self.assertLessEqual(max(abs(x-y) for x, y in zip(a, b)), 2e-6)
        actual = exported_positions(self.path / 'rotation.glb')
        control = exported_positions(self.path / 'control.glb')
        self.assertEqual(len(actual), len(control))
        # Float32 rotation can change the lexicographic order of cube corners.
        # Match the full position multiset, including duplicated seam vertices.
        for a in actual:
            match = next((i for i, b in enumerate(control)
                          if max(abs(x-y) for x, y in zip(a, b)) <= 2e-6), None)
            self.assertIsNotNone(match, a)
            control.pop(match)
        self.assertEqual(control, [])

    def test_checker_keeps_quaternion_and_rotated_vector_provenance(self):
        for expression, expected in (
            ('q.unsupported_magic()', 'mathutils.Quaternion.unsupported_magic'),
            ('q.to_matrix().unsupported_magic()', 'mathutils.Matrix.unsupported_magic'),
            ('(q @ Vector((0,0,1))).unsupported_magic()', 'mathutils.Vector.unsupported_magic'),
            ('(q @ Quaternion()).length', 'mathutils.Quaternion.length'),
        ):
            with self.subTest(expression=expression):
                result = self.hb('check', self.script('''from mathutils import Vector,Quaternion
q=Vector((0,0,1)).rotation_difference(Vector((1,0,0)))
''' + expression), ok=False)
                self.assertTrue(any(expected in e['message'] for e in result['errors']))

    def test_invalid_inputs_leave_views_and_scene_unchanged(self):
        self.hb('run', self.script('import bpy\nbpy.ops.mesh.primitive_cube_add()'))
        self.hb('run', self.script('''import bpy
from mathutils import Vector
source=bpy.context.object.location
before=tuple(source)
for bad in (float('nan'),float('inf'),1e7):
    target=Vector((1,0,0,bad))
    for a,b in ((source,target),(target,source)):
        try:a.rotation_difference(b)
        except Exception as error:assert type(error).__name__=='UnsupportedError'
        else:raise AssertionError('Invalid components accepted')
        assert tuple(source)==before
for bad in (None,3,'bad'):
    try:source.rotation_difference(bad)
    except TypeError:pass
    else:raise AssertionError('Invalid argument accepted')
'''))
        before = (self.path / 'scene.hb').read_bytes()
        result = self.hb('run', self.script('''import bpy
from mathutils import Vector
bpy.context.object.location.x=9
Vector((0,0,1)).rotation_difference(Vector((1e7,0,0)))
'''), ok=False)
        self.assertEqual(result['error']['code'], 'UNSUPPORTED_API')
        self.assertEqual((self.path / 'scene.hb').read_bytes(), before)
