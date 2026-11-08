"""Malformed glTF resource escapes must not terminate HB or strand writer locks."""
import base64
import copy
import json
import struct
import unittest
from urllib.parse import quote

import test_cli
import test_server
from normalize import revision
from test_server import request


class GltfURI(unittest.TestCase):
    setUp = test_cli.CLI.setUp
    tearDown = test_cli.CLI.tearDown
    hb = test_cli.CLI.hb
    script = test_cli.CLI.script
    exchange = test_server.Server.exchange

    def document(self):
        binary = struct.pack('<15f', 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1)
        image = (test_cli.ROOT / 'compat/fixtures/checker.png').read_bytes()
        return {
            'asset': {'version': '2.0'},
            'buffers': [{'byteLength': len(binary), 'uri':
                         'data:application/octet-stream;base64,' + base64.b64encode(binary).decode()}],
            'bufferViews': [{'buffer': 0, 'byteLength': 36},
                            {'buffer': 0, 'byteOffset': 36, 'byteLength': 24}],
            'accessors': [{'bufferView': 0, 'componentType': 5126, 'type': 'VEC3', 'count': 3,
                           'min': [0, 0, 0], 'max': [1, 1, 0]},
                          {'bufferView': 1, 'componentType': 5126, 'type': 'VEC2', 'count': 3}],
            'images': [{'name': 'Paint', 'uri': 'data:image/png;base64,' + base64.b64encode(image).decode()}],
            'textures': [{'source': 0}],
            'materials': [{'name': 'Surface', 'pbrMetallicRoughness': {
                'baseColorTexture': {'index': 0}, 'metallicFactor': 0, 'roughnessFactor': 1}}],
            'meshes': [{'name': 'Triangle', 'primitives': [{
                'attributes': {'POSITION': 0, 'TEXCOORD_0': 1}, 'material': 0}]}],
            'nodes': [{'name': 'Triangle', 'mesh': 0}], 'scenes': [{'nodes': [0]}], 'scene': 0,
        }

    def asset(self, document):
        path = self.path / 'asset.gltf'
        path.write_text(json.dumps(document, ensure_ascii=False), encoding='utf-8')
        return path

    def import_asset(self, document, scene, operator):
        path = self.asset(document)
        if operator:
            self.hb('run', self.script('import bpy\nbpy.ops.import_scene.gltf(filepath=' +
                                      repr(str(path)) + ')'), '--scene', scene)
        else:
            self.hb('import', path, '--scene', scene)

    def test_malformed_escapes_preserve_scene_and_release_lock(self):
        self.hb('run', self.script('import bpy\nbpy.ops.mesh.primitive_cube_add()'))
        before = (self.path / 'scene.hb').read_bytes()
        snapshots = set((self.path / 'scene.hb.revisions').iterdir())
        for resource in ('buffer', 'image'):
            for uri in ('%模型.bin', '%A模型.bin', '%🙂.bin', '%', '%A', '%GG', '%+A', '%FF'):
                with self.subTest(resource=resource, uri=uri):
                    doc = self.document()
                    if resource == 'buffer':
                        doc['buffers'][0]['uri'] = uri
                    else:
                        # A preceding valid image exercises partial import rollback.
                        doc['images'].append({'uri': uri})
                    path = self.asset(doc)
                    rejected = self.hb('import', path, ok=False)
                    self.assertEqual(rejected['error']['code'], 'IMPORT_ERROR')
                    expected = 'Invalid URI UTF-8' if uri == '%FF' else 'Invalid URI escape'
                    self.assertIn(expected, rejected['error']['message'])
                    rejected = self.hb('run', self.script(
                        'import bpy\nbpy.context.object.location.x=9\n'
                        'bpy.ops.import_scene.gltf(filepath=' + repr(str(path)) + ')'), ok=False)
                    self.assertEqual(rejected['error']['code'], 'SCRIPT_ERROR')
                    self.assertIn(expected, rejected['error']['message'])
                    self.assertEqual((self.path / 'scene.hb').read_bytes(), before)
                    self.assertEqual(set((self.path / 'scene.hb.revisions').iterdir()), snapshots)
                    self.assertFalse((self.path / 'scene.hb.lock').exists())

    def test_unicode_and_percent_encoded_resources_match_data_uri_control(self):
        control = self.document()
        expected = {}
        for operator in (False, True):
            scene = f'control-{operator}.hb'
            self.import_asset(control, scene, operator)
            self.hb('export', f'control-{operator}.glb', '--scene', scene)
            expected[operator] = revision(self.path / scene)['scene']
        for index, mode in enumerate(('unicode', 'encoded', 'literal-percent')):
            doc = copy.deepcopy(control)
            names = ('данные模型.bin', 'цвет🙂.png') if mode != 'literal-percent' else (
                'данные %20 + 模型.bin', 'цвет % + 🙂.png')
            for entry, name in zip((doc['buffers'][0], doc['images'][0]), names):
                (self.path / name).write_bytes(base64.b64decode(entry['uri'].split(',')[1]))
                entry['uri'] = name if mode == 'unicode' else quote(name).lower()
            for operator in (False, True):
                with self.subTest(mode=mode, operator=operator):
                    scene = f'{index}-{operator}.hb'
                    self.import_asset(doc, scene, operator)
                    self.assertEqual(revision(self.path / scene)['scene'], expected[operator])
                    self.hb('export', 'actual.glb', '--scene', scene)
                    self.assertEqual((self.path / 'actual.glb').read_bytes(),
                                     (self.path / f'control-{operator}.glb').read_bytes())

    def test_servers_continue_after_malformed_resource(self):
        for mode in ('--jsonrpc', '--mcp'):
            with self.subTest(mode=mode):
                scene = mode[2:] + '.hb'
                self.hb('run', self.script('import bpy\nbpy.ops.mesh.primitive_cube_add()'), '--scene', scene)
                doc = self.document()
                doc['images'].append({'uri': '%模型.png'})
                path = self.asset(doc)
                operations = [('import', {'args': [str(path)]}), ('query', {'args': ['stats']}),
                              ('run', {'code': 'import bpy\nbpy.context.object.location.x=3'}),
                              ('log', {})]
                messages = []
                if mode == '--mcp':
                    messages = [request(0, 'initialize', {'protocolVersion': '2025-11-25',
                                                         'clientInfo': {}, 'capabilities': {}}),
                                {'jsonrpc': '2.0', 'method': 'notifications/initialized'}]
                for identifier, (command, arguments) in enumerate(operations, 1):
                    arguments = {**arguments, 'scene': scene}
                    messages.append(request(identifier, 'tools/call', {
                        'name': 'hb_' + command, 'arguments': arguments}) if mode == '--mcp' else
                        request(identifier, command, arguments))
                replies = self.exchange(mode, messages, self.path)
                if mode == '--mcp':
                    replies = replies[1:]
                    self.assertTrue(replies[0]['result']['isError'])
                    error = replies[0]['result']['structuredContent']['error']
                    results = [r['result']['structuredContent'] for r in replies[1:]]
                else:
                    error = replies[0]['error']['data']
                    results = [r['result'] for r in replies[1:]]
                self.assertEqual([r['id'] for r in replies], [1, 2, 3, 4])
                self.assertEqual(error['code'], 'IMPORT_ERROR')
                self.assertIn('Invalid URI escape', error['message'])
                self.assertEqual(results[0]['result']['objects'], 1)
                self.assertTrue(results[1]['ok'])
                self.assertEqual(len(results[2]['revisions']), 2)
                self.assertFalse((self.path / (scene + '.lock')).exists())
