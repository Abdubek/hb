"""Preflight follows API objects returned as builtin dictionary defaults."""
import unittest

import test_cli
import test_server


GOLDEN = test_cli.ROOT / 'compat/golden/m3_checker_dict_defaults.py'
CONTROL = '''import bpy
from mathutils import Matrix
bpy.ops.mesh.primitive_cube_add(location=(2,2,3))
obj=bpy.context.object
matrix=Matrix.Diagonal((2,2,2))
for vertex in obj.data.vertices:
    vertex.co=matrix@vertex.co
world=bpy.data.worlds.new('Fallback')
world.color=(.1,.2,.3)
bpy.context.scene.world=world
'''


class CheckerDictDefaults(unittest.TestCase):
    setUp = test_cli.CLI.setUp
    tearDown = test_cli.CLI.tearDown
    hb = test_cli.CLI.hb
    script = test_cli.CLI.script
    exchange = test_server.Server.exchange

    def test_defaults_retain_api_through_aliases_helpers_and_containers(self):
        for method in ('get', 'pop'):
            cases = [
                "value={}.METHOD('x',Vector((1,2,3)))\nvalue.freeze()",
                "cache={}\nvalue=cache.copy().METHOD('x',Vector((1,2,3)))\nvalue.freeze()",
                "cache={}\nchoose=cache.METHOD\nchoose('x',Vector((1,2,3))).freeze()",
                "def choose(cache,fallback):return cache.METHOD('x',fallback)\n"
                "choose({},Vector((1,2,3))).freeze()",
                "def choose(cache,fallback=Vector((1,2,3))):return cache.METHOD('x',fallback)\n"
                "choose({}).freeze()",
                "cache={}\ncache.METHOD('x',[Vector((1,2,3))])[0].freeze()",
                "cache={}\ncache.METHOD('x',{'point':Vector((1,2,3))})['point'].freeze()",
                "cache={}\ncache.METHOD('x',Matrix.Identity(3)).unsupported_magic()",
            ]
            for source in cases:
                with self.subTest(method=method, source=source):
                    source = 'from mathutils import Vector,Matrix\n' + source.replace('METHOD', method)
                    errors = self.hb('check', self.script(source), ok=False)['errors']
                    expected = ('mathutils.Matrix.unsupported_magic' if 'Matrix.Identity' in source
                                else 'mathutils.Vector.freeze')
                    self.assertEqual(len(errors), 1, errors)
                    self.assertIn(expected, errors[0]['message'])

    def test_stored_values_and_defaults_form_a_conservative_union(self):
        for method in ('get', 'pop'):
            with self.subTest(method=method):
                source = ("import bpy\nfrom mathutils import Vector\n"
                          "cache={'point':Vector((1,2,3))}\n"
                          f"cache.{method}('point',bpy.context.object).unsupported_magic()")
                errors = self.hb('check', self.script(source), ok=False)['errors']
                self.assertEqual(len(errors), 2, errors)
                for path in ('mathutils.Vector.unsupported_magic', 'bpy.types.Object.unsupported_magic'):
                    self.assertTrue(any(path in e['message'] for e in errors), errors)
                # Omitting the default still retains the stored value type.
                source = ("from mathutils import Vector\ncache={'point':Vector((1,2,3))}\n"
                          f"cache.{method}('point').freeze()")
                errors = self.hb('check', self.script(source), ok=False)['errors']
                self.assertEqual(len(errors), 1, errors)
                self.assertIn('mathutils.Vector.freeze', errors[0]['message'])

    def test_dictionary_semantics_scene_and_export_match_control(self):
        self.hb('check', GOLDEN)
        self.hb('run', GOLDEN, '--out', 'defaults.glb')
        self.hb('run', self.script(CONTROL), '--scene', 'control.hb', '--out', 'control.glb')
        self.assertEqual(test_cli.revision(self.path / 'scene.hb')['scene'],
                         test_cli.revision(self.path / 'control.hb')['scene'])
        self.assertEqual((self.path / 'defaults.glb').read_bytes(),
                         (self.path / 'control.glb').read_bytes())

    def test_mcp_checks_both_defaults_before_execution_and_recovers(self):
        messages = [
            test_server.request(0, 'initialize', {'protocolVersion': '2025-11-25',
                                                 'clientInfo': {}, 'capabilities': {}}),
            {'jsonrpc': '2.0', 'method': 'notifications/initialized'},
        ]
        for identifier, method in enumerate(('get', 'pop'), 1):
            source = ("import bpy\n" + f"open('executed-{method}','w').write('started')\n"
                      "cache={}\n" + f"world=cache.{method}('world',bpy.data.worlds.new('Fallback'))\n"
                      "world.use_nodes=True\nnodes=world.node_tree.nodes\n"
                      "nodes.remove(next(iter(nodes)))\n")
            messages.append(test_server.request(identifier, 'tools/call', {
                'name': 'hb_run', 'arguments': {'code': source}}))
        messages.extend([
            test_server.request(3, 'tools/call', {'name': 'hb_run', 'arguments': {
                'code': GOLDEN.read_text(), 'args': ['--out', 'mcp.glb']}}),
            test_server.request(4, 'tools/call', {'name': 'hb_query',
                                                'arguments': {'args': ['stats']}}),
        ])
        replies = self.exchange('--mcp', messages, self.path)
        for identifier, method in enumerate(('get', 'pop'), 1):
            with self.subTest(method=method):
                self.assertTrue(replies[identifier]['result']['isError'])
                payload = replies[identifier]['result']['structuredContent']
                self.assertIn('errors', payload, payload)
                errors = payload['errors']
                self.assertEqual(len(errors), 1, errors)
                self.assertIn('bpy.types.World.node_tree.nodes.remove', errors[0]['message'])
                self.assertFalse((self.path / ('executed-' + method)).exists())
        self.assertFalse(replies[3]['result']['isError'], replies[3])
        self.assertEqual(replies[4]['result']['structuredContent']['result']['objects'], 1)
        self.assertEqual(replies[4]['result']['structuredContent']['revision'],
                         replies[3]['result']['structuredContent']['revision'])
        self.hb('run', self.script(CONTROL), '--scene', 'control.hb', '--out', 'control.glb')
        self.assertEqual(test_cli.revision(self.path / 'scene.hb')['scene'],
                         test_cli.revision(self.path / 'control.hb')['scene'])
        self.assertEqual((self.path / 'mcp.glb').read_bytes(),
                         (self.path / 'control.glb').read_bytes())
