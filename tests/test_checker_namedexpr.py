"""API provenance must survive both the value and binding of := expressions."""
import unittest

import test_cli
import test_server


GOLDEN = test_cli.ROOT / 'compat/golden/m3_checker_namedexpr.py'
CONTROL = '''import bpy
bpy.ops.mesh.primitive_cube_add(location=(2,2,3))
bpy.context.object.scale=(2,2,2)
world=bpy.data.worlds.get('World')
world.use_nodes=False
world.color=(.1,.2,.3)
bpy.context.scene.world=world
'''


class CheckerNamedExpr(unittest.TestCase):
    setUp = test_cli.CLI.setUp
    tearDown = test_cli.CLI.tearDown
    hb = test_cli.CLI.hb
    script = test_cli.CLI.script
    exchange = test_server.Server.exchange

    def test_expression_values_and_bindings_keep_api_types(self):
        cases = [
            '(point:=Vector((1,2,3))).freeze()',
            '(point:=Vector((1,2,3)))\npoint.freeze()',
            'copy=(point:=Vector((1,2,3)))\ncopy.freeze()',
            'if (point:=Vector((1,2,3))) is not None:\n    point.freeze()',
            'while (point:=Vector((1,2,3))) is not None:\n    point.freeze()\n    break',
            'def identity(value):return value\nidentity(point:=Vector((1,2,3))).freeze()',
            'def make():return (point:=Vector((1,2,3)))\nmake().freeze()',
            'points=[(point:=Vector((1,2,3)))]\npoints[0].freeze()',
            "points={'point':(point:=Vector((1,2,3)))}\npoints['point'].freeze()",
            '(first:=(second:=Vector((1,2,3))))\nfirst.freeze()',
            '(first:=(second:=Vector((1,2,3))))\nsecond.freeze()',
            'points=[(point:=Vector((1,2,3))) for _ in range(1)]\npoints[0].freeze()',
            'points=[(point:=Vector((1,2,3))) for _ in range(1)]\npoint.freeze()',
            'points={i:(point:=Vector((1,2,3))) for i in range(1)}\npoint.freeze()',
            'points=(point:=Vector((1,2,3)) for _ in range(1))\nnext(points)\npoint.freeze()',
            'points=[point for _ in range(1) if (point:=Vector((1,2,3)))]\npoint.freeze()',
            'points=[]\n(alias:=points)\nalias.append(Vector((1,2,3)))\npoints[0].freeze()',
            'points=[]\nalias=(other:=points)\nalias.append(Vector((1,2,3)))\npoints[0].freeze()',
            'def append(points):points.append(Vector((1,2,3)))\n'
            'append(points:=[])\npoints[0].freeze()',
            'points=[]\nalias=(first:=(second:=points))\nalias.append(Vector((1,2,3)))\n'
            'second[0].freeze()',
        ]
        for source in cases:
            with self.subTest(source=source):
                errors = self.hb('check', self.script('from mathutils import Vector\n' + source),
                                 ok=False)['errors']
                self.assertEqual(len(errors), 1, errors)
                self.assertIn('mathutils.Vector.freeze', errors[0]['message'])

    def test_function_scopes_global_nonlocal_and_branch_unions(self):
        cases = [
            ('point=bpy.context.object\ndef f():\n    (point:=Vector((1,2,3)))\n'
             '    point.freeze()\nf()', ['mathutils.Vector.freeze']),
            ('def f():\n    values=[(point:=Vector((1,2,3))) for _ in range(1)]\n'
             '    return point.freeze()\nf()', ['mathutils.Vector.freeze']),
            ('def f():\n    values=[[(point:=Vector((1,2,3))) for _ in range(1)] '
             'for _ in range(1)]\n    return point.freeze()\nf()', ['mathutils.Vector.freeze']),
            ('point=None\ndef f():\n    global point\n    (point:=Vector((1,2,3)))\n'
             'f()\npoint.freeze()', ['mathutils.Vector.freeze']),
            ('def outer():\n    point=None\n    def f():\n        nonlocal point\n'
             '        (point:=Vector((1,2,3)))\n    f()\n    point.freeze()\nouter()',
             ['mathutils.Vector.freeze']),
            ('if True:\n    (value:=Vector((1,2,3)))\nelse:\n    (value:=bpy.context.object)\n'
             'value.unsupported_magic()',
             ['mathutils.Vector.unsupported_magic', 'bpy.types.Object.unsupported_magic']),
        ]
        for source, expected in cases:
            with self.subTest(source=source):
                errors = self.hb('check', self.script('import bpy\nfrom mathutils import Vector\n' +
                                                     source), ok=False)['errors']
                self.assertEqual(len(errors), len(expected), errors)
                for path in expected:
                    self.assertTrue(any(path in error['message'] for error in errors), errors)

    def test_valid_assignment_semantics_scene_and_export_match_control(self):
        self.hb('check', GOLDEN)
        self.hb('run', GOLDEN, '--out', 'namedexpr.glb')
        self.hb('run', self.script(CONTROL), '--scene', 'control.hb', '--out', 'control.glb')
        self.assertEqual(test_cli.revision(self.path / 'scene.hb')['scene'],
                         test_cli.revision(self.path / 'control.hb')['scene'])
        self.assertEqual((self.path / 'namedexpr.glb').read_bytes(),
                         (self.path / 'control.glb').read_bytes())

    def test_mcp_rejects_walrus_api_error_before_execution_and_recovers(self):
        source = '''import bpy
open('executed','w').write('started')
if (world:=bpy.data.worlds.get('World')) is not None:
    world.use_nodes=True
    nodes=world.node_tree.nodes
    nodes.remove(next(iter(nodes)))
'''
        replies = self.exchange('--mcp', [
            test_server.request(0, 'initialize', {'protocolVersion': '2025-11-25',
                                                 'clientInfo': {}, 'capabilities': {}}),
            {'jsonrpc': '2.0', 'method': 'notifications/initialized'},
            test_server.request(1, 'tools/call', {'name': 'hb_run', 'arguments': {'code': source}}),
            test_server.request(2, 'tools/call', {'name': 'hb_run', 'arguments': {
                'code': GOLDEN.read_text(), 'args': ['--out', 'mcp.glb']}}),
            test_server.request(3, 'tools/call', {'name': 'hb_query',
                                                'arguments': {'args': ['stats']}}),
        ], self.path)
        self.assertTrue(replies[1]['result']['isError'])
        payload = replies[1]['result']['structuredContent']
        self.assertIn('errors', payload, payload)
        self.assertEqual(len(payload['errors']), 1, payload)
        self.assertIn('bpy.types.World.node_tree.nodes.remove', payload['errors'][0]['message'])
        self.assertFalse((self.path / 'executed').exists())
        self.assertFalse(replies[2]['result']['isError'], replies[2])
        self.assertEqual(replies[3]['result']['structuredContent']['result']['objects'], 1)
        self.assertEqual(replies[3]['result']['structuredContent']['revision'],
                         replies[2]['result']['structuredContent']['revision'])
        self.hb('run', self.script(CONTROL), '--scene', 'control.hb', '--out', 'control.glb')
        self.assertEqual(test_cli.revision(self.path / 'scene.hb')['scene'],
                         test_cli.revision(self.path / 'control.hb')['scene'])
        self.assertEqual((self.path / 'mcp.glb').read_bytes(),
                         (self.path / 'control.glb').read_bytes())
