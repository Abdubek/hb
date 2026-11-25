"""Numeric values from RNA views must not become synthetic API tuple paths."""
import unittest

import test_cli
import test_server


GOLDEN = test_cli.ROOT / 'compat/golden/m3_checker_rna_scalars.py'
CONTROL = '''import bpy
bpy.ops.mesh.primitive_cube_add(location=(1,2,2))
bpy.context.object.scale=(2,2,2)
'''


class CheckerRNAScalars(unittest.TestCase):
    setUp = test_cli.CLI.setUp
    tearDown = test_cli.CLI.tearDown
    hb = test_cli.CLI.hb
    script = test_cli.CLI.script
    exchange = test_server.Server.exchange

    def test_view_scalar_model_matches_control_scene_and_export(self):
        self.hb('check', GOLDEN)
        self.hb('run', GOLDEN, '--out', 'scalars.glb')
        self.hb('run', self.script(CONTROL), '--scene', 'control.hb', '--out', 'control.glb')
        self.assertEqual(test_cli.revision(self.path / 'scene.hb')['scene'],
                         test_cli.revision(self.path / 'control.hb')['scene'])
        self.assertEqual((self.path / 'scalars.glb').read_bytes(),
                         (self.path / 'control.glb').read_bytes())

    def test_spline_shape_key_and_cursor_components_remain_numbers(self):
        cases = [
            ("curve=bpy.data.curves.new('Path','CURVE')\ncurve.dimensions='3D'\nspline=curve.splines.new('POLY')\n"
             "point=spline.points[0]\npoint.co=(1,2,3,4)\n",
             '(point.co.x,point.co.y,point.co.z,point.co.w)'),
            ("curve=bpy.data.curves.new('Path','CURVE')\ncurve.dimensions='3D'\nspline=curve.splines.new('BEZIER')\n"
             "point=spline.bezier_points[0]\npoint.handle_left=(1,2,3)\n"
             "point.handle_right=(4,5,6)\n",
             '(point.handle_left.x,point.handle_left.y,point.handle_right.z)'),
            ('bpy.ops.mesh.primitive_cube_add()\n'
             "key=bpy.context.object.shape_key_add(name='Basis')\npoint=key.data[0]\n",
             '(point.co.x,point.co.y,point.co.z)'),
            ('cursor=bpy.context.scene.cursor\ncursor.location=(1,2,3)\n',
             '(cursor.location.x,cursor.location.y,cursor.location.z)'),
        ]
        for setup, values in cases:
            with self.subTest(values=values):
                source = self.script('import bpy\nfrom mathutils import Vector\n'
                    'def copy(values):\n    values=Vector(values)\n    return values.copy()\n' +
                    setup + f'values={values}\nassert tuple(copy(values))==values\n')
                self.hb('check', source)
                self.hb('run', source)

    def test_raw_members_api_objects_and_swizzles_are_still_validated(self):
        cases = [
            ('obj.location.unsupported_magic()', 'bpy.types.Object.location.unsupported_magic'),
            ("getattr(obj.location,'unsupported_magic')()", 'bpy.types.Object.location.unsupported_magic'),
            ('obj.location.xy.freeze()', 'bpy.types.Object.location.xy.freeze'),
            ('obj.location.unsupported_view.x', 'bpy.types.Object.location.unsupported_view'),
            ('obj.unsupported_view.location.x', 'bpy.types.Object.unsupported_view'),
            ('obj.data.vertices[0].normal.x', 'bpy.types.MeshVertex.normal'),
            ('values=(obj.location.x,obj)\nvalues[1].unsupported_magic()',
             'bpy.types.Object.unsupported_magic'),
            ('values=[obj.location]\nvalues[0].freeze()', 'bpy.types.Object.location.freeze'),
            # A tuple containing a Vector view is still a tuple, not a number.
            ('values=(obj.location,)\nvalues.x', '@tuple:1:0:bpy.types.Object.location.x'),
        ]
        for source, expected in cases:
            with self.subTest(source=source):
                errors = self.hb('check', self.script('import bpy\nobj=bpy.context.object\n' + source),
                                 ok=False)['errors']
                self.assertTrue(any(expected in error['message'] for error in errors), errors)

    def test_mcp_accepts_scalar_helpers_and_keeps_rejecting_real_api_errors(self):
        bad = ("import bpy\nopen('executed','w').write('started')\n"
               "values=(bpy.context.object.location.x,bpy.context.object)\n"
               'values[1].unsupported_magic()\n')
        replies = self.exchange('--mcp', [
            test_server.request(0, 'initialize', {'protocolVersion': '2025-11-25',
                                                 'clientInfo': {}, 'capabilities': {}}),
            {'jsonrpc': '2.0', 'method': 'notifications/initialized'},
            test_server.request(1, 'tools/call', {'name': 'hb_run', 'arguments': {
                'code': GOLDEN.read_text(), 'args': ['--out', 'mcp.glb']}}),
            test_server.request(2, 'tools/call', {'name': 'hb_run', 'arguments': {'code': bad}}),
            test_server.request(3, 'tools/call', {'name': 'hb_query',
                                                'arguments': {'args': ['stats']}}),
        ], self.path)
        self.assertFalse(replies[1]['result']['isError'], replies[1])
        self.assertTrue(replies[2]['result']['isError'])
        errors = replies[2]['result']['structuredContent']['errors']
        self.assertTrue(any('bpy.types.Object.unsupported_magic' in e['message'] for e in errors))
        self.assertFalse((self.path / 'executed').exists())
        self.assertEqual(replies[3]['result']['structuredContent']['result']['objects'], 1)
        self.assertEqual(replies[3]['result']['structuredContent']['revision'],
                         replies[1]['result']['structuredContent']['revision'])
        self.hb('run', self.script(CONTROL), '--scene', 'control.hb', '--out', 'control.glb')
        self.assertEqual(test_cli.revision(self.path / 'scene.hb')['scene'],
                         test_cli.revision(self.path / 'control.hb')['scene'])
        self.assertEqual((self.path / 'mcp.glb').read_bytes(),
                         (self.path / 'control.glb').read_bytes())
