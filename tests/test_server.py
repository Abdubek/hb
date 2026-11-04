"""Exercise HB's stdio protocols through the packaged executable."""
import base64
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from test_cli import HB, ROOT


def request(identifier, method, params=None):
    return {"jsonrpc": "2.0", "id": identifier, "method": method, "params": params or {}}


class Server(unittest.TestCase):
    def exchange(self, mode, messages, directory):
        process = subprocess.run(
            [str(HB), "serve", mode],
            input="".join(json.dumps(message) + "\n" for message in messages),
            text=True, capture_output=True, cwd=directory, timeout=30,
        )
        self.assertEqual(process.returncode, 0, process.stderr)
        return [json.loads(line) for line in process.stdout.splitlines()]

    def test_inline_code_preserves_existing_temp_files_and_cleans_up(self):
        for mode in ('--jsonrpc', '--mcp'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                temporary = root / 'temporary'
                temporary.mkdir()
                process = subprocess.Popen(
                    [str(HB), 'serve', mode], cwd=root,
                    env={**os.environ, 'TMPDIR': str(temporary)},
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    text=True,
                )
                # Preserve both the legacy name and an occupied new-style candidate.
                legacy = temporary / f'hb-rpc-{process.pid}.py'
                collision = temporary / f'hb-rpc-{process.pid}-0.py'
                protected = {legacy: b'existing user source\n', collision: b'occupied candidate\n'}
                for path, data in protected.items():
                    path.write_bytes(data)
                link = temporary / f'hb-rpc-{process.pid}-1.py'
                link.symlink_to(legacy)
                protected[link] = protected[legacy]
                source = '''import bpy,json,os
bpy.ops.mesh.primitive_cube_add()
json.dump({'path':__file__,'mode':os.stat(__file__).st_mode & 0o777},open('observed.json','w'))
'''
                operations = [('run', {'code': source}),
                              ('run', {'code': 'import bpy\nbpy.ops.wm.save_as_mainfile(filepath="x.blend")'}),
                              ('run', {'code': 'raise RuntimeError("intentional failure")'}),
                              ('query', {'args': ['stats']})]
                messages = []
                if mode == '--mcp':
                    messages = [request(0, 'initialize', {'protocolVersion': '2025-11-25',
                                                         'clientInfo': {}, 'capabilities': {}}),
                                {'jsonrpc': '2.0', 'method': 'notifications/initialized'}]
                for identifier, (command, arguments) in enumerate(operations, 1):
                    if mode == '--mcp':
                        messages.append(request(identifier, 'tools/call', {
                            'name': 'hb_' + command, 'arguments': arguments}))
                    else:
                        messages.append(request(identifier, command, arguments))
                try:
                    stdout, stderr = process.communicate(
                        ''.join(json.dumps(m) + '\n' for m in messages), timeout=30)
                finally:
                    if process.poll() is None:
                        process.kill()
                        process.communicate()
                self.assertEqual(process.returncode, 0, stderr)
                for path, data in protected.items():
                    self.assertTrue(path.exists(), f'Existing file removed: {path}')
                    self.assertEqual(path.read_bytes(), data)
                self.assertTrue(link.is_symlink())
                self.assertEqual(link.readlink(), legacy)
                self.assertEqual(set(temporary.iterdir()), set(protected))
                replies = [json.loads(line) for line in stdout.splitlines()]
                if mode == '--mcp':
                    replies = [reply['result']['structuredContent'] for reply in replies[1:]]
                else:
                    replies = [reply['result'] for reply in replies]
                self.assertTrue(replies[0]['ok'])
                rejected = replies[1]
                code = rejected['errors'][0]['code'] if mode == '--mcp' else rejected['error']['code']
                self.assertEqual(code, 'UNSUPPORTED_API')
                self.assertEqual(replies[2]['error']['code'], 'SCRIPT_ERROR')
                self.assertEqual(replies[-1]['result']['objects'], 1)
                observed = json.loads((root / 'observed.json').read_text())
                self.assertNotIn(Path(observed['path']), protected)
                self.assertEqual(Path(observed['path']).parent.resolve(), temporary.resolve())
                if os.name == 'posix':
                    self.assertEqual(observed['mode'], 0o600)

    def test_jsonrpc_scene_history_and_batch(self):
        with tempfile.TemporaryDirectory() as directory:
            replies = self.exchange("--jsonrpc", [
                request(1, "run", {"code": "import bpy\nbpy.ops.mesh.primitive_cube_add()"}),
                request(2, "run", {"code": "import bpy\nbpy.context.object.location.x=3"}),
                request(3, "log"),
                request(4, "undo"),
                [request(5, "query", {"args": ["stats"]}), request(6, "capabilities")],
                {"jsonrpc": "2.0", "method": "capabilities"},
            ], directory)
            self.assertEqual(len(replies), 5)
            first, second = replies[0]["result"], replies[1]["result"]
            self.assertNotEqual(first["revision"], second["revision"])
            self.assertEqual([entry["revision"] for entry in replies[2]["result"]["revisions"]],
                             [second["revision"], first["revision"]])
            self.assertEqual(replies[3]["result"]["revision"], first["revision"])
            self.assertTrue(replies[4][0]["result"]["ok"])
            self.assertEqual(replies[4][1]["result"]["name"], "hb")

    def test_mcp_run_accepts_comprehension_shadowing(self):
        source=(ROOT/'compat/golden/m3_checker_comprehensions.py').read_text()
        with tempfile.TemporaryDirectory() as directory:
            replies=self.exchange('--mcp',[
                request(1,'initialize',{'protocolVersion':'2025-11-25',
                                      'clientInfo':{},'capabilities':{}}),
                {'jsonrpc':'2.0','method':'notifications/initialized'},
                request(2,'tools/call',{'name':'hb_run','arguments':{'code':source}}),
                request(3,'tools/call',{'name':'hb_query','arguments':{'args':['stats']}}),
            ],directory)
            self.assertFalse(replies[1]['result']['isError'])
            self.assertTrue(replies[1]['result']['structuredContent']['ok'])
            self.assertEqual(replies[2]['result']['structuredContent']['result']['objects'],1)

    def test_mcp_handshake_tools_and_render_content(self):
        with tempfile.TemporaryDirectory() as directory:
            image = str(Path(directory) / "cube.png")
            replies = self.exchange("--mcp", [
                request(1, "tools/list"),
                request(2, "initialize", {"protocolVersion": "2025-11-25",
                                          "clientInfo": {"name": "test", "version": "1"},
                                          "capabilities": {}}),
                {"jsonrpc": "2.0", "method": "notifications/initialized"},
                request(3, "tools/list"),
                request(4, "tools/call", {"name": "hb_run", "arguments": {
                    "code": "import bpy\nbpy.ops.mesh.primitive_cube_add()"}}),
                request(5, "tools/call", {"name": "hb_render", "arguments": {
                    "args": ["--size", "64", "--out", image]}}),
                request(6, "tools/call", {"name": "missing_tool"}),
            ], directory)
            self.assertEqual(replies[0]["error"]["code"], -32000)
            self.assertEqual(replies[1]["result"]["serverInfo"]["name"], "hb")
            tools = {tool["name"] for tool in replies[2]["result"]["tools"]}
            self.assertTrue({"hb_run", "hb_api", "hb_review", "hb_render"} <= tools)
            self.assertFalse(replies[3]["result"]["isError"])
            rendered = replies[4]["result"]
            self.assertFalse(rendered["isError"])
            self.assertEqual(rendered["content"][1]["mimeType"], "image/png")
            self.assertEqual(base64.b64decode(rendered["content"][1]["data"]),
                             Path(image).read_bytes())
            self.assertEqual(replies[5]["error"]["code"], -32602)

    def test_jsonrpc_invalid_requests_and_parameters(self):
        with tempfile.TemporaryDirectory() as directory:
            replies = self.exchange("--jsonrpc", [
                {"jsonrpc": "1.0", "id": 1, "method": "capabilities"},
                request(2, "unknown"),
                request(3, "run", {"args": "not an array"}),
                request(4, "run", {"code": 42}),
            ], directory)
            self.assertEqual(replies[0]["error"]["code"], -32600)
            self.assertEqual(replies[1]["error"]["code"], -32601)
            for reply in replies[2:]:
                self.assertEqual(reply["error"]["data"]["code"], "INVALID_PARAMS")

    def test_mcp_render_cannot_overwrite_scene_through_absolute_path(self):
        with tempfile.TemporaryDirectory() as directory:
            replies = self.exchange('--mcp', [
                request(1, 'initialize', {'protocolVersion': '2025-11-25',
                                        'clientInfo': {}, 'capabilities': {}}),
                {'jsonrpc': '2.0', 'method': 'notifications/initialized'},
                request(2, 'tools/call', {'name': 'hb_run', 'arguments': {
                    'code': 'import bpy\nbpy.ops.mesh.primitive_cube_add()'}}),
                request(3, 'tools/call', {'name': 'hb_render', 'arguments': {
                    'args': ['--size', '32', '--out', str(Path(directory) / 'scene.hb')]}}),
                request(4, 'tools/call', {'name': 'hb_query', 'arguments': {'args': ['stats']}}),
            ], directory)
            self.assertTrue(replies[1]['result']['structuredContent']['ok'])
            rejected = replies[2]['result']
            self.assertTrue(rejected['isError'])
            self.assertEqual(rejected['structuredContent']['error']['code'], 'USAGE')
            self.assertEqual(len(rejected['content']), 1)
            self.assertEqual(replies[3]['result']['structuredContent']['result']['objects'], 1)

    def test_request_size_limit_and_recovery(self):
        limit = 16 * 1024 * 1024
        for mode, method in [("--mcp", "ping"), ("--jsonrpc", "capabilities")]:
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                valid = json.dumps(request(1, method)).encode()
                # Whitespace is valid JSON padding. Include the newline in the byte limit.
                boundary = valid + b" " * (limit - len(valid) - 1) + b"\n"
                oversized = boundary[:-1] + b" \n"
                with tempfile.TemporaryFile() as data:
                    data.write(boundary)
                    data.write(oversized)
                    # An oversized whitespace-only line must also respect the limit.
                    data.write(b" " * limit + b"\n")
                    data.write(json.dumps(request(2, method)).encode() + b"\n")
                    data.seek(0)
                    process = subprocess.run(
                        [str(HB), "serve", mode], stdin=data, capture_output=True,
                        cwd=directory, timeout=30,
                    )
                self.assertEqual(process.returncode, 0, process.stderr)
                replies = [json.loads(line) for line in process.stdout.splitlines()]
                self.assertEqual(len(replies), 4, replies)
                self.assertEqual(replies[0]["id"], 1)
                self.assertIn("result", replies[0])
                for reply in replies[1:3]:
                    self.assertIsNone(reply["id"])
                    self.assertEqual(reply["error"]["code"], -32600)
                    self.assertEqual(reply["error"]["message"], "Request exceeds 16 MB")
                self.assertEqual(replies[3]["id"], 2)
                self.assertIn("result", replies[3])


if __name__ == "__main__":
    unittest.main()
