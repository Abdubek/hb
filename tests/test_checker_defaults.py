"""API-bearing helper defaults must pass through the same checks as arguments."""
import unittest

import test_cli
import test_server


class CheckerDefaults(unittest.TestCase):
    setUp = test_cli.CLI.setUp
    tearDown = test_cli.CLI.tearDown
    hb = test_cli.CLI.hb
    script = test_cli.CLI.script
    exchange = test_server.Server.exchange

    def test_omitted_defaults_retain_api_types(self):
        setup = 'import bpy\nfrom mathutils import Vector, Matrix\n'
        cases = [
            ('def f(v=Vector((1,2,3))):\n    return v.to_tuple()\nf()',
             'mathutils.Vector.to_tuple'),
            ('def f(v=Vector((1,2,3)), /):\n    return v.to_tuple()\nf()',
             'mathutils.Vector.to_tuple'),
            ('def f(*, obj=bpy.context.object):\n    return obj.unsupported_magic()\nf()',
             'bpy.types.Object.unsupported_magic'),
            ('def f(required, v=Vector((1,2,3)), *, flag):\n    return v.to_tuple()\n'
             'f(1, flag=True)', 'mathutils.Vector.to_tuple'),
            ('value=(1,2,3)\ndef outer():\n    value=Vector((1,2,3))\n'
             '    def f(value=value):\n        return value.to_tuple()\n'
             '    return f()\nouter()', 'mathutils.Vector.to_tuple'),
            ('def make():return Matrix.Identity(3)\n'
             'def f(matrix=make()):return matrix.unsupported_magic()\nf()',
             'mathutils.Matrix.unsupported_magic'),
            ('def f(v=[Vector((1,2,3))]):return v\nf()[0].to_tuple()',
             'mathutils.Vector.to_tuple'),
            ('points=[]\ndef f(values=points):values.append(Vector((1,2,3)))\n'
             'f()\npoints[0].to_tuple()', 'mathutils.Vector.to_tuple'),
            # Defaults still execute when the caller supplies an override.
            ('def outer():\n    import bpy as local\n'
             '    def f(v=local.unsupported_magic):return v\n'
             '    return f(1)\nouter()', 'bpy.unsupported_magic'),
            # A positional-only name in **kwargs does not override its default.
            ('def f(v=Vector((1,2,3)), /, **kwargs):return v.to_tuple()\nf(v=1)',
             'mathutils.Vector.to_tuple'),
        ]
        for source, expected in cases:
            with self.subTest(source=source):
                errors = self.hb('check', self.script(setup + source), ok=False)['errors']
                self.assertTrue(any(expected in error['message'] for error in errors), errors)

    def test_definition_scope_and_overrides_match_control_scene_and_export(self):
        source = test_cli.ROOT / 'compat/golden/m3_checker_defaults.py'
        self.hb('check', source)
        self.hb('run', source, '--out', 'defaults.glb')
        self.hb('run', self.script('''import bpy
bpy.ops.mesh.primitive_cube_add(location=(1,2,3))
bpy.context.object.scale=(2,2,2)
'''), '--scene', 'control.hb', '--out', 'control.glb')
        self.assertEqual(test_cli.revision(self.path / 'scene.hb')['scene'],
                         test_cli.revision(self.path / 'control.hb')['scene'])
        self.assertEqual((self.path / 'defaults.glb').read_bytes(),
                         (self.path / 'control.glb').read_bytes())

    def test_defaults_and_explicit_arguments_are_both_checked(self):
        source = '''from mathutils import Vector
def f(point=Vector((1,2,3))):return point.to_tuple()
f((1,2,3))
f()
'''
        errors = self.hb('check', self.script(source), ok=False)['errors']
        self.assertEqual(len(errors), 1, errors)
        self.assertIn('mathutils.Vector.to_tuple', errors[0]['message'])

    def test_mcp_checks_defaults_before_executing_and_recovers(self):
        source = '''from mathutils import Vector
open('executed', 'w').write('preflight was bypassed')
def coordinates(point=Vector((1,2,3))):return point.to_tuple()
coordinates()
'''
        replies = self.exchange('--mcp', [
            test_server.request(0, 'initialize', {'protocolVersion': '2025-11-25',
                                                 'clientInfo': {}, 'capabilities': {}}),
            {'jsonrpc': '2.0', 'method': 'notifications/initialized'},
            test_server.request(1, 'tools/call', {'name': 'hb_run',
                                                'arguments': {'code': source}}),
            test_server.request(2, 'tools/call', {'name': 'hb_run', 'arguments': {
                'code': (test_cli.ROOT / 'compat/golden/m3_checker_defaults.py').read_text(),
                'args': ['--out', 'mcp.glb']}}),
            test_server.request(3, 'tools/call', {'name': 'hb_query',
                                                'arguments': {'args': ['stats']}}),
        ], self.path)
        self.assertTrue(replies[1]['result']['isError'])
        errors = replies[1]['result']['structuredContent']['errors']
        self.assertTrue(any('mathutils.Vector.to_tuple' in e['message'] for e in errors))
        self.assertFalse((self.path / 'executed').exists())
        self.assertFalse(replies[2]['result']['isError'], replies[2])
        self.assertEqual(replies[3]['result']['structuredContent']['result']['objects'], 1)
        self.assertEqual(replies[3]['result']['structuredContent']['revision'],
                         replies[2]['result']['structuredContent']['revision'])
        self.assertEqual((self.path / 'mcp.glb').read_bytes()[:4], b'glTF')
