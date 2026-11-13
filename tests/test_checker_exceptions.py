"""Exception-local names must not inherit unrelated global API provenance."""
import unittest

import test_cli
import test_server


class CheckerExceptions(unittest.TestCase):
    setUp = test_cli.CLI.setUp
    tearDown = test_cli.CLI.tearDown
    hb = test_cli.CLI.hb
    script = test_cli.CLI.script
    exchange = test_server.Server.exchange

    def test_handlers_and_closures_match_control_scene_and_export(self):
        source = test_cli.ROOT / 'compat/golden/m3_checker_exceptions.py'
        self.hb('check', source)
        self.hb('run', source, '--out', 'exceptions.glb')
        self.hb('run', self.script('''import bpy
bpy.ops.mesh.primitive_cube_add(location=(1,2,3))
bpy.context.object.scale=(4,4,4)
'''), '--scene', 'control.hb', '--out', 'control.glb')
        self.assertEqual(test_cli.revision(self.path / 'scene.hb')['scene'],
                         test_cli.revision(self.path / 'control.hb')['scene'])
        self.assertEqual((self.path / 'exceptions.glb').read_bytes(),
                         (self.path / 'control.glb').read_bytes())

    def test_handler_bindings_preserve_real_api_errors(self):
        setup = 'import bpy\nobj=bpy.context.object\n'
        cases = [
            ('def f():\n    try:raise ValueError()\n    except ValueError as obj:pass\n'
             'f()\nobj.unsupported_magic()', 'bpy.types.Object.unsupported_magic'),
            ('def f():\n    try:raise ValueError()\n    except ValueError as obj:\n'
             '        obj=bpy.context.object\n        obj.unsupported_magic()\nf()',
             'bpy.types.Object.unsupported_magic'),
            ('def f():\n    global obj\n    try:raise ValueError()\n    except ValueError as obj:\n'
             '        obj=bpy.context.object\n        obj.unsupported_magic()\nf()',
             'bpy.types.Object.unsupported_magic'),
            ('def outer(value):\n    def f():\n        nonlocal value\n'
             '        try:raise ValueError()\n        except ValueError as value:\n'
             '            value=bpy.context.object\n            value.unsupported_magic()\n'
             '    f()\nouter(obj)', 'bpy.types.Object.unsupported_magic'),
            ('def f():\n    try:raise ValueError()\n    except bpy.unsupported_error as obj:pass\nf()',
             'bpy.unsupported_error'),
        ]
        for source, expected in cases:
            with self.subTest(source=source):
                errors = self.hb('check', self.script(setup + source), ok=False)['errors']
                self.assertTrue(any(expected in error['message'] for error in errors), errors)

    def test_mcp_runs_exception_shadowing_and_checks_later_requests(self):
        source = (test_cli.ROOT / 'compat/golden/m3_checker_exceptions.py').read_text()
        replies = self.exchange('--mcp', [
            test_server.request(0, 'initialize', {'protocolVersion': '2025-11-25',
                                                 'clientInfo': {}, 'capabilities': {}}),
            {'jsonrpc': '2.0', 'method': 'notifications/initialized'},
            test_server.request(1, 'tools/call', {'name': 'hb_run', 'arguments': {
                'code': source, 'args': ['--out', 'mcp.glb']}}),
            test_server.request(2, 'tools/call', {'name': 'hb_run', 'arguments': {
                'code': source + '\nobj.unsupported_magic()'}}),
            test_server.request(3, 'tools/call', {'name': 'hb_query',
                                                'arguments': {'args': ['stats']}}),
        ], self.path)
        self.assertFalse(replies[1]['result']['isError'], replies[1])
        self.assertTrue(replies[2]['result']['isError'])
        errors = replies[2]['result']['structuredContent']['errors']
        self.assertTrue(any('bpy.types.Object.unsupported_magic' in e['message'] for e in errors))
        self.assertEqual(replies[3]['result']['structuredContent']['result']['objects'], 1)
        self.assertEqual(replies[3]['result']['structuredContent']['revision'],
                         replies[1]['result']['structuredContent']['revision'])
        self.assertEqual((self.path / 'mcp.glb').read_bytes()[:4], b'glTF')
