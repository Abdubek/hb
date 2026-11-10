"""Embedded Python text I/O must work without the host's locale or Python settings."""
import codecs
import json
import os
import subprocess
import unittest

import test_cli
from test_server import request


TEXT = 'Қазақша — Привет 🌍'


class PythonTextIO(unittest.TestCase):
    setUp = test_cli.CLI.setUp
    tearDown = test_cli.CLI.tearDown
    script = test_cli.CLI.script

    def invoke(self, *args, messages=None, ok=True):
        environment = {**os.environ, 'LC_ALL': 'C', 'LANG': 'C',
                       'PYTHONUTF8': '0', 'PYTHONCOERCECLOCALE': '0',
                       'PYTHONIOENCODING': 'ascii', 'PYTHONHOME': '/nonexistent',
                       'PYTHONPATH': '/nonexistent'}
        data = None if messages is None else ''.join(json.dumps(m, ensure_ascii=False) + '\n'
                                                    for m in messages)
        result = subprocess.run([str(test_cli.HB), *map(str, args)], cwd=self.path,
                                input=data, capture_output=True, encoding='utf-8',
                                env=environment, timeout=30)
        self.assertEqual(result.returncode, 0 if ok else 1, result.stdout + '\n' + result.stderr)
        return result

    def test_cli_default_utf8_files_streams_and_unicode_paths(self):
        payload = {'name': TEXT, 'location': [1, 2, 3]}
        (self.path / 'данные.json').write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')
        result = self.invoke('run', self.script('''import bpy,json,io,os,sys
with open('данные.json') as source:data=json.load(source)
text=data['name']
with open('Қазақша.json','w') as output:json.dump(data,output,ensure_ascii=False)
with open('Қазақша.json') as source:assert json.load(source)==data
with io.TextIOWrapper(io.BytesIO(text.encode('utf-8'))) as source:assert source.read()==text
buffer=io.BytesIO()
output=io.TextIOWrapper(buffer)
output.write(text);output.flush()
assert buffer.getvalue()==text.encode('utf-8')
assert os.fsencode('Қазақша.json')=='Қазақша.json'.encode('utf-8')
assert os.fsdecode(os.fsencode(text))==text
assert sys.flags.utf8_mode==1
print(text)
sys.stderr.write(text+'\\n')
bpy.ops.mesh.primitive_cube_add(location=data['location'])
bpy.context.object.name=text
''', 'сценарий.py'), '--scene', 'сцена.hb', '--out', 'куб.glb')
        # Script output stays on stderr; stdout remains one parseable protocol response.
        body = json.loads(result.stdout)
        self.assertEqual(body['objects']['created'], [TEXT])
        self.assertEqual(result.stderr.count(TEXT), 2)
        self.assertEqual(json.loads((self.path / 'Қазақша.json').read_bytes()), payload)
        self.assertIn(TEXT.encode('utf-8'), (self.path / 'Қазақша.json').read_bytes())
        self.assertEqual((self.path / 'куб.glb').read_bytes()[:4], b'glTF')

    def test_repeated_server_initialization_keeps_utf8(self):
        write = """import bpy,json,sys
assert sys.flags.utf8_mode==1
with open('текст.json','w') as output:json.dump({'name':%r},output,ensure_ascii=False)
bpy.ops.mesh.primitive_cube_add()
bpy.context.object.name=%r
print(%r)
""" % (TEXT, TEXT, TEXT)
        read = """import bpy,json,sys
assert sys.flags.utf8_mode==1
with open('текст.json') as source:assert json.load(source)['name']==%r
assert bpy.context.object.name==%r
bpy.context.object.location.x=3
print(%r)
""" % (TEXT, TEXT, TEXT)
        for mode in ('--jsonrpc', '--mcp'):
            with self.subTest(mode=mode):
                scene = mode[2:] + '.hb'
                if mode == '--mcp':
                    messages = [request(0, 'initialize', {'protocolVersion': '2025-11-25',
                                                         'clientInfo': {}, 'capabilities': {}}),
                                {'jsonrpc': '2.0', 'method': 'notifications/initialized'}]
                    for identifier, code in enumerate((write, read), 1):
                        messages.append(request(identifier, 'tools/call', {
                            'name': 'hb_run', 'arguments': {'scene': scene, 'code': code}}))
                    messages.append(request(3, 'tools/call', {
                        'name': 'hb_query', 'arguments': {'scene': scene, 'args': ['stats']}}))
                else:
                    messages = [request(1, 'run', {'scene': scene, 'code': write}),
                                request(2, 'run', {'scene': scene, 'code': read}),
                                request(3, 'query', {'scene': scene, 'args': ['stats']})]
                result = self.invoke('serve', mode, messages=messages)
                replies = [json.loads(line) for line in result.stdout.splitlines()]
                if mode == '--mcp':
                    replies = [reply['result']['structuredContent'] for reply in replies[1:]]
                else:
                    replies = [reply['result'] for reply in replies]
                self.assertTrue(replies[0]['ok'])
                self.assertTrue(replies[1]['ok'])
                self.assertNotEqual(replies[0]['revision'], replies[1]['revision'])
                self.assertEqual(replies[2]['result']['objects'], 1)
                self.assertEqual(result.stderr.count(TEXT), 2)

    def test_explicit_encodings_and_invalid_utf8_keep_their_semantics(self):
        (self.path / 'latin1.txt').write_bytes(b'caf\xe9')
        self.invoke('run', self.script('''import bpy
with open('latin1.txt',encoding='latin-1') as source:assert source.read()=='café'
with open('copy.txt','w',encoding='latin-1') as output:output.write('café')
with open('latin1.txt','rb') as source:assert source.read()==b'caf\\xe9'
bpy.ops.mesh.primitive_cube_add()
'''))
        self.assertEqual((self.path / 'copy.txt').read_bytes(), b'caf\xe9')
        before = (self.path / 'scene.hb').read_bytes()
        for expression in ("open('latin1.txt').read()",
                           "open('latin1.txt',encoding='ascii').read()"):
            with self.subTest(expression=expression):
                result = self.invoke('run', self.script(
                    'import bpy\nbpy.context.object.location.x=9\n' + expression), ok=False)
                self.assertEqual(json.loads(result.stdout)['error']['code'], 'SCRIPT_ERROR')
                self.assertEqual((self.path / 'scene.hb').read_bytes(), before)

    def test_utf8_bom_scripts_match_plain_scripts_and_preserve_source(self):
        # Only the source signature is consumed; BOMs inside literals/data stay intact.
        (self.path / 'data.txt').write_bytes(codecs.BOM_UTF8 + b'data')
        body = ("import bpy\nassert open('data.txt').read()=='\ufeffdata'\n"
                "bpy.ops.mesh.primitive_cube_add(location=(1,2,3))\n"
                "bpy.context.object.name=%r\n" % TEXT)
        for index, source in enumerate((body, '# coding: utf-8\n' + body,
                                       ('#!/usr/bin/env python3\n# coding: utf-8\n' + body)
                                       .replace('\n', '\r\n'))):
            with self.subTest(index=index):
                records = []
                exports = []
                for kind, prefix in (('plain', b''), ('bom', codecs.BOM_UTF8)):
                    stem = kind + str(index)
                    raw = prefix + source.encode('utf-8')
                    script = self.path / (stem + '.py')
                    script.write_bytes(raw)
                    self.assertTrue(json.loads(self.invoke('check', script).stdout)['ok'])
                    result = json.loads(self.invoke('run', script, '--scene', stem + '.hb',
                                                    '--out', stem + '.glb').stdout)
                    self.assertEqual(result['objects']['created'], [TEXT])
                    record = test_cli.revision(self.path / (stem + '.hb'))
                    self.assertEqual(record['script'], raw.decode('utf-8'))
                    records.append(record['scene'])
                    exports.append((self.path / (stem + '.glb')).read_bytes())
                self.assertEqual(records[0], records[1])
                self.assertEqual(exports[0], exports[1])

    def test_invalid_source_boms_and_encodings_leave_scene_unchanged(self):
        self.invoke('run', self.script('import bpy\nbpy.ops.mesh.primitive_cube_add()'))
        before = (self.path / 'scene.hb').read_bytes()
        history = set((self.path / 'scene.hb.revisions').iterdir())
        cases = [
            (codecs.BOM_UTF8 + b'import bpy\nif:\n', 2),
            (codecs.BOM_UTF8 * 2 + b'import bpy\n', 1),
            (b'import bpy\n' + codecs.BOM_UTF8 + b'pass\n', 2),
            (codecs.BOM_UTF8 + b'# coding: latin-1\npass\n', None),
            (codecs.BOM_UTF8 + b'# coding: ascii\npass\n', None),
        ]
        for index, (raw, line) in enumerate(cases):
            with self.subTest(index=index):
                script = self.path / 'invalid.py'
                script.write_bytes(raw)
                checked = json.loads(self.invoke('check', script, ok=False).stdout)
                executed = json.loads(self.invoke('run', script, ok=False).stdout)
                self.assertEqual(checked['errors'][0]['code'], 'SYNTAX_ERROR')
                self.assertEqual(executed['error']['code'], 'SCRIPT_ERROR')
                if line is not None:
                    self.assertEqual(checked['errors'][0]['location'], f'{script}:{line}')
                    self.assertEqual(executed['error']['location'], f'{script}:{line}')
                else:
                    self.assertIn('encoding', checked['errors'][0]['message'])
                    self.assertIn('encoding', executed['error']['message'])
                self.assertEqual((self.path / 'scene.hb').read_bytes(), before)
                self.assertEqual(set((self.path / 'scene.hb.revisions').iterdir()), history)
                self.assertFalse((self.path / 'scene.hb.lock').exists())
        script.write_bytes(codecs.BOM_UTF8 + b'# invalid UTF-8: \xff\n')
        for command in ('check', 'run'):
            response = json.loads(self.invoke(command, script, ok=False).stdout)
            self.assertEqual(response['error']['code'], 'IO_ERROR')
        self.assertEqual((self.path / 'scene.hb').read_bytes(), before)
        self.assertEqual(set((self.path / 'scene.hb.revisions').iterdir()), history)

    def test_servers_accept_utf8_bom_files_and_inline_code(self):
        source = ('import bpy\nbpy.ops.mesh.primitive_cube_add(location=(1,2,3))\n'
                  'bpy.context.object.name=%r\n' % TEXT)
        script = self.path / 'bom.py'
        script.write_bytes(codecs.BOM_UTF8 + source.encode('utf-8'))
        self.invoke('run', self.script(source), '--scene', 'control.hb', '--out', 'control.glb')
        for mode in ('--jsonrpc', '--mcp'):
            with self.subTest(mode=mode):
                stem = mode[2:]
                inline = '\ufeffimport bpy\nbpy.context.object.location.x=4\n'
                operations = [('check', {'args': [str(script)]}),
                              ('run', {'args': [str(script), '--out', stem + '.glb']}),
                              ('check', {'code': inline}), ('run', {'code': inline}),
                              ('query', {'args': ['stats']})]
                messages = []
                if mode == '--mcp':
                    messages = [request(0, 'initialize', {'protocolVersion': '2025-11-25',
                                                         'clientInfo': {}, 'capabilities': {}}),
                                {'jsonrpc': '2.0', 'method': 'notifications/initialized'}]
                for identifier, (command, arguments) in enumerate(operations, 1):
                    arguments = {**arguments, 'scene': stem + '.hb'}
                    if mode == '--mcp':
                        messages.append(request(identifier, 'tools/call', {
                            'name': 'hb_' + command, 'arguments': arguments}))
                    else:
                        messages.append(request(identifier, command, arguments))
                output = self.invoke('serve', mode, messages=messages)
                replies = [json.loads(line) for line in output.stdout.splitlines()]
                for reply in replies:
                    self.assertIn('result', reply, reply)
                if mode == '--mcp':
                    replies = replies[1:]
                    for reply in replies:
                        self.assertFalse(reply['result']['isError'], reply)
                    replies = [reply['result']['structuredContent'] for reply in replies]
                else:
                    replies = [reply['result'] for reply in replies]
                self.assertTrue(all(reply['ok'] for reply in replies), replies)
                self.assertEqual(replies[-1]['result']['objects'], 1)
                record = test_cli.revision(self.path / (stem + '.hb'))
                self.assertEqual(record['script'], inline)
                self.assertEqual(record['scene']['objects'][0]['location'], [4, 2, 3])
                self.assertEqual((self.path / (stem + '.glb')).read_bytes(),
                                 (self.path / 'control.glb').read_bytes())
