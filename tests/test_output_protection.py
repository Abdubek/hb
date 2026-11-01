"""CLI artifact destinations must preserve the source scene and its history."""
import json
import unittest

import test_cli


TEXTURED_CUBE = '''import bpy
bpy.ops.mesh.primitive_cube_add()
material=bpy.data.materials.new('Paint');material.use_nodes=True
shader=material.node_tree.nodes['Principled BSDF']
image=bpy.data.images.new('Image',width=2,height=2,alpha=True,float_buffer=True)
image.pixels=[1,0,0,1,.25,.5,.75,.5,0,1,0,1,0,0,1,0]
texture=material.node_tree.nodes.new('ShaderNodeTexImage');texture.image=image
normal=material.node_tree.nodes.new('ShaderNodeNormalMap')
links=material.node_tree.links
links.new(texture.outputs['Color'],shader.inputs['Base Color'])
links.new(texture.outputs['Alpha'],shader.inputs['Alpha'])
links.new(texture.outputs['Color'],normal.inputs['Color'])
links.new(normal.outputs['Normal'],shader.inputs['Normal'])
bpy.context.object.data.materials.append(material)
'''


class OutputProtection(unittest.TestCase):
    setUp = test_cli.CLI.setUp
    tearDown = test_cli.CLI.tearDown
    hb = test_cli.CLI.hb
    script = test_cli.CLI.script

    def state(self, scene):
        head = self.path / scene
        history = self.path / (scene + '.revisions')
        return head.read_bytes(), {p.name: p.read_bytes() for p in history.iterdir()}

    def textured_scene(self):
        script = self.script(TEXTURED_CUBE)
        self.hb('run', script)
        reference = self.path / 'reference'
        reference.mkdir()
        self.hb('export', reference / 'asset.obj')
        maps = [line.split()[1] for line in (reference / 'asset.mtl').read_text().splitlines()
                if line.startswith(('map_Kd ', 'map_d ', 'map_Bump '))]
        self.assertEqual(len(maps), 3)
        for name in maps:
            self.assertEqual((reference / name).read_bytes()[:8], b'\x89PNG\r\n\x1a\n')
        return script, maps

    def output_files(self, directory):
        return {p.name: (('symlink', p.readlink()) if p.is_symlink() else p.read_bytes())
                for p in directory.iterdir() if not p.is_dir()}

    def test_obj_texture_companions_preserve_scene_before_any_writes(self):
        script, maps = self.textured_scene()
        edit = self.script('import bpy\nbpy.context.object.location.x=3', 'edit.py')
        for index, name in enumerate(maps):
            for command in ('export', 'run'):
                with self.subTest(texture=name, command=command):
                    directory = self.path / f'{index}-{command}'
                    directory.mkdir()
                    scene = directory / name
                    self.hb('run', script, '--scene', scene)
                    before = self.state(str(scene))
                    for output in ['asset.obj', 'asset.mtl', *maps]:
                        if output != name:
                            (directory / output).write_bytes(b'existing artifact')
                    files = self.output_files(directory)
                    # Resolve the generated companions through a parent-directory alias too.
                    alias = self.path / f'{index}-{command}-alias'
                    alias.symlink_to(directory, target_is_directory=True)
                    out = alias / 'asset.obj'
                    args = ('export', out) if command == 'export' else ('run', edit, '--out', out)
                    result = self.hb(*args, '--scene', scene, ok=False)
                    self.assertEqual(result['error']['code'], 'USAGE')
                    self.assertEqual(self.state(str(scene)), before)
                    self.assertEqual(self.output_files(directory), files)
                    self.assertEqual(self.hb('query', 'stats', '--scene', scene)['result']['objects'], 1)

    def test_obj_texture_symlinks_to_scene_and_history_are_rejected(self):
        _, maps = self.textured_scene()
        before = self.state('scene.hb')
        snapshot = next((self.path / 'scene.hb.revisions').glob('*.hbr'))
        for index, protected in enumerate((self.path / 'scene.hb', snapshot)):
            with self.subTest(protected=protected):
                directory = self.path / f'alias-{index}'
                directory.mkdir()
                # The last generated texture must be checked before earlier textures are written.
                (directory / maps[-1]).symlink_to(protected)
                files = self.output_files(directory)
                result = self.hb('export', directory / 'asset.obj', ok=False)
                self.assertEqual(result['error']['code'], 'USAGE')
                self.assertEqual(self.state('scene.hb'), before)
                self.assertEqual(self.output_files(directory), files)

    def test_deliver_texture_companions_preserve_review_and_assessment(self):
        _, maps = self.textured_scene()
        before = self.state('scene.hb')
        for protected in ('review', 'assessment', 'image'):
            with self.subTest(protected=protected):
                directory = self.path / protected
                directory.mkdir()
                review_path = directory / (maps[-1] if protected == 'review' else 'review.json')
                assessment_path = directory / (maps[-1] if protected == 'assessment' else 'assessment.json')
                review = self.hb('review', '--size', 32, '--out', review_path)['review']
                assessment = review['assessment_template']
                for check in assessment['checks']:
                    assessment['checks'][check] = {'pass': True, 'notes': 'Synthetic protocol test.'}
                assessment['acknowledged_warnings'] = {
                    issue['id']: 'Intentional test geometry.' for issue in review['diagnostics']['issues']}
                assessment_path.write_text(json.dumps(assessment))
                if protected == 'image':
                    (directory / maps[-1]).symlink_to(review['image'])
                files = self.output_files(directory)
                args = ('deliver', '--review', review_path, '--assessment', assessment_path)
                result = self.hb(*args, '--out', directory / 'asset.obj', ok=False)
                self.assertEqual(result['error']['code'], 'USAGE')
                self.assertEqual(self.state('scene.hb'), before)
                self.assertEqual(self.output_files(directory), files)
                # Successful delivery emits all companions when their directory is separate.
                delivered = directory / 'delivered'
                delivered.mkdir()
                self.hb(*args, '--out', delivered / 'asset.obj')
                for name in ['asset.obj', 'asset.mtl', *maps]:
                    self.assertEqual((delivered / name).read_bytes(),
                                     (self.path / 'reference' / name).read_bytes())
                self.assertTrue((delivered / 'asset.delivery.json').is_file())

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
