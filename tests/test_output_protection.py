"""CLI artifact destinations must preserve the source scene and its history."""
import unittest

import test_cli


class OutputProtection(unittest.TestCase):
    setUp = test_cli.CLI.setUp
    tearDown = test_cli.CLI.tearDown
    hb = test_cli.CLI.hb
    script = test_cli.CLI.script

    def state(self, scene):
        head = self.path / scene
        history = self.path / (scene + '.revisions')
        return head.read_bytes(), {p.name: p.read_bytes() for p in history.iterdir()}

    def test_render_rejects_scene_and_history_aliases(self):
        self.hb('run', self.script('import bpy\nbpy.ops.mesh.primitive_cube_add()'))
        before = self.state('scene.hb')
        (self.path / 'sub').mkdir()
        (self.path / 'alias').symlink_to(self.path, target_is_directory=True)
        history = self.path / 'scene.hb.revisions'
        (self.path / 'history-alias').symlink_to(history, target_is_directory=True)
        snapshot = next(history.glob('*.hbr'))
        for output in (
            str(self.path / 'scene.hb'), 'sub/../scene.hb', 'alias/scene.hb',
            str(snapshot), 'scene.hb.revisions/new.png', 'history-alias/new.png',
        ):
            with self.subTest(output=output):
                result = self.hb('render', '--size', 32, '--out', output, ok=False)
                self.assertEqual(result['error']['code'], 'USAGE')
                self.assertEqual(self.state('scene.hb'), before)
        self.assertEqual(self.hb('query', 'stats')['result']['objects'], 1)
        self.hb('render', '--size', 32, '--out', 'preview.png')
        self.assertEqual((self.path / 'preview.png').read_bytes()[:8], b'\x89PNG\r\n\x1a\n')

    def test_export_and_run_preserve_scene_and_history(self):
        script = self.script('import bpy\nbpy.ops.mesh.primitive_cube_add()')
        self.hb('run', script, '--scene', 'project.glb')
        before = self.state('project.glb')
        edit = self.script('import bpy\nbpy.context.object.location.x=3', 'edit.py')
        for output in (str(self.path / 'project.glb'), 'project.glb.revisions/new.glb'):
            for operation in (('export', output), ('run', edit, '--out', output)):
                with self.subTest(operation=operation):
                    result = self.hb(*operation, '--scene', 'project.glb', ok=False)
                    self.assertEqual(result['error']['code'], 'USAGE')
                    self.assertEqual(self.state('project.glb'), before)
        self.assertEqual(self.hb('query', 'stats', '--scene', 'project.glb')['result']['objects'], 1)

    def test_obj_companion_is_checked_before_any_export_writes(self):
        script = self.script('import bpy\nbpy.ops.mesh.primitive_cube_add()')
        self.hb('run', script, '--scene', 'asset.mtl')
        before = self.state('asset.mtl')
        for operation in (('export', 'asset.obj'), ('run', script, '--out', 'asset.obj')):
            with self.subTest(operation=operation):
                result = self.hb(*operation, '--scene', 'asset.mtl', ok=False)
                self.assertEqual(result['error']['code'], 'USAGE')
                self.assertEqual(self.state('asset.mtl'), before)
                self.assertFalse((self.path / 'asset.obj').exists())


if __name__ == '__main__':
    unittest.main()
