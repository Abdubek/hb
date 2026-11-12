"""Accessor bounds must be validated before materializing decoded rows."""
import base64
import json
import struct
import unittest

import test_cli
import test_server


POSITIONS = ((0, 0, 0), (1, 0, 0), (0, 1, 0))


def document(layout='packed', index_type=5121):
    positions = struct.pack('<9f', *(x for row in POSITIONS for x in row))
    views = []
    accessor = {'componentType': 5126, 'type': 'VEC3', 'count': 3,
                'min': [0, 0, 0], 'max': [1, 1, 0]}
    if layout == 'strided':
        # Both offsets are nonzero; the last element has no trailing stride padding.
        binary = b'view' + b'base' + b'gap!'.join(struct.pack('<3f', *v) for v in POSITIONS)
        views.append({'buffer': 0, 'byteOffset': 4, 'byteLength': 48, 'byteStride': 16})
        accessor.update(bufferView=0, byteOffset=4)
    elif layout.startswith('sparse'):
        binary = bytes(36) if layout == 'sparse-overlay' else b''
        if binary:
            views.append({'buffer': 0, 'byteLength': 36})
            accessor['bufferView'] = 0
        fmt = {5121: 'B', 5123: 'H', 5125: 'I'}[index_type]
        width = struct.calcsize(fmt)
        ids = bytes(width) + struct.pack('<2' + fmt, 1, 2)
        index_view = len(views)
        views.append({'buffer': 0, 'byteOffset': len(binary), 'byteLength': len(ids)})
        binary += ids
        binary += bytes(-len(binary) % 4)
        values = bytes(4) + positions[12:]
        value_view = len(views)
        views.append({'buffer': 0, 'byteOffset': len(binary), 'byteLength': len(values)})
        binary += values
        accessor['sparse'] = {'count': 2,
                              'indices': {'bufferView': index_view, 'byteOffset': width,
                                          'componentType': index_type},
                              'values': {'bufferView': value_view, 'byteOffset': 4}}
    else:
        binary = positions
        views.append({'buffer': 0, 'byteLength': 36})
        accessor['bufferView'] = 0
    uv = struct.pack('<6H', 0, 0, 65535, 0, 0, 65535) if layout == 'normalized' else (
        struct.pack('<6f', 0, 0, 1, 0, 0, 1))
    views.append({'buffer': 0, 'byteOffset': len(binary), 'byteLength': len(uv)})
    binary += uv
    return {'asset': {'version': '2.0'},
            'buffers': [{'byteLength': len(binary), 'uri': 'data:application/octet-stream;base64,' +
                         base64.b64encode(binary).decode()}], 'bufferViews': views,
            'accessors': [accessor, {'bufferView': len(views)-1, 'count': 3, 'type': 'VEC2',
                                     'componentType': 5123 if layout == 'normalized' else 5126,
                                     'normalized': layout == 'normalized'}],
            'meshes': [{'name': 'Triangle', 'primitives': [{'attributes': {
                'POSITION': 0, 'TEXCOORD_0': 1}}]}],
            'nodes': [{'name': 'Triangle', 'mesh': 0}], 'scenes': [{'nodes': [0]}], 'scene': 0}


class GltfAccessors(unittest.TestCase):
    setUp = test_cli.CLI.setUp
    tearDown = test_cli.CLI.tearDown
    hb = test_cli.CLI.hb
    script = test_cli.CLI.script
    exchange = test_server.Server.exchange

    def asset(self, doc):
        path = self.path / 'asset.gltf'
        path.write_text(json.dumps(doc))
        return path

    def test_valid_layouts_match_packed_scene_and_glb(self):
        variants = [('packed', 5121), ('strided', 5121), ('normalized', 5121)]
        variants += [(layout, ct) for layout in ('sparse-only', 'sparse-overlay')
                     for ct in (5121, 5123, 5125)]
        expected = {}
        for layout, ct in variants:
            for operator in (False, True):
                with self.subTest(layout=layout, index_type=ct, operator=operator):
                    path = self.asset(document(layout, ct))
                    scene = f'{layout}-{ct}-{operator}.hb'
                    if operator:
                        self.hb('run', self.script('import bpy\nbpy.ops.import_scene.gltf(filepath=' +
                                                  repr(str(path)) + ')'), '--scene', scene)
                    else:
                        self.hb('import', path, '--scene', scene)
                    self.hb('export', 'actual.glb', '--scene', scene)
                    actual = (test_cli.revision(self.path / scene)['scene'],
                              (self.path / 'actual.glb').read_bytes())
                    if layout == 'packed':
                        expected[operator] = actual
                    else:
                        self.assertEqual(actual, expected[operator])

    def test_invalid_layouts_preserve_scene_and_release_lock(self):
        self.hb('run', self.script('import bpy\nbpy.ops.mesh.primitive_cube_add()'))
        before = (self.path / 'scene.hb').read_bytes()
        history = set((self.path / 'scene.hb.revisions').iterdir())
        cases = []
        for field, value in (('count', 2_000_000), ('byteOffset', 12),
                             ('byteOffset', 2**64-1), ('bufferView', 99)):
            doc = document()
            doc['accessors'][0][field] = value
            cases.append(doc)
        for stride in (8, 2**64-1):
            doc = document()
            doc['bufferViews'][0]['byteStride'] = stride
            cases.append(doc)
        for field, value in (('count', 4), ('indices-offset', 2**64-1),
                             ('values-offset', 2**64-1), ('index-type', 5122),
                             ('indices-short', 1), ('values-short', 12), ('values-view', 99)):
            doc = document('sparse-only', 5123)
            sparse = doc['accessors'][0]['sparse']
            if field == 'count': sparse['count'] = value
            elif field == 'indices-offset': sparse['indices']['byteOffset'] = value
            elif field == 'values-offset': sparse['values']['byteOffset'] = value
            elif field == 'index-type': sparse['indices']['componentType'] = value
            elif field == 'indices-short': doc['bufferViews'][0]['byteLength'] = value
            elif field == 'values-short': doc['bufferViews'][1]['byteLength'] = value
            else: sparse['values']['bufferView'] = value
            cases.append(doc)
        doc = document('sparse-only', 5123)
        data = bytearray(base64.b64decode(doc['buffers'][0]['uri'].split(',')[1]))
        struct.pack_into('<H', data, 2, 3)  # Index equals the base accessor count.
        doc['buffers'][0]['uri'] = 'data:application/octet-stream;base64,' + base64.b64encode(data).decode()
        cases.append(doc)
        for index, doc in enumerate(cases):
            with self.subTest(case=index):
                path = self.asset(doc)
                self.assertEqual(self.hb('import', path, ok=False)['error']['code'], 'IMPORT_ERROR')
                result = self.hb('run', self.script('import bpy\nbpy.context.object.location.x=9\n'
                                 'bpy.ops.import_scene.gltf(filepath=' + repr(str(path)) + ')'), ok=False)
                self.assertEqual(result['error']['code'], 'SCRIPT_ERROR')
                self.assertEqual((self.path / 'scene.hb').read_bytes(), before)
                self.assertEqual(set((self.path / 'scene.hb.revisions').iterdir()), history)
                self.assertFalse((self.path / 'scene.hb.lock').exists())

    def test_servers_continue_after_oversized_accessor_rejection(self):
        doc = document()
        doc['accessors'][0]['count'] = 2_000_000
        path = self.asset(doc)
        for mode in ('--mcp', '--jsonrpc'):
            with self.subTest(mode=mode):
                scene = mode[2:] + '.hb'
                self.hb('run', self.script('import bpy\nbpy.ops.mesh.primitive_cube_add()'), '--scene', scene)
                operations = [('import', {'args': [str(path)]}),
                              ('query', {'args': ['stats']}),
                              ('run', {'code': 'import bpy\nbpy.context.object.location.x=9\n'
                                       'bpy.ops.import_scene.gltf(filepath=' + repr(str(path)) + ')'}),
                              ('query', {'args': ['stats']}),
                              ('run', {'code': 'import bpy\nbpy.context.object.location.x=3'}), ('log', {})]
                messages = []
                if mode == '--mcp':
                    messages = [test_server.request(0, 'initialize', {'protocolVersion': '2025-11-25',
                                                                     'clientInfo': {}, 'capabilities': {}}),
                                {'jsonrpc': '2.0', 'method': 'notifications/initialized'}]
                for identifier, (command, arguments) in enumerate(operations, 1):
                    arguments = {**arguments, 'scene': scene}
                    messages.append(test_server.request(identifier, 'tools/call', {
                        'name': 'hb_' + command, 'arguments': arguments}) if mode == '--mcp' else
                        test_server.request(identifier, command, arguments))
                replies = self.exchange(mode, messages, self.path)
                if mode == '--mcp':
                    replies = replies[1:]
                    self.assertTrue(replies[0]['result']['isError'])
                    self.assertTrue(replies[2]['result']['isError'])
                    bodies = [r['result']['structuredContent'] for r in replies]
                    error = bodies[0]['error']
                else:
                    error = replies[0]['error']['data']
                    bodies = [None] + [r['result'] for r in replies[1:]]
                self.assertEqual(error['code'], 'IMPORT_ERROR')
                self.assertEqual(bodies[2]['error']['code'], 'SCRIPT_ERROR')
                self.assertEqual(bodies[1]['result']['objects'], 1)
                self.assertEqual(bodies[3]['result']['objects'], 1)
                self.assertTrue(bodies[4]['ok'])
                self.assertEqual(len(bodies[5]['revisions']), 2)
                self.assertFalse((self.path / (scene + '.lock')).exists())
