"""API types must survive and/or expressions without leaking through not."""
import unittest

import test_cli
import test_server


class CheckerBooleans(unittest.TestCase):
    setUp = test_cli.CLI.setUp
    tearDown = test_cli.CLI.tearDown
    hb = test_cli.CLI.hb
    script = test_cli.CLI.script
    exchange = test_server.Server.exchange

    def test_boolean_values_keep_api_provenance(self):
        setup = 'import bpy\nfrom mathutils import Vector\n'
        cases = [
            ("world=bpy.data.worlds.get('World') or bpy.data.worlds.new('World')\n"
             'world.unsupported_magic()', 'bpy.types.World.unsupported_magic'),
            ("world=bpy.data.worlds.get('World') or bpy.data.worlds.new('World')\n"
             'world.use_nodes=True\nnodes=world.node_tree.nodes\nnodes.remove(next(iter(nodes)))',
             'bpy.types.World.node_tree.nodes.remove'),
            ('(None or bpy.context.object).unsupported_magic()',
             'bpy.types.Object.unsupported_magic'),
            ('value=True and bpy.context.object\nvalue.unsupported_magic()',
             'bpy.types.Object.unsupported_magic'),
            ('def choose(v):return v or bpy.context.object\nchoose(None).unsupported_magic()',
             'bpy.types.Object.unsupported_magic'),
            ('values=[] or [bpy.context.object]\nvalues[0].unsupported_magic()',
             'bpy.types.Object.unsupported_magic'),
            ('values={"v":None or bpy.context.object}\nvalues["v"].unsupported_magic()',
             'bpy.types.Object.unsupported_magic'),
            ('def f(v=None or Vector((1,2,3))):return v.unsupported_magic()\nf()',
             'mathutils.Vector.unsupported_magic'),
            ('value=True and (None or Vector((1,2,3)))\nvalue.unsupported_magic()',
             'mathutils.Vector.unsupported_magic'),
            ('value=not bpy.context.object.unsupported_magic',
             'bpy.types.Object.unsupported_magic'),
        ]
        for source, expected in cases:
            with self.subTest(source=source):
                errors = self.hb('check', self.script(setup + source), ok=False)['errors']
                self.assertTrue(any(expected in error['message'] for error in errors), errors)

    def test_all_operand_types_are_kept_conservatively(self):
        source = '''import bpy
from mathutils import Vector
value=Vector((1,2,3)) or bpy.context.object
value.unsupported_magic()
'''
        errors = self.hb('check', self.script(source), ok=False)['errors']
        for expected in ('mathutils.Vector.unsupported_magic', 'bpy.types.Object.unsupported_magic'):
            self.assertTrue(any(expected in error['message'] for error in errors), errors)

    def test_boolean_modeling_and_plain_bool_match_control(self):
        source = test_cli.ROOT / 'compat/golden/m3_checker_booleans.py'
        self.hb('check', source)
        self.hb('run', source, '--out', 'booleans.glb')
        self.hb('run', self.script('''import bpy
bpy.ops.mesh.primitive_cube_add(location=(1,2,3))
bpy.context.object.scale=(2,2,2)
world=bpy.data.worlds.new('Fallback')
world.color=(.1,.2,.3)
bpy.context.scene.world=world
'''), '--scene', 'control.hb', '--out', 'control.glb')
        self.assertEqual(test_cli.revision(self.path / 'scene.hb')['scene'],
                         test_cli.revision(self.path / 'control.hb')['scene'])
        self.assertEqual((self.path / 'booleans.glb').read_bytes(),
                         (self.path / 'control.glb').read_bytes())

    def test_mcp_rejects_boolean_api_error_before_execution(self):
        source = '''import bpy
open('executed','w').write('preflight was bypassed')
world=bpy.data.worlds.get('World') or bpy.data.worlds.new('World')
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
                'code': (test_cli.ROOT / 'compat/golden/m3_checker_booleans.py').read_text(),
                'args': ['--out', 'mcp.glb']}}),
            test_server.request(3, 'tools/call', {'name': 'hb_query',
                                                'arguments': {'args': ['stats']}}),
        ], self.path)
        self.assertTrue(replies[1]['result']['isError'])
        errors = replies[1]['result']['structuredContent']['errors']
        self.assertTrue(any('bpy.types.World.node_tree.nodes.remove' in e['message'] for e in errors))
        self.assertFalse((self.path / 'executed').exists())
        self.assertFalse(replies[2]['result']['isError'], replies[2])
        self.assertEqual(replies[3]['result']['structuredContent']['result']['objects'], 1)
        self.assertEqual(replies[3]['result']['structuredContent']['revision'],
                         replies[2]['result']['structuredContent']['revision'])
        self.assertEqual((self.path / 'mcp.glb').read_bytes()[:4], b'glTF')
