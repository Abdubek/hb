"""OS write failures during lock acquisition must not block the next writer."""
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

import test_cli
import test_server


# Isolate file-size limits and signal handling in an exec wrapper, not the test
# runner. Ignoring SIGXFSZ makes the real write return EFBIG instead of killing HB.
LIMITED = '''import os,resource,signal,sys
signal.signal(signal.SIGXFSZ,signal.SIG_IGN)
resource.setrlimit(resource.RLIMIT_FSIZE,(int(sys.argv[1]),resource.getrlimit(resource.RLIMIT_FSIZE)[1]))
os.execv(sys.argv[2],sys.argv[2:])
'''


@unittest.skipUnless(os.name == 'posix', 'Requires Unix file-size limits')
class LockIO(unittest.TestCase):
    setUp = test_cli.CLI.setUp
    tearDown = test_cli.CLI.tearDown
    hb = test_cli.CLI.hb
    script = test_cli.CLI.script

    def limited(self, *args, limit=0, messages=None):
        return subprocess.run(
            [sys.executable, '-c', LIMITED, str(limit), str(test_cli.HB), *map(str, args)],
            cwd=self.path, input=None if messages is None else ''.join(
                json.dumps(message) + '\n' for message in messages),
            capture_output=True, text=True, timeout=30)

    def test_empty_and_partial_pid_failures_allow_immediate_retry(self):
        create = self.script('import bpy\nbpy.ops.mesh.primitive_cube_add()\n', 'create.py')
        edit = self.script('import bpy\nbpy.context.object.location.x=3\n', 'edit.py')
        for limit in (0, 1):
            with self.subTest(limit=limit):
                scene = self.path / f'limit-{limit}.hb'
                self.hb('run', create, '--scene', scene)
                before = scene.read_bytes()
                history = Path(str(scene) + '.revisions')
                snapshots = {p.name: p.read_bytes() for p in history.iterdir()}
                result = self.limited('run', edit, '--scene', scene, limit=limit)
                self.assertEqual(result.returncode, 1, result.stderr + result.stdout)
                self.assertEqual(json.loads(result.stdout)['error']['code'], 'IO_ERROR')
                self.assertFalse(Path(str(scene) + '.lock').exists())
                self.assertEqual(scene.read_bytes(), before)
                self.assertEqual({p.name: p.read_bytes() for p in history.iterdir()}, snapshots)
                self.hb('run', edit, '--scene', scene, '--out', 'retry.glb')
                self.assertNotEqual(scene.read_bytes(), before)
                self.assertEqual(test_cli.revision(scene)['scene']['objects'][0]['location'], [3, 0, 0])
                self.assertEqual((self.path / 'retry.glb').read_bytes()[:4], b'glTF')

    def test_existing_lock_files_and_symlinks_are_preserved(self):
        source = self.script('import bpy\nbpy.ops.mesh.primitive_cube_add()\n')
        owner = self.path / 'owner'
        owner.write_text(str(os.getpid()))
        missing = self.path / 'missing'
        for kind in ('file', 'symlink', 'dangling'):
            with self.subTest(kind=kind):
                scene = self.path / (kind + '.hb')
                lock = Path(str(scene) + '.lock')
                if kind == 'file':lock.write_bytes(owner.read_bytes())
                else:lock.symlink_to(owner if kind == 'symlink' else missing)
                result = self.limited('run', source, '--scene', scene)
                self.assertEqual(result.returncode, 1, result.stderr + result.stdout)
                self.assertEqual(json.loads(result.stdout)['error']['code'], 'SCENE_BUSY')
                self.assertTrue(os.path.lexists(lock))
                if kind == 'file':self.assertEqual(lock.read_bytes(), owner.read_bytes())
                else:self.assertEqual(lock.readlink(), owner if kind == 'symlink' else missing)
                self.assertEqual(owner.read_text(), str(os.getpid()))
                self.assertFalse(missing.exists())
                self.assertFalse(scene.exists())

    def test_servers_keep_io_errors_and_queries_work_until_retry(self):
        create = self.script('import bpy\nbpy.ops.mesh.primitive_cube_add()\n', 'create.py')
        edit = self.script('import bpy\nbpy.context.object.location.x=3\n', 'edit.py')
        for mode in ('--jsonrpc', '--mcp'):
            with self.subTest(mode=mode):
                scene = self.path / (mode[2:] + '.hb')
                initial = self.hb('run', create, '--scene', scene)
                before = scene.read_bytes()
                messages = []
                if mode == '--mcp':
                    messages = [test_server.request(0, 'initialize', {
                        'protocolVersion': '2025-11-25', 'clientInfo': {}, 'capabilities': {}}),
                        {'jsonrpc': '2.0', 'method': 'notifications/initialized'}]
                    for identifier in (1, 2):
                        messages.append(test_server.request(identifier, 'tools/call', {
                            'name': 'hb_run', 'arguments': {'scene': str(scene), 'args': [str(edit)]}}))
                    messages.append(test_server.request(3, 'tools/call', {
                        'name': 'hb_query', 'arguments': {'scene': str(scene), 'args': ['stats']}}))
                else:
                    messages = [test_server.request(i, 'run', {'scene': str(scene), 'args': [str(edit)]})
                                for i in (1, 2)]
                    messages.append(test_server.request(3, 'query', {'scene': str(scene), 'args': ['stats']}))
                result = self.limited('serve', mode, messages=messages)
                self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
                replies = [json.loads(line) for line in result.stdout.splitlines()]
                if mode == '--mcp':
                    values = [reply['result']['structuredContent'] for reply in replies[1:]]
                    errors = [value['error']['code'] for value in values[:2]]
                    query = values[2]
                else:
                    errors = [reply['error']['data']['code'] for reply in replies[:2]]
                    query = replies[2]['result']
                self.assertEqual(errors, ['IO_ERROR', 'IO_ERROR'])
                self.assertEqual(query['revision'], initial['revision'])
                self.assertEqual(query['result']['objects'], 1)
                self.assertEqual(scene.read_bytes(), before)
                self.assertFalse(Path(str(scene) + '.lock').exists())
                self.hb('run', edit, '--scene', scene)
