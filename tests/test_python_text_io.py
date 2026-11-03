"""Embedded Python text I/O must work without the host's locale or Python settings."""
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
