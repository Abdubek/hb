import unittest,json,zlib
import test_cli
from normalize import revision
from primitive_extensions_check import compare

class PrimitiveExtensions(unittest.TestCase):
    setUp=test_cli.CLI.setUp;tearDown=test_cli.CLI.tearDown;hb=test_cli.CLI.hb;script=test_cli.CLI.script
    def fixture(self,name):
        return json.loads(zlib.decompress((test_cli.ROOT/('compat/fixtures/primitive-extensions-'+name+'.json.zlib')).read_bytes()))

    def test_construction_geometry_uv_and_edit_references(self):
        script=test_cli.ROOT/'compat/primitive_extensions_probe.py'
        self.hb('check',script);self.hb('run',script)
        passed,failures=compare(self.fixture('combined-construction-reference'),revision(self.path/'scene.hb')['scene'])
        self.assertFalse(failures,failures);self.assertEqual(len(passed),100)

    def test_finite_degenerate_topology_references(self):
        def cycle(face):return min(tuple(face[i:]+face[:i]) for i in range(len(face)))
        for name in ('degenerate','zero-sphere'):
            script=test_cli.ROOT/('compat/primitive_extensions_'+name.replace('-','_')+'_probe.py')
            self.hb('check',script);self.hb('run',script,'--scene',name+'.hb')
            refs=self.fixture(name+'-reference');scene=revision(self.path/(name+'.hb'))['scene'];meshes={m['id']:m for m in scene['meshes']}
            self.assertEqual(len(scene['objects']),len(refs))
            for obj in scene['objects']:
                expected=refs[obj['name']];mesh=meshes[obj['data']['id']]
                self.assertEqual(len(mesh['vertices']),len(expected['vertices']))
                self.assertTrue(all(abs(a-b)<=1e-5 for av,bv in zip(mesh['vertices'],expected['vertices']) for a,b in zip(av,bv)))
                self.assertEqual(sorted(cycle(f) for f in mesh['faces']),sorted(cycle(f) for f in expected['faces']))
                self.assertEqual(sorted(tuple(sorted(e)) for e in mesh['edges']),sorted(tuple(sorted(e)) for e in expected['edges']))
                if name=='degenerate':
                    actual=mesh['uv_layers'][mesh['active_uv']]['data'] if mesh['uv_layers'] else []
                    self.assertEqual(len(actual),len(expected['uv']))
                    self.assertTrue(all(abs(a-b)<=1e-5 for av,bv in zip(actual,expected['uv']) for a,b in zip(av,bv)))

    def test_cursor_alignment_and_edit_boundaries(self):
        script=test_cli.ROOT/'compat/primitive_extensions_alignment_probe.py'
        self.hb('check',script);self.hb('run',script)
        before=(self.path/'scene.hb').read_bytes()
        for code in (
            "bpy.ops.mesh.primitive_cube_add(enter_editmode=True)",
            "bpy.ops.mesh.primitive_cube_add(enter_editmode=True);bpy.ops.object.transform_apply()",
            "bpy.ops.object.select_all(action='SELECT');bpy.ops.object.mode_set(mode='EDIT')",
            "bpy.ops.mesh.primitive_cube_add(align='VIEW')",
            "bpy.ops.mesh.primitive_circle_add(radius=0)",
            "bpy.ops.mesh.primitive_uv_sphere_add(radius=0)",
            "bpy.ops.mesh.primitive_cone_add(scale=(-1,1,1))",
            "bpy.ops.mesh.primitive_cylinder_add(scale=(-1,1,1))",
        ):
            result=self.hb('run',self.script('import bpy\n'+code),ok=False)
            self.assertEqual(result['error']['code'],'UNSUPPORTED_API')
            self.assertEqual((self.path/'scene.hb').read_bytes(),before)
        self.hb('run',self.script("import bpy\nassert tuple(bpy.context.scene.cursor.location)==(0,0,0)\nassert bpy.context.mode=='OBJECT'"),'--scene','context.hb')

    def test_editmode_toggle_matches_explicit_mode_geometry(self):
        source=(test_cli.ROOT/'compat/golden/m3_editmode_toggle.py').read_text()
        script=self.script(source)
        self.hb('check',script)
        self.hb('run',script,'--scene','toggle.hb','--out','toggle.glb')
        explicit=source
        for mode in ('EDIT','OBJECT','EDIT','OBJECT'):
            explicit=explicit.replace('bpy.ops.object.editmode_toggle()',
                                      "bpy.ops.object.mode_set(mode='"+mode+"')",1)
        self.hb('run',self.script(explicit,'explicit.py'),
                '--scene','explicit.hb','--out','explicit.glb')
        self.assertEqual((self.path/'toggle.glb').read_bytes(),
                         (self.path/'explicit.glb').read_bytes())

    def test_editmode_toggle_invalid_contexts_and_rollback(self):
        self.hb('run',self.script('''import bpy
try:bpy.ops.object.editmode_toggle()
except RuntimeError:pass
else:raise AssertionError('Missing active mesh accepted')
assert bpy.context.mode=='OBJECT'
bpy.ops.object.camera_add()
try:bpy.ops.object.editmode_toggle()
except RuntimeError:pass
else:raise AssertionError('Camera edit mode accepted')
assert bpy.context.mode=='OBJECT'
bpy.ops.mesh.primitive_cube_add()
bpy.ops.object.select_all(action='SELECT')
try:bpy.ops.object.editmode_toggle()
except Exception as error:assert 'Only one selected mesh' in str(error)
else:raise AssertionError('Multi-object edit mode accepted')
assert bpy.context.mode=='OBJECT'
'''))
        before=(self.path/'scene.hb').read_bytes()
        invalid=(
            "bpy.ops.object.editmode_toggle()",
            "bpy.ops.object.select_all(action='DESELECT');bpy.context.object.select_set(True);bpy.ops.object.editmode_toggle()",
            "bpy.ops.object.editmode_toggle(mode='EDIT')",
            "bpy.ops.object.editmode_toggle('EXEC_DEFAULT')",
        )
        for call in invalid:
            with self.subTest(call=call):
                self.hb('run',self.script('import bpy\n'+call),ok=False)
                self.assertEqual((self.path/'scene.hb').read_bytes(),before)
        for call in invalid[2:]:
            errors=self.hb('check',self.script('import bpy\n'+call),ok=False)['errors']
            self.assertTrue(any('editmode_toggle(' in error['message'] for error in errors),errors)
