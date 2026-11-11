"""Vector.angle must match Blender and drive the same mesh through CLI/MCP."""
import unittest

import test_cli
import test_server


class VectorAngle(unittest.TestCase):
    setUp = test_cli.CLI.setUp
    tearDown = test_cli.CLI.tearDown
    hb = test_cli.CLI.hb
    script = test_cli.CLI.script
    exchange = test_server.Server.exchange

    def test_blender_reference_and_angle_driven_export(self):
        fixture = test_cli.ROOT / 'compat/golden/m3_vector_angle.py'
        self.hb('check', fixture)
        self.hb('run', fixture, '--out', 'angles.glb')
        self.hb('run', self.script('''import bpy
bpy.ops.mesh.primitive_cube_add()
bpy.context.object.name='Angles'
for vertex in bpy.context.object.data.vertices:vertex.co.z+=2
'''), '--scene', 'control.hb', '--out', 'control.glb')
        actual = test_cli.revision(self.path / 'scene.hb')['scene']
        control = test_cli.revision(self.path / 'control.hb')['scene']
        self.assertEqual(actual, control)
        self.assertEqual((self.path / 'angles.glb').read_bytes(),
                         (self.path / 'control.glb').read_bytes())

    def test_parameters_fallback_provenance_and_rollback(self):
        setup = 'import bpy\nfrom mathutils import Vector\nv=Vector((1,0,0))\n'
        for expression, expected in (
            ('v.angle()', 'mathutils.Vector.angle'),
            ('v.angle(other=v)', 'mathutils.Vector.angle'),
            ('v.angle(v,fallback=0)', 'mathutils.Vector.angle'),
            ('v.angle(v,0,1)', 'mathutils.Vector.angle'),
            ('value=v.angle(v,bpy.context.object)\nvalue.unsupported_magic()',
             'bpy.types.Object.unsupported_magic'),
        ):
            with self.subTest(expression=expression):
                result = self.hb('check', self.script(setup + expression), ok=False)
                self.assertTrue(any(expected in e['message'] for e in result['errors']))
        self.hb('run', self.script(setup + '''
for operation in (lambda:v.angle(), lambda:v.angle(other=v),
                  lambda:v.angle(v,fallback=0), lambda:v.angle(v,0,1)):
    try:operation()
    except TypeError:pass
    else:raise AssertionError('Invalid arguments accepted')
bpy.ops.mesh.primitive_cube_add()
'''))
        before = (self.path / 'scene.hb').read_bytes()
        history = set((self.path / 'scene.hb.revisions').iterdir())
        for expression in ('Vector((0,0,0,9)).angle((1,0,0,7))',
                           'v.angle((1,0))', 'v.angle(None)'):
            with self.subTest(expression=expression):
                result = self.hb('run', self.script(
                    setup + 'bpy.context.object.location.x=9\n' + expression), ok=False)
                self.assertEqual(result['error']['code'], 'SCRIPT_ERROR')
                self.assertEqual((self.path / 'scene.hb').read_bytes(), before)
                self.assertEqual(set((self.path / 'scene.hb.revisions').iterdir()), history)
                self.assertFalse((self.path / 'scene.hb.lock').exists())

    def test_mcp_executes_angle_driven_geometry(self):
        source = (test_cli.ROOT / 'compat/golden/m3_vector_angle.py').read_text()
        replies = self.exchange('--mcp', [
            test_server.request(0, 'initialize', {'protocolVersion': '2025-11-25',
                                                 'clientInfo': {}, 'capabilities': {}}),
            {'jsonrpc': '2.0', 'method': 'notifications/initialized'},
            test_server.request(1, 'tools/call', {'name': 'hb_run', 'arguments': {
                'code': source.replace("os.path.dirname(__file__)",
                                       repr(str(test_cli.ROOT / 'compat/golden'))),
                'args': ['--out', 'mcp.glb']}}),
            test_server.request(2, 'tools/call', {'name': 'hb_query',
                                                'arguments': {'args': ['stats']}}),
        ], self.path)
        self.assertFalse(replies[1]['result']['isError'], replies[1])
        self.assertEqual(replies[2]['result']['structuredContent']['result']['objects'], 1)
        positions = test_cli.revision(self.path / 'scene.hb')['scene']['meshes'][0]['vertices']
        self.assertEqual(sorted({v[2] for v in positions}), [1, 3])
        self.assertEqual((self.path / 'mcp.glb').read_bytes()[:4], b'glTF')
